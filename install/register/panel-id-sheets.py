#!/usr/bin/env python3
"""
panel-id-sheets.py

Appends a new panel registration row to the SevenCourts Devices Google Spreadsheet.

Usage:
    python3 panel-id-sheets.py <PANEL_ID> <ASSEMBLY_DATE>

Example:
    python3 panel-id-sheets.py A1B2C3D4 2026-03-26

Requires:
    pip3 install gspread

Credentials:
    Place your Google service account JSON key at:
    install/google-credentials.json
    and share the spreadsheet with the service account email (Editor access).
"""

import sys
import os
from datetime import date

try:
    import gspread
    from gspread.exceptions import WorksheetNotFound, SpreadsheetNotFound
except ImportError:
    print("ERROR: gspread not installed. Run: pip3 install gspread", file=sys.stderr)
    sys.exit(1)

# ─── Configuration ────────────────────────────────────────────────────────────

SPREADSHEET_ID = "10Z8tR_vX-hWsxYZuYaRmEjbCB9eWyRcdgMDHE83mh2A"
WORKSHEET_NAME = "Devices"

# Column header names (must match the spreadsheet exactly)
COL_PANEL_ID        = "Hostname\n(Panel ID)"
COL_ASSEMBLY_DATE   = "Assembly Date"
COL_CURRENT_LOCATION = "Current\nLocation"

# Columns C through W are copied from the previous row on new registration,
# then D:W are cleared, and "Current Location" is set to the default below.
DEFAULT_LOCATION = "Stuttgart, DE"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, "google-credentials.json")

# ─── Sheets helpers ───────────────────────────────────────────────────────────

def open_worksheet():
    gc = gspread.service_account(filename=CREDENTIALS_FILE)
    try:
        sh = gc.open_by_key(SPREADSHEET_ID)
    except SpreadsheetNotFound:
        print(f"ERROR: Spreadsheet not found: {SPREADSHEET_ID}", file=sys.stderr)
        print("Make sure the spreadsheet is shared with the service account email.", file=sys.stderr)
        sys.exit(1)
    try:
        return sh.worksheet(WORKSHEET_NAME)
    except WorksheetNotFound:
        print(f"ERROR: Worksheet '{WORKSHEET_NAME}' not found in spreadsheet.", file=sys.stderr)
        sys.exit(1)


def find_column(ws, header_name):
    """Return the 1-based column index for the given header name."""
    headers = ws.row_values(1)
    try:
        return headers.index(header_name) + 1
    except ValueError:
        print(f"ERROR: Column '{header_name}' not found in row 1 of '{WORKSHEET_NAME}'.", file=sys.stderr)
        print(f"  Found columns: {headers}", file=sys.stderr)
        sys.exit(1)


def next_append_row(ws):
    """Return the row number after the last row with any data (safe append, never fills gaps)."""
    all_values = ws.get_all_values()
    return len(all_values) + 1


def register_panel(panel_id, assembly_date):
    ws = open_worksheet()

    col_panel_id      = find_column(ws, COL_PANEL_ID)
    col_assembly_date = find_column(ws, COL_ASSEMBLY_DATE)

    # Check if this panel ID is already registered
    existing = ws.col_values(col_panel_id)
    if panel_id in existing:
        row = existing.index(panel_id) + 1
        print(f"WARNING: Panel ID '{panel_id}' already registered at row {row}. Skipping.", file=sys.stderr)
        return

    row = next_append_row(ws)
    prev_row = row - 1

    # Copy columns C:W from previous row using CopyPaste API
    # (preserves data validation / checkboxes, formatting, and formulas)
    col_c = 3   # Column C (1-indexed)
    col_w = 23  # Column W (1-indexed)
    sheet_id = ws.id
    sh = ws.spreadsheet
    sh.batch_update({"requests": [{
        "copyPaste": {
            "source": {
                "sheetId": sheet_id,
                "startRowIndex": prev_row - 1,
                "endRowIndex": prev_row,
                "startColumnIndex": col_c - 1,
                "endColumnIndex": col_w,
            },
            "destination": {
                "sheetId": sheet_id,
                "startRowIndex": row - 1,
                "endRowIndex": row,
                "startColumnIndex": col_c - 1,
                "endColumnIndex": col_w,
            },
            "pasteType": "PASTE_NORMAL",
        }
    }]})

    # Clear D:W values (checkboxes reset to unchecked, text cells cleared)
    # Data validation is preserved from the copy above
    col_d = 4
    prev_values = ws.row_values(prev_row)
    prev_values += [''] * (col_w - len(prev_values))
    d_w_prev = prev_values[col_d - 1:col_w]
    reset_values = [
        False if v.upper() in ('TRUE', 'FALSE') else ''
        for v in d_w_prev
    ]
    from gspread.utils import rowcol_to_a1
    range_start_d = rowcol_to_a1(row, col_d)
    range_end = rowcol_to_a1(row, col_w)
    ws.update(values=[reset_values], range_name=f"{range_start_d}:{range_end}")

    # Set Panel ID, Assembly Date, and Current Location
    ws.update_cell(row, col_panel_id, panel_id)
    ws.update_cell(row, col_assembly_date, assembly_date)
    col_location = find_column(ws, COL_CURRENT_LOCATION)
    ws.update_cell(row, col_location, DEFAULT_LOCATION)

    print(f"Registered panel '{panel_id}' in row {row}.")


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <PANEL_ID> <ASSEMBLY_DATE>", file=sys.stderr)
        sys.exit(1)

    panel_id      = sys.argv[1]
    assembly_date = sys.argv[2]

    if not panel_id:
        print("ERROR: PANEL_ID must not be empty.", file=sys.stderr)
        sys.exit(1)

    register_panel(panel_id, assembly_date)
