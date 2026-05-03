# HTTP Traffic Analyzer

A command-line tool written in Python that sends HTTP requests and tells you everything about the response — how long it took, what headers came back, whether there's a CDN in front, if HTTPS is properly configured, and whether two URLs return the same thing.

I built this while learning about how CDN and edge servers work. Wanted something I could point at any URL and get a clear picture of what's happening at the HTTP level.

---

## What it does

- Analyze a single URL and see status, timing, headers, redirects, security info
- Run it against a list of URLs and get an HTML report
- Compare two URLs and see exactly what's different between them
- Automatically figures out which CDN is serving the response (Cloudflare, Google, Akamai, etc.)
- Checks for security headers like HSTS, CSP, CORS on every request
- Separates Time To First Byte from actual download time so you can tell if the server is slow vs the network

---

## Example outputs

### Analyzing a single URL

```
python main.py analyze https://google.com
```

```
════════════════════════════════════════════════════════════
  HTTP TRAFFIC ANALYSIS
  https://google.com
════════════════════════════════════════════════════════════

  Status                 200 OK
  Content-Type           text/html; charset=ISO-8859-1
  Body Size              80.33 KB (82254 bytes)

  ── Timing ──
  Total                  1499.91 ms
  Time to First Byte     1205.9 ms
  Body Download          294.01 ms

  ── Redirects (1) ──
  301 → https://www.google.com/

  ── Security ──
  TLS/HTTPS              ✓ HTTPS
  HSTS                   ✗ Missing
  Content-Security-Policy ✗ Missing
  CORS Origin            Not set
  CDN Provider           Google CDN
  Cache-Control          private, max-age=0
```

---

### Comparing two URLs

```
python main.py compare https://google.com https://bing.com
```

```
════════════════════════════════════════════════════════════
  RESPONSE COMPARISON
  A: https://google.com
  B: https://bing.com
════════════════════════════════════════════════════════════

  ✗ 4 difference(s) found:

╭──────────────────────────────────┬───────────────────────────────┬──────────────────────────────────────────────╮
│ Field                            │ URL A                         │ URL B                                        │
├──────────────────────────────────┼───────────────────────────────┼──────────────────────────────────────────────┤
│ content_type                     │ text/html; charset=ISO-8859-1 │ text/html; charset=utf-8                     │
│ body_size_bytes                  │ 82378                         │ 63964                                        │
│ header:Cache-Control             │ private, max-age=0            │ private                                      │
│ header:Strict-Transport-Security │ None                          │ max-age=31536000; includeSubDomains; preload │
╰──────────────────────────────────┴───────────────────────────────┴──────────────────────────────────────────────╯

  ✓ Matching fields: status_code, header:Content-Encoding, header:Access-Control-Allow-Origin, redirect_count
```

The interesting thing here is the HSTS difference. Bing has it set with a 1-year expiry and is on the browser preload list. Google doesn't have it on the root domain at all — it just does a 301 redirect to www instead. Small difference but it matters from a security standpoint.

---

### Batch analysis with HTML report

```
python main.py batch urls.txt --report
```

```
Batch analyzing 7 URLs...

[1/7] https://httpbin.org/get          → 200 OK  | 2265.5 ms
[2/7] https://httpbin.org/status/200   → 200 OK  | 3281.1 ms
[3/7] https://httpbin.org/status/404   → 404     | 3193.3 ms
[4/7] https://httpbin.org/redirect/2   → 200 OK  | 3268.6 ms  | 2 redirects
[5/7] https://httpbin.org/delay/1      → 200 OK  | 3588.3 ms
[6/7] https://example.com              → 200 OK  | 1215.1 ms  | Cloudflare
[7/7] https://google.com               → 200 OK  | 2035.0 ms  | Google CDN

📄 HTML report saved: reports/http_analysis_20260503_094007.html
```
## HTML Report

<img width="2856" height="1417" alt="image" src="https://github.com/user-attachments/assets/9fcbba41-d877-44b5-8568-6bb997840f5f" />


## Test Report Screenshot
<img width="2336" height="1052" alt="image" src="https://github.com/user-attachments/assets/785a02d8-0a4e-4428-9d5b-d4349786cffa" />


Saves a dark-themed HTML file you can open in a browser or share with someone.

---

## Setup

You need Python 3.10 or above.

```bash
git clone https://github.com/vijaykumardandu/http-traffic-analyzer.git
cd http-traffic-analyzer

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

---

## How to use it

```bash
# single URL
python main.py analyze https://example.com

# multiple URLs from a text file
python main.py batch urls.txt

# multiple URLs + save HTML report
python main.py batch urls.txt --report

# compare two URLs
python main.py compare https://prod.example.com https://staging.example.com
```

Add your own URLs to `urls.txt` — one per line, lines starting with `#` are ignored.

---

## Project structure

```
http_traffic_analyzer/
├── analyzer/
│   ├── capture.py        ← sends the request, measures timing, parses headers
│   └── comparator.py     ← diffs two responses field by field
├── reports/
│   └── reporter.py       ← prints to terminal and generates the HTML report
├── main.py               ← CLI (analyze / batch / compare commands)
├── urls.txt              ← sample URLs to test with
└── requirements.txt
```

---

## Dependencies

```
requests==2.31.0
colorama==0.4.6
tabulate==0.9.0
python-dotenv==1.0.0
```
