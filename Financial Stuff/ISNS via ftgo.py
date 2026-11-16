import time
from datetime import datetime, timedelta

import ftgo
import xlwings as xw

# --- edit these ---
WORKBOOK = r"C:\Users\jonny\OneDrive\Desktop\Money Sheet.xlsm"
SHEET = "Queries"
CELLS = {#fund: location
        "GB00BYN5DR75": "D16", 
        "GB00B4MGHC41": "E16",}
MAX_WRITE_ATTEMPTS = 5      # tries at writing to Excel
WAIT_SECONDS = 30           # pause between write attempts
# ------------------


def get_latest_price(isin):
    end = datetime.now()
    start = end - timedelta(days=7)
    xid = ftgo.get_xid(isin)
    df = ftgo.get_historical_prices(xid, start.strftime("%d%m%Y"), end.strftime("%d%m%Y"))
    return float(df.iloc[-1]["close"])


def write_to_excel(values):
    wb = xw.Book(WORKBOOK)  # attaches if already open, otherwise opens it
    ws = wb.sheets[SHEET]
    for isin, cell in CELLS.items():
        ws[cell].value = values[isin]
    wb.save()


# 1) Fetch every price ONCE (the only FT calls this script makes)
values = {}
for isin in CELLS:
    try:
        values[isin] = get_latest_price(isin)
    except Exception as e:
        values[isin] = f"FAILED: {e}"  # visible failure instead of a stale price


# 2) Write to Excel, retrying the write only (no new FT calls)
for attempt in range(1, MAX_WRITE_ATTEMPTS + 1):
    try:
        write_to_excel(values)
        break
    except Exception as e:
        if attempt < MAX_WRITE_ATTEMPTS:
            time.sleep(WAIT_SECONDS)
        else:
            break