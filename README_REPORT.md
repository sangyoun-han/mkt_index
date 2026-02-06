Daily report runner

This repository includes `daily_report.py` which runs the four analysis scripts and
produces a consolidated report (stdout, stderr, and saved figures) in `reports/<timestamp>/`.

Setup

1. Create a Python virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure SMTP environment variables if you want the script to email results:

- `SMTP_SERVER` (e.g. smtp.gmail.com)
- `SMTP_PORT` (e.g. 587)
- `SMTP_USER` (your SMTP username)
- `SMTP_PASSWORD` (your SMTP password or app-specific password)
- Optional: `EMAIL_FROM`, `EMAIL_TO` (defaults to sangyoun.han@outlook.com)

Run once

```bash
python daily_report.py
```

Schedule with cron (daily at 07:00):

```cron
0 7 * * * cd /path/to/mkt_index && /path/to/mkt_index/.venv/bin/python daily_report.py >> /path/to/mkt_index/logs/daily_report.log 2>&1
```

Notes

- The script runs the following files by default:
  - `mkt_index.py`
  - `trading_strategy_aapl.py`
  - `trading_strategy_tsla.py`
  - `schd_vs_copper_gold.py`

- `daily_report.py` uses a non-interactive Matplotlib backend and monkeypatches
  `plt.show()` to save figures produced by the scripts into the `reports/` folder.

- If you prefer the script to actually send emails, provide valid SMTP credentials
  in environment variables. For some providers (Gmail, Outlook) you may need an
  app-specific password or to enable SMTP access.
