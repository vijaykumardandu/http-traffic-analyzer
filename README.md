# 🔍 HTTP Traffic Analyzer

A command-line tool that intercepts and analyzes HTTP traffic — capturing timing,
security headers, redirect chains, CDN detection, and response diffs between URLs.

## What this demonstrates (for your resume)
- Deep HTTP protocol knowledge (status codes, headers, TTFB, redirects, CORS, HSTS)
- CDN/edge server detection from response headers
- Security header auditing
- Prod vs staging comparison (response diffing)
- HTML report generation for team sharing / CI pipelines

---

## Setup (Windows)

### 1. Create virtual environment
```
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

---

## Usage

### Analyze a single URL
```
python main.py analyze https://example.com
```
Shows: status code, timing breakdown, body size, CDN provider, security headers

### Analyze multiple URLs from a file
```
python main.py batch urls.txt
```
Edit `urls.txt` to add any URLs you want to test (one per line, `#` for comments)

### Save results as an HTML report
```
python main.py batch urls.txt --report
```
Saves a dark-themed HTML report in `reports/` folder — shareable with your team

### Compare two URLs side-by-side
```
python main.py compare https://prod.example.com https://staging.example.com
```
Useful for: prod vs staging, CDN cached vs origin, before/after deploys

---

## Project structure
```
http_traffic_analyzer/
├── analyzer/
│   ├── capture.py        ← Core HTTP engine (sends requests, captures everything)
│   └── comparator.py     ← Diffs two response records field-by-field
├── reports/
│   └── reporter.py       ← Terminal printing + HTML report generation
├── main.py               ← CLI entry point (analyze / batch / compare)
├── urls.txt              ← Sample URLs for batch testing
└── requirements.txt
```

## What gets captured per request

| Field | What it means |
|---|---|
| Status code | HTTP response code (200, 404, 503, etc.) |
| Total latency | End-to-end request time |
| TTFB | Time To First Byte — when the server started responding |
| Body size | How many bytes were downloaded |
| Content-Type | What kind of content was returned |
| Redirects | Full redirect chain with status codes |
| HTTPS / TLS | Whether the connection is encrypted |
| HSTS | Whether the server enforces HTTPS |
| CORS | Cross-Origin Resource Sharing settings |
| Cache-Control | Caching directives from the server |
| CDN Provider | Auto-detected from response headers |

## Resume talking points

> "I built a Python HTTP traffic analyzer that captures timing, security headers,
> redirect chains, and CDN detection for any URL. It supports batch analysis of
> multiple endpoints and can diff two responses field-by-field — useful for
> validating prod vs staging consistency or detecting CDN misconfiguration.
> Results are exported as standalone HTML reports."
