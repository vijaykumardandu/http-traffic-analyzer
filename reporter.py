# ─────────────────────────────────────────────
# reports/reporter.py
# Prints analysis results to terminal + saves HTML report
# ─────────────────────────────────────────────

import os
import json
from datetime import datetime
from colorama import Fore, Style, init
from tabulate import tabulate

init(autoreset=True)


def print_single_analysis(record: dict):
    """Pretty-prints the full analysis of a single URL to the terminal."""

    url = record["request"]["url"]
    print(f"\n{Fore.CYAN}{'═'*60}")
    print(f"  HTTP TRAFFIC ANALYSIS")
    print(f"  {url[:55]}")
    print(f"{'═'*60}{Style.RESET_ALL}")

    # Error short-circuit
    if record["error"]:
        print(f"\n  {Fore.RED}✗ ERROR: {record['error']}{Style.RESET_ALL}\n")
        return

    r = record["response"]
    t = record["timing"]
    s = record["security"]

    # Status
    status_color = Fore.GREEN if r["status_code"] == 200 else Fore.YELLOW if r["status_code"] < 500 else Fore.RED
    print(f"\n  {'Status':<22} {status_color}{r['status_code']} {r['status_text']}{Style.RESET_ALL}")
    print(f"  {'Content-Type':<22} {r['content_type']}")
    print(f"  {'Body Size':<22} {r['body_size_kb']} KB ({r['body_size_bytes']} bytes)")

    # Timing
    print(f"\n  {Fore.CYAN}── Timing ──{Style.RESET_ALL}")
    print(f"  {'Total':<22} {t['total_ms']} ms")
    print(f"  {'Time to First Byte':<22} {t['ttfb_ms']} ms")
    print(f"  {'Body Download':<22} {t['download_ms']} ms")

    # Redirects
    if record["redirects"]:
        print(f"\n  {Fore.YELLOW}── Redirects ({len(record['redirects'])}) ──{Style.RESET_ALL}")
        for rd in record["redirects"]:
            print(f"  {rd['status_code']} → {rd['to_url'][:55]}")

    # Security
    print(f"\n  {Fore.CYAN}── Security ──{Style.RESET_ALL}")
    tls = f"{Fore.GREEN}✓ HTTPS{Style.RESET_ALL}" if s["is_https"] else f"{Fore.RED}✗ HTTP (insecure){Style.RESET_ALL}"
    hsts = f"{Fore.GREEN}✓ Present{Style.RESET_ALL}" if s["hsts"] else f"{Fore.YELLOW}✗ Missing{Style.RESET_ALL}"
    csp = f"{Fore.GREEN}✓ Present{Style.RESET_ALL}" if s["content_security_policy"] else f"{Fore.YELLOW}✗ Missing{Style.RESET_ALL}"
    cors = s["cors_allowed_origin"] or f"{Fore.YELLOW}Not set{Style.RESET_ALL}"

    print(f"  {'TLS/HTTPS':<22} {tls}")
    print(f"  {'HSTS':<22} {hsts}")
    print(f"  {'Content-Security-Policy':<22} {csp}")
    print(f"  {'CORS Origin':<22} {cors}")
    print(f"  {'CDN Provider':<22} {s['cdn_provider']}")
    print(f"  {'Cache-Control':<22} {s['cache_control'] or 'Not set'}")
    print()


def print_comparison(diff: dict):
    """Pretty-prints a comparison between two URLs."""
    print(f"\n{Fore.CYAN}{'═'*60}")
    print(f"  RESPONSE COMPARISON")
    print(f"  A: {diff['url_a'][:50]}")
    print(f"  B: {diff['url_b'][:50]}")
    print(f"{'═'*60}{Style.RESET_ALL}")

    if diff["identical"]:
        print(f"\n  {Fore.GREEN}✓ Responses are identical on all checked fields.{Style.RESET_ALL}\n")
        return

    print(f"\n  {Fore.RED}✗ {len(diff['differences'])} difference(s) found:{Style.RESET_ALL}\n")
    rows = []
    for d in diff["differences"]:
        rows.append([d["field"], str(d["value_a"]), str(d["value_b"])])

    print(tabulate(rows, headers=["Field", "URL A", "URL B"], tablefmt="rounded_outline"))

    if diff["matches"]:
        print(f"\n  {Fore.GREEN}✓ Matching fields: {', '.join(diff['matches'])}{Style.RESET_ALL}")
    print()


def save_html_report(records: list, filename: str = None):
    """
    Saves all analyzed records as a standalone HTML report.
    Opens in any browser — useful for sharing with teammates.
    """
    os.makedirs("reports", exist_ok=True)
    if not filename:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/http_analysis_{ts}.html"

    rows_html = ""
    for rec in records:
        url = rec["request"]["url"]
        if rec["error"]:
            rows_html += f"""
            <tr class="error">
              <td>{url}</td><td colspan="5">ERROR: {rec['error']}</td>
            </tr>"""
            continue

        r = rec["response"]
        t = rec["timing"]
        s = rec["security"]
        status_class = "ok" if r["status_code"] == 200 else "warn" if r["status_code"] < 500 else "err"
        tls_badge = '<span class="badge green">HTTPS</span>' if s["is_https"] else '<span class="badge red">HTTP</span>'
        hsts_badge = '<span class="badge green">HSTS ✓</span>' if s["hsts"] else '<span class="badge yellow">No HSTS</span>'

        rows_html += f"""
        <tr>
          <td class="url-cell" title="{url}">{url[:60]}{'…' if len(url)>60 else ''}</td>
          <td class="{status_class}">{r['status_code']} {r['status_text']}</td>
          <td>{t['total_ms']} ms</td>
          <td>{t['ttfb_ms']} ms</td>
          <td>{r['body_size_kb']} KB</td>
          <td>{tls_badge} {hsts_badge}</td>
          <td>{s['cdn_provider']}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>HTTP Traffic Analysis Report</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; background: #0f1117; color: #c9d1d9; margin: 0; padding: 2rem; }}
  h1 {{ color: #58a6ff; font-size: 1.4rem; margin-bottom: 0.3rem; }}
  p.meta {{ color: #8b949e; font-size: 0.85rem; margin-bottom: 2rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  th {{ background: #161b22; color: #8b949e; text-align: left; padding: 10px 12px; border-bottom: 1px solid #30363d; }}
  td {{ padding: 9px 12px; border-bottom: 1px solid #21262d; vertical-align: top; }}
  tr:hover td {{ background: #161b22; }}
  .ok {{ color: #3fb950; font-weight: 600; }}
  .warn {{ color: #d29922; font-weight: 600; }}
  .err {{ color: #f85149; font-weight: 600; }}
  tr.error td {{ color: #f85149; }}
  .url-cell {{ font-family: monospace; font-size: 0.82rem; color: #79c0ff; max-width: 320px; word-break: break-all; }}
  .badge {{ font-size: 0.75rem; padding: 2px 7px; border-radius: 12px; font-weight: 600; }}
  .badge.green {{ background: #1f4d2e; color: #3fb950; }}
  .badge.red {{ background: #4d1f1f; color: #f85149; }}
  .badge.yellow {{ background: #4d3800; color: #d29922; }}
</style>
</head>
<body>
<h1>🔍 HTTP Traffic Analysis Report</h1>
<p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {len(records)} URL(s) analyzed</p>
<table>
  <thead>
    <tr>
      <th>URL</th><th>Status</th><th>Total</th><th>TTFB</th><th>Size</th><th>Security</th><th>CDN</th>
    </tr>
  </thead>
  <tbody>
    {rows_html}
  </tbody>
</table>
</body>
</html>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    return filename
