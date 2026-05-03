# ─────────────────────────────────────────────
# main.py
# Command-line interface for the HTTP Traffic Analyzer
#
# USAGE EXAMPLES:
#   Analyze a single URL:
#     python main.py analyze https://example.com
#
#   Analyze multiple URLs from a file:
#     python main.py batch urls.txt
#
#   Compare two URLs side-by-side:
#     python main.py compare https://prod.example.com https://staging.example.com
#
#   Save an HTML report after batch analysis:
#     python main.py batch urls.txt --report
# ─────────────────────────────────────────────

import sys
import os

# Make sure Python can find our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyzer.capture import analyze_request
from analyzer.comparator import compare_responses
from reports.reporter import print_single_analysis, print_comparison, save_html_report
from colorama import Fore, Style, init

init(autoreset=True)


def cmd_analyze(url: str):
    """Analyze a single URL and print results."""
    print(f"\n{Fore.CYAN}Analyzing: {url}{Style.RESET_ALL}")
    record = analyze_request(url)
    print_single_analysis(record)
    return record


def cmd_batch(filepath: str, save_report: bool = False):
    """
    Analyze all URLs listed in a text file (one URL per line).
    Lines starting with # are treated as comments and skipped.
    """
    if not os.path.exists(filepath):
        print(f"{Fore.RED}Error: File not found: {filepath}{Style.RESET_ALL}")
        sys.exit(1)

    with open(filepath, "r") as f:
        urls = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]

    if not urls:
        print(f"{Fore.YELLOW}No URLs found in {filepath}{Style.RESET_ALL}")
        return

    print(f"\n{Fore.CYAN}Batch analyzing {len(urls)} URLs...{Style.RESET_ALL}")
    records = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        record = analyze_request(url)
        print_single_analysis(record)
        records.append(record)

    if save_report:
        path = save_html_report(records)
        print(f"{Fore.GREEN}📄 HTML report saved: {path}{Style.RESET_ALL}")

    return records


def cmd_compare(url_a: str, url_b: str):
    """Fetch both URLs and print a side-by-side diff of their responses."""
    print(f"\n{Fore.CYAN}Fetching URL A: {url_a}{Style.RESET_ALL}")
    record_a = analyze_request(url_a)

    print(f"{Fore.CYAN}Fetching URL B: {url_b}{Style.RESET_ALL}")
    record_b = analyze_request(url_b)

    diff = compare_responses(record_a, record_b)
    print_comparison(diff)


def print_help():
    print(f"""
{Fore.CYAN}HTTP Traffic Analyzer{Style.RESET_ALL}

Usage:
  python main.py analyze <url>
  python main.py batch <urls_file.txt> [--report]
  python main.py compare <url_a> <url_b>

Commands:
  analyze   Analyze a single URL — shows status, timing, security headers, CDN
  batch     Analyze all URLs in a file (one per line, # for comments)
  compare   Compare two URLs side by side — shows what's different

Options:
  --report  (batch only) Also save results as an HTML report

Examples:
  python main.py analyze https://example.com
  python main.py batch urls.txt --report
  python main.py compare https://google.com https://bing.com
""")


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print_help()
        return

    command = args[0].lower()

    if command == "analyze":
        if len(args) < 2:
            print(f"{Fore.RED}Usage: python main.py analyze <url>{Style.RESET_ALL}")
            sys.exit(1)
        cmd_analyze(args[1])

    elif command == "batch":
        if len(args) < 2:
            print(f"{Fore.RED}Usage: python main.py batch <urls_file.txt> [--report]{Style.RESET_ALL}")
            sys.exit(1)
        save_report = "--report" in args
        cmd_batch(args[1], save_report=save_report)

    elif command == "compare":
        if len(args) < 3:
            print(f"{Fore.RED}Usage: python main.py compare <url_a> <url_b>{Style.RESET_ALL}")
            sys.exit(1)
        cmd_compare(args[1], args[2])

    else:
        print(f"{Fore.RED}Unknown command: {command}{Style.RESET_ALL}")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
