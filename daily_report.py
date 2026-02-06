# -*- coding: utf-8 -*-
"""
daily_report.py

Runs the analysis scripts, captures their console outputs and any Matplotlib figures,
and emails a consolidated report (text + attached images) to a configured recipient.

Usage (one-off):
    python daily_report.py

Configuration (environment variables):
- REPORT_OUTPUT_DIR: directory to place report artifacts (default: ./reports)
- SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD: SMTP credential to send email
- EMAIL_TO: recipient email (default: sangyoun.han@outlook.com)
- EMAIL_FROM: sender email (defaults to SMTP_USER)

If SMTP credentials are not provided, the script will save the report locally and
print instructions for sending it manually.
"""

import os
import sys
import runpy
import io
import traceback
from datetime import datetime
from pathlib import Path
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from email.mime.base import MIMEBase
from email import encoders
import matplotlib
# Use non-interactive backend so show() doesn't block and figures can be saved
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPTS = [
    "mkt_index.py",
    "trading_strategy_aapl.py",
    "trading_strategy_tsla.py",
    "schd_vs_copper_gold.py",
]

REPORT_OUTPUT_DIR = Path(os.environ.get("REPORT_OUTPUT_DIR", "reports"))
EMAIL_TO = os.environ.get("EMAIL_TO", "sangyoun.han@outlook.com")
EMAIL_FROM = os.environ.get("EMAIL_FROM")
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587")) if os.environ.get("SMTP_PORT") else None
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

# Create output folder
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
outdir = REPORT_OUTPUT_DIR / timestamp
outdir.mkdir(parents=True, exist_ok=True)

# Monkeypatch plt.show to save current figures to files instead of blocking
orig_show = plt.show

saved_images = []

def save_and_close(show_arg=None, prefix=None):
    """Save all open figures to files and close them.
    Files will be saved into `outdir` with names like <scriptname>_fig1.png.
    The `prefix` argument is used by the runner to name files per-script.
    """
    figs = plt.get_fignums()
    for i, num in enumerate(figs, start=1):
        fig = plt.figure(num)
        fname = outdir / f"{prefix}_fig{i}.png"
        try:
            fig.savefig(fname, bbox_inches='tight')
            saved_images.append(fname)
        except Exception:
            # best-effort saving
            pass
    plt.close('all')

# We'll run each script in a fresh globals dict but within this process.
# Redirect stdout/stderr to capture text output.
report_texts = {}

for script in SCRIPTS:
    script_path = Path(script)
    if not script_path.exists():
        report_texts[script] = f"ERROR: script not found: {script}\n"
        continue

    # prepare capture
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    sys_stdout = sys.stdout
    sys_stderr = sys.stderr
    try:
        sys.stdout = buf_out
        sys.stderr = buf_err

        # monkeypatch plt.show to save images with the script name prefix
        def _show():
            save_and_close(prefix=script_path.stem)
        plt.show = _show

        # run script
        try:
            runpy.run_path(str(script_path), run_name='__main__')
        except SystemExit:
            # some scripts may call sys.exit(); ignore to continue
            pass
        except Exception:
            # capture traceback
            traceback.print_exc(file=buf_err)

    finally:
        # restore stdout/stderr and plt.show
        sys.stdout = sys_stdout
        sys.stderr = sys_stderr
        plt.show = orig_show

    out_text = buf_out.getvalue()
    err_text = buf_err.getvalue()
    combined = "".join(["--- STDOUT ---\n", out_text, "\n--- STDERR ---\n", err_text])
    # Save combined text
    text_file = outdir / f"{script_path.stem}.txt"
    text_file.write_text(combined, encoding='utf-8')
    report_texts[script] = combined

# Compose consolidated email body
subject = f"Daily Analysis Report: {timestamp}"
body_lines = [f"Daily Analysis Report - {timestamp}", "", "Scripts executed:"]
for s in SCRIPTS:
    body_lines.append(f"- {s}")
body_lines.append("")
body_lines.append("Summary outputs:\n")
for s in SCRIPTS:
    snippet = report_texts.get(s, "(no output)")
    # include first 2000 chars of each script output
    body_lines.append(f"== {s} ==\n")
    body_lines.append(snippet[:2000])
    body_lines.append('\n')

body = "\n".join(body_lines)

# Save consolidated report text
consolidated_file = outdir / "report_summary.txt"
consolidated_file.write_text(body, encoding='utf-8')

# Prepare email
def attach_file(msg, path):
    with open(path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{path.name}"')
    msg.attach(part)

sent_mail = False
if SMTP_SERVER and SMTP_USER and SMTP_PASSWORD:
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM if EMAIL_FROM else SMTP_USER
    msg['To'] = EMAIL_TO
    msg.set_content(body)

    # Attach text files and images
    for txt in outdir.glob('*.txt'):
        with open(txt, 'rb') as f:
            data = f.read()
        msg.add_attachment(data, maintype='text', subtype='plain', filename=txt.name)
    for img in saved_images:
        with open(img, 'rb') as f:
            data = f.read()
        # guess PNG
        msg.add_attachment(data, maintype='image', subtype='png', filename=img.name)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {EMAIL_TO}")
        sent_mail = True
    except Exception as e:
        print("Failed to send email:", e)
        sent_mail = False
else:
    print("SMTP credentials not set. Skipping email send.")
    print("Report saved to:", outdir)

if not sent_mail:
    print("To enable automatic email delivery, set the following environment variables:")
    print("  SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD (and optionally EMAIL_FROM, EMAIL_TO)")

print("Done.")
