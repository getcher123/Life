from __future__ import annotations

import argparse
import base64
import json
import logging
import os
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openai import OpenAI
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFInfoNotInstalledError

logger = logging.getLogger("scripts.pdf_to_json_pipeline")


class PipelineError(Exception):
    pass


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    openai_vision_model: str
    chatgpt_instructions_path: str
    chatgpt_schema_path: str
    pdf_vision_prompt_path: str
    pdf_vision_schema_path: str
    pdf_md_prompt_path: str
    results_dir: str
    poppler_path: str | None


def _default_config_dir() -> Path:
    return Path(__file__).resolve().parent / "pdf_pipeline_config"


def get_settings() -> Settings:
    config_dir = _default_config_dir()

    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "o3"),
        openai_vision_model=os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini"),
        chatgpt_instructions_path=os.getenv(
            "CHATGPT_INSTRUCTIONS_PATH",
            str(config_dir / "chatgpt_instructions.txt"),
        ),
        chatgpt_schema_path=os.getenv(
            "CHATGPT_SCHEMA_PATH",
            str(config_dir / "chatgpt_schema.json"),
        ),
        pdf_vision_prompt_path=os.getenv(
            "PDF_VISION_PROMPT_PATH",
            str(config_dir / "pdf_vision_prompt.txt"),
        ),
        pdf_vision_schema_path=os.getenv(
            "PDF_VISION_SCHEMA_PATH",
            str(config_dir / "pdf_vision_schema.json"),
        ),
        pdf_md_prompt_path=os.getenv(
            "PDF_MD_PROMPT_PATH",
            str(config_dir / "pdf_md_prompt.txt"),
        ),
        results_dir=os.getenv("RESULTS_DIR", "data/results"),
        poppler_path=os.getenv("POPPLER_PATH"),
    )


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def file_ext(path: str | Path) -> str:
    return Path(path).suffix.lstrip(".").lower()


def safe_name(name: str) -> str:
    out = []
    for ch in name:
        if ch.isalnum() or ch in {"_", "-", "."}:
            out.append(ch)
        else:
            out.append("_")
    return "".join(out) or "_"


def _wsl_to_windows_path(path: Path) -> str:
    text = str(path)
    parts = text.split("/")
    if len(parts) >= 4 and parts[1] == "mnt" and len(parts[2]) == 1:
        drive = parts[2].upper()
        rest = "/".join(parts[3:])
        rest_win = rest.replace("/", "\\")
        return f"{drive}:\\{rest_win}"
    return text


def _maybe_windows_path(path: Path, poppler_path: str | None) -> str:
    if poppler_path and poppler_path.startswith("/mnt/"):
        return _wsl_to_windows_path(path)
    return str(path)


def _read_text(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8-sig").strip()
    except FileNotFoundError as exc:
        raise PipelineError(f"Instructions file not found: {path}") from exc
    except Exception as exc:  # noqa: BLE001
        raise PipelineError(f"Failed to read instructions: {exc}") from exc


def _read_schema(path: str) -> dict[str, Any]:
    try:
        raw = Path(path).read_text(encoding="utf-8-sig")
    except FileNotFoundError as exc:
        raise PipelineError(f"Schema file not found: {path}") from exc
    except Exception as exc:  # noqa: BLE001
        raise PipelineError(f"Failed to read schema: {exc}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PipelineError(f"Invalid schema JSON: {exc}") from exc


def _get_openai_client(api_key: str | None) -> OpenAI:
    if not api_key:
        raise PipelineError("OPENAI_API_KEY is not configured")
    return OpenAI(api_key=api_key)


def pdf_to_images(
    pdf_path: str,
    out_dir: str,
    *,
    dpi: int = 150,
    image_format: str = "png",
    poppler_path: str | None = None,
) -> list[str]:
    source = Path(pdf_path)
    if not source.exists() or not source.is_file():
        raise PipelineError(f"PDF not found: {pdf_path}")

    fmt = image_format.lower()
    if fmt == "jpg":
        fmt = "jpeg"
    if fmt not in {"png", "jpeg"}:
        raise PipelineError(f"Unsupported image format: {image_format}")

    ensure_dir(out_dir)

    poppler_input = _maybe_windows_path(source, poppler_path)

    try:
        images = convert_from_path(poppler_input, dpi=dpi, fmt=fmt, poppler_path=poppler_path)
    except PDFInfoNotInstalledError as exc:
        raise PipelineError(
            "Poppler is required for PDF rasterization. Install Poppler and set POPPLER_PATH."
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise PipelineError(f"Failed to convert PDF to images: {exc}") from exc

    if not images:
        raise PipelineError("PDF rendered zero pages")

    base = safe_name(source.stem or "page")
    saved_paths: list[str] = []
    out_dir_path = Path(out_dir)

    for idx, image in enumerate(images, start=1):
        page_name = f"{base}_p{idx:04d}.{fmt}"
        target = out_dir_path / page_name
        try:
            save_format = "JPEG" if fmt == "jpeg" else fmt.upper()
            image.save(str(target), format=save_format)
        finally:
            image.close()
        saved_paths.append(str(target))

    return saved_paths


def analyze_page_image(
    image_path: str,
    *,
    prompt_path: str,
    schema_path: str,
    model: str,
) -> dict[str, Any]:
    image_file = Path(image_path)
    if not image_file.exists() or not image_file.is_file():
        raise PipelineError(f"Image not found: {image_path}")

    suffix = image_file.suffix.lstrip(".").lower()
    if suffix == "jpg":
        suffix = "jpeg"
    mime = {
        "png": "image/png",
        "jpeg": "image/jpeg",
    }.get(suffix)
    if not mime:
        raise PipelineError(f"Unsupported image format: {image_file.suffix}")

    prompt = _read_text(prompt_path)
    schema = _read_schema(schema_path)

    tool_spec = {
        "type": "function",
        "function": {
            "name": "emit_page",
            "description": "Return page data strictly by schema.",
            "strict": True,
            "parameters": schema,
        },
    }

    try:
        data = image_file.read_bytes()
    except Exception as exc:  # noqa: BLE001
        raise PipelineError(f"Failed to read image: {exc}") from exc

    encoded = base64.b64encode(data).decode("ascii")
    settings = get_settings()
    client = _get_openai_client(settings.openai_api_key)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this page and return JSON via emit_page."},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}},
                    ],
                },
            ],
            tools=[tool_spec],
            tool_choice={"type": "function", "function": {"name": "emit_page"}},
        )
    except Exception as exc:  # noqa: BLE001
        raise PipelineError(f"OpenAI vision request failed: {exc}") from exc

    try:
        message = response.choices[0].message
        tool_call = message.tool_calls[0]
        arguments = tool_call.function.arguments
    except Exception as exc:  # noqa: BLE001
        raise PipelineError(f"Malformed OpenAI response: {exc}") from exc

    try:
        parsed = json.loads(arguments)
    except json.JSONDecodeError as exc:  # noqa: BLE001
        raise PipelineError(f"OpenAI vision produced invalid JSON envelope: {exc}: {arguments[:200]}") from exc

    page_payload: dict[str, Any] | None = None
    if isinstance(parsed, dict):
        if "result" in parsed and isinstance(parsed["result"], str):
            result_text = parsed["result"]
            if not result_text.strip():
                raise PipelineError("OpenAI vision payload missing result string")
            try:
                page_payload = json.loads(result_text)
            except json.JSONDecodeError as exc:
                raise PipelineError(f"OpenAI vision produced invalid JSON: {exc}: {result_text[:200]}") from exc
        else:
            page_payload = parsed
    elif isinstance(parsed, str):
        try:
            page_payload = json.loads(parsed)
        except json.JSONDecodeError as exc:
            raise PipelineError(f"OpenAI vision produced invalid JSON: {exc}: {parsed[:200]}") from exc
    else:
        raise PipelineError("OpenAI vision returned unsupported payload format")

    return page_payload


def render_page_markdown(
    image_path: str,
    *,
    prompt_path: str,
    model: str,
) -> str:
    image_file = Path(image_path)
    if not image_file.exists() or not image_file.is_file():
        raise PipelineError(f"Image not found: {image_path}")

    suffix = image_file.suffix.lstrip(".").lower()
    if suffix == "jpg":
        suffix = "jpeg"
    mime = {
        "png": "image/png",
        "jpeg": "image/jpeg",
    }.get(suffix)
    if not mime:
        raise PipelineError(f"Unsupported image format: {image_file.suffix}")

    prompt = _read_text(prompt_path)
    settings = get_settings()
    client = _get_openai_client(settings.openai_api_key)

    try:
        data = image_file.read_bytes()
    except Exception as exc:  # noqa: BLE001
        raise PipelineError(f"Failed to read image: {exc}") from exc

    encoded = base64.b64encode(data).decode("ascii")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Return Markdown for this page only."},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}},
                    ],
                },
            ],
            temperature=0,
        )
    except Exception as exc:  # noqa: BLE001
        raise PipelineError(f"OpenAI markdown request failed: {exc}") from exc

    try:
        content = response.choices[0].message.content
    except Exception as exc:  # noqa: BLE001
        raise PipelineError(f"Malformed OpenAI markdown response: {exc}") from exc

    return (content or "").strip()


def _write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def run_pipeline(
    input_pdf: Path,
    *,
    results_dir: Path,
    dpi: int | None = None,
    image_format: str | None = None,
    poppler_path: str | None = None,
    prompt_path: str | None = None,
    schema_path: str | None = None,
    save_pages: bool = False,
    emit_md: bool = False,
    emit_text: bool = False,
    md_prompt_path: str | None = None,
) -> Path:
    settings = get_settings()

    if file_ext(input_pdf) != "pdf":
        raise PipelineError(f"Input must be a PDF: {input_pdf}")

    dpi_final = dpi if dpi is not None else 150
    image_format_final = (image_format or "png").lower()

    poppler_final = poppler_path or settings.poppler_path
    pages_dir = results_dir / "pdf_pages"
    ensure_dir(pages_dir)

    start_ts = time.perf_counter()
    logger.info("pipeline.start", extra={"pdf": str(input_pdf), "output_dir": str(results_dir)})

    page_images = pdf_to_images(
        str(input_pdf),
        str(pages_dir),
        dpi=dpi_final,
        image_format=image_format_final,
        poppler_path=poppler_final,
    )

    prompt_final = prompt_path or settings.pdf_vision_prompt_path
    schema_final = schema_path or settings.pdf_vision_schema_path
    vision_model = settings.openai_vision_model

    page_payloads: list[dict[str, Any]] = []
    out_dir = results_dir
    ensure_dir(out_dir)

    for idx, image_path in enumerate(page_images, start=1):
        page_data = analyze_page_image(
            image_path,
            prompt_path=prompt_final,
            schema_path=schema_final,
            model=vision_model,
        )
        if isinstance(page_data, dict) and "page_index" not in page_data:
            page_data["page_index"] = idx
        page_payloads.append(page_data)

        if save_pages:
            _write_json(out_dir / f"pdf_page_{idx:04d}.json", page_data)

    combined_path = out_dir / "pdf_pages_combined.json"
    _write_json(combined_path, page_payloads)

    if emit_text:
        lines: list[str] = []
        for idx, page in enumerate(page_payloads, start=1):
            lines.append(f"=== Page {idx} ===")
            lines.extend(page.get("raw_lines", []))
            lines.append("")
        text_payload = "\n".join(lines).rstrip() + "\n"
        _write_text(out_dir / "pdf_pages_combined.txt", text_payload)

    if emit_md:
        md_prompt_final = md_prompt_path or settings.pdf_md_prompt_path
        md_model_final = vision_model
        md_pages: list[str] = []
        for idx, image_path in enumerate(page_images, start=1):
            page_md = render_page_markdown(
                image_path,
                prompt_path=md_prompt_final,
                model=md_model_final,
            )
            if page_md:
                md_pages.append(f"## Page {idx}\n\n{page_md}\n")
            else:
                md_pages.append(f"## Page {idx}\n\n")
        _write_text(out_dir / "pdf_pages_combined.md", "\n".join(md_pages).rstrip() + "\n")

    elapsed_ms = int((time.perf_counter() - start_ts) * 1000)
    logger.info("pipeline.done", extra={"elapsed_ms": elapsed_ms, "output": str(combined_path)})
    return combined_path


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PDF -> JSON pipeline (vision only)")
    parser.add_argument("-i", "--input", required=True, help="Path to PDF file")
    parser.add_argument("-o", "--output", help="Override output JSON path")
    parser.add_argument("--results-dir", help="Subfolder inside PDF directory (default: <pdf>_results)")
    parser.add_argument("--request-id", help="Optional subfolder name inside results dir")
    parser.add_argument("--dpi", type=int, help="Override PDF raster DPI")
    parser.add_argument("--image-format", help="Override image format (png/jpeg)")
    parser.add_argument("--poppler-path", help="Override POPPLER_PATH")
    parser.add_argument("--prompt-path", help="Override vision prompt path")
    parser.add_argument("--schema-path", help="Override vision schema path")
    parser.add_argument("--emit-text", action="store_true", help="Write plain text output")
    parser.add_argument("--emit-md", action="store_true", help="Write Markdown output")
    parser.add_argument("--md-prompt-path", help="Override markdown prompt path")
    parser.add_argument("--save-pages", action="store_true", help="Save per-page JSON files")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser


def _resolve_results_dir(input_pdf: Path, results_dir: str | None, request_id: str | None) -> Path:
    base_dir = input_pdf.parent
    if results_dir:
        candidate = Path(results_dir)
        if not candidate.is_absolute():
            candidate = base_dir / candidate
        base_resolved = base_dir.resolve()
        candidate_resolved = candidate.resolve()
        if candidate_resolved != base_resolved and base_resolved not in candidate_resolved.parents:
            raise PipelineError("results-dir must be inside the PDF directory")
        root = candidate
    else:
        root = base_dir / f"{input_pdf.stem}_results"

    if request_id:
        return root / request_id
    return root


def main() -> int:
    args = build_arg_parser().parse_args()
    logging.basicConfig(level=args.log_level.upper(), format="%(levelname)s:%(name)s:%(message)s")

    input_pdf = Path(args.input).expanduser()
    if not input_pdf.exists():
        print(f"Input PDF not found: {input_pdf}", file=sys.stderr)
        return 2

    request_id = args.request_id
    try:
        results_dir = _resolve_results_dir(input_pdf, args.results_dir, request_id)
    except PipelineError as exc:
        print(f"Invalid results-dir: {exc}", file=sys.stderr)
        return 2

    try:
        output_path = run_pipeline(
            input_pdf,
            results_dir=results_dir,
            dpi=args.dpi,
            image_format=args.image_format,
            poppler_path=args.poppler_path,
            prompt_path=args.prompt_path,
            schema_path=args.schema_path,
            save_pages=args.save_pages,
            emit_md=args.emit_md,
            emit_text=args.emit_text,
            md_prompt_path=args.md_prompt_path,
        )
    except PipelineError as exc:
        print(f"Pipeline failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Pipeline crashed: {exc}", file=sys.stderr)
        return 1

    if args.output:
        target = Path(args.output)
        ensure_dir(target.parent)
        target.write_text(output_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Saved: {target}")
    else:
        print(f"Saved: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
