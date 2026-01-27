#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urlparse


DEFAULT_CREDS_PATH = Path("Work/00_Inbox/Private/google-service-account.json")


@dataclass(frozen=True)
class SheetRef:
    spreadsheet_id: str
    gid: int | None


def parse_sheet_ref(sheet_url_or_id: str, gid: int | None) -> SheetRef:
    value = sheet_url_or_id.strip()
    if not value:
        raise ValueError("Empty sheet url/id.")

    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        match = re.search(r"/spreadsheets/d/([^/]+)/", parsed.path)
        if not match:
            raise ValueError("Could not extract spreadsheet id from URL.")
        spreadsheet_id = match.group(1)

        qs = parse_qs(parsed.query)
        url_gid = None
        if "gid" in qs and qs["gid"]:
            try:
                url_gid = int(qs["gid"][0])
            except ValueError:
                url_gid = None

        return SheetRef(spreadsheet_id=spreadsheet_id, gid=gid if gid is not None else url_gid)

    return SheetRef(spreadsheet_id=value, gid=gid)


def load_creds_path(explicit: str | None) -> Path:
    env_path = os.getenv("GSHEETS_SERVICE_ACCOUNT_JSON")
    candidate = explicit or env_path
    if candidate:
        return Path(candidate)
    return DEFAULT_CREDS_PATH


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch data from Google Sheets using a service account (read-only by default).")
    parser.add_argument("--creds", help="Path to service account json (default: env GSHEETS_SERVICE_ACCOUNT_JSON or Work/00_Inbox/Private/google-service-account.json).")
    parser.add_argument("--sheet-url", required=True, help="Google Sheets URL or spreadsheet id.")
    parser.add_argument("--gid", type=int, help="Worksheet gid (optional; can be parsed from URL).")
    parser.add_argument("--limit", type=int, default=20, help="Max rows to print (default: 20).")
    parser.add_argument("--format", choices=["json", "tsv"], default="json", help="Output format (default: json).")
    parser.add_argument("--self-test", action="store_true", help="Only parse inputs and exit (no API calls).")
    args = parser.parse_args()

    sheet_ref = parse_sheet_ref(args.sheet_url, args.gid)
    creds_path = load_creds_path(args.creds)

    if args.self_test:
        print(json.dumps({"spreadsheet_id": sheet_ref.spreadsheet_id, "gid": sheet_ref.gid, "creds_path": str(creds_path)}, ensure_ascii=False))
        return 0

    if not creds_path.exists():
        print(
            f"Credentials file not found: {creds_path}\n"
            f"Create it locally (gitignored) and paste the service account JSON.\n"
            f"Tip: set GSHEETS_SERVICE_ACCOUNT_JSON=/path/to/google-service-account.json",
            file=sys.stderr,
        )
        return 2

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ModuleNotFoundError:
        print("Missing dependencies. Run: ./scripts/setup-gsheets.sh", file=sys.stderr)
        return 2

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    credentials = Credentials.from_service_account_file(str(creds_path), scopes=scopes)
    client = gspread.authorize(credentials)

    try:
        spreadsheet = client.open_by_key(sheet_ref.spreadsheet_id)
        if sheet_ref.gid is not None:
            worksheet = spreadsheet.get_worksheet_by_id(sheet_ref.gid)
            if worksheet is None:
                raise RuntimeError(f"Worksheet with gid={sheet_ref.gid} not found.")
        else:
            worksheet = spreadsheet.sheet1

        values = worksheet.get_all_values()
    except Exception as exc:
        print(f"Failed to fetch sheet: {exc}", file=sys.stderr)
        return 1

    rows = values[: max(args.limit, 0)]

    if args.format == "tsv":
        for row in rows:
            print("\t".join(row))
        return 0

    print(json.dumps({"rows": rows, "row_count_total": len(values)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

