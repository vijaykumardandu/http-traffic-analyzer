# ─────────────────────────────────────────────
# analyzer/capture.py
# Core engine: sends HTTP requests and captures everything about them
# This is the "traffic capture" part of the tool
# ─────────────────────────────────────────────

import time
import requests
from datetime import datetime


def analyze_request(url: str, method: str = "GET", headers: dict = None,
                    follow_redirects: bool = True, timeout: int = 10) -> dict:
    """
    Sends an HTTP request and captures everything about it:
    - Request details (method, headers sent)
    - Response details (status, headers received, body size)
    - Timing breakdown (how long each phase took)
    - Redirect chain (if any)
    - Security signals (HTTPS, HSTS, etc.)

    Returns a rich dictionary with all captured data.
    """
    if headers is None:
        headers = {
            "User-Agent": "HTTPAnalyzer/1.0 (QA Tool)",
            "Accept": "*/*",
        }

    record = {
        "timestamp": datetime.now().isoformat(),
        "request": {
            "url": url,
            "method": method.upper(),
            "headers": headers,
        },
        "response": None,
        "timing": {},
        "redirects": [],
        "security": {},
        "error": None,
    }

    try:
        # ── Phase 1: DNS + TCP + TLS + First byte (all measured together) ──
        t_start = time.perf_counter()
        response = requests.request(
            method,
            url,
            headers=headers,
            allow_redirects=follow_redirects,
            timeout=timeout,
            stream=True,       # Don't download body yet — measure TTFB first
        )
        t_first_byte = time.perf_counter()

        # ── Phase 2: Download the body ──
        body = response.content  # now we download
        t_end = time.perf_counter()

        # ── Build timing breakdown ──
        record["timing"] = {
            "total_ms": round((t_end - t_start) * 1000, 2),
            "ttfb_ms": round((t_first_byte - t_start) * 1000, 2),    # Time To First Byte
            "download_ms": round((t_end - t_first_byte) * 1000, 2),  # Body download time
        }

        # ── Build response record ──
        record["response"] = {
            "status_code": response.status_code,
            "status_text": _status_text(response.status_code),
            "headers": dict(response.headers),
            "body_size_bytes": len(body),
            "body_size_kb": round(len(body) / 1024, 2),
            "content_type": response.headers.get("Content-Type", "unknown"),
            "encoding": response.encoding,
        }

        # ── Redirect chain ──
        if response.history:
            for r in response.history:
                record["redirects"].append({
                    "from_url": r.url,
                    "to_url": r.headers.get("Location", "?"),
                    "status_code": r.status_code,
                })

        # ── Security analysis ──
        record["security"] = _analyze_security(url, response)

    except requests.exceptions.Timeout:
        record["error"] = "TIMEOUT: Server did not respond within the timeout window"
    except requests.exceptions.SSLError as e:
        record["error"] = f"SSL_ERROR: {str(e)[:120]}"
    except requests.exceptions.ConnectionError as e:
        record["error"] = f"CONNECTION_ERROR: {str(e)[:120]}"
    except Exception as e:
        record["error"] = f"UNEXPECTED_ERROR: {str(e)[:120]}"

    return record


def _analyze_security(url: str, response: requests.Response) -> dict:
    """
    Checks for common security headers and signals.
    These are important for CDN/edge server QA — misconfigured headers
    are a common source of production incidents.
    """
    headers = response.headers

    return {
        "is_https": url.startswith("https://"),
        "hsts": headers.get("Strict-Transport-Security") is not None,
        "hsts_value": headers.get("Strict-Transport-Security"),
        "x_frame_options": headers.get("X-Frame-Options"),
        "content_security_policy": headers.get("Content-Security-Policy") is not None,
        "x_content_type_options": headers.get("X-Content-Type-Options"),
        "cors_allowed_origin": headers.get("Access-Control-Allow-Origin"),
        "cache_control": headers.get("Cache-Control"),
        "cdn_provider": _detect_cdn(headers),
    }


def _detect_cdn(headers: dict) -> str:
    """
    Heuristically detects which CDN is serving the response
    based on response headers — a useful skill for edge server QA.
    """
    server = headers.get("Server", "").lower()
    via = headers.get("Via", "").lower()
    x_cache = headers.get("X-Cache", "").lower()

    if "cloudflare" in server or headers.get("CF-Ray"):
        return "Cloudflare"
    if "akamai" in via or headers.get("X-Check-Cacheable"):
        return "Akamai"
    if "fastly" in headers.get("X-Served-By", "").lower() or "fastly" in via:
        return "Fastly"
    if "amazon" in via or headers.get("X-Amz-Cf-Id"):
        return "AWS CloudFront"
    if "gws" in server or "google" in via:
        return "Google CDN"
    if "nginx" in server:
        return "Nginx (self-hosted or generic)"
    if "apache" in server:
        return "Apache (self-hosted or generic)"
    return "Unknown / Not detected"


def _status_text(code: int) -> str:
    """Returns human-readable HTTP status text."""
    STATUS_MAP = {
        200: "OK", 201: "Created", 204: "No Content",
        301: "Moved Permanently", 302: "Found", 304: "Not Modified",
        400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
        404: "Not Found", 408: "Request Timeout", 429: "Too Many Requests",
        500: "Internal Server Error", 502: "Bad Gateway",
        503: "Service Unavailable", 504: "Gateway Timeout",
    }
    return STATUS_MAP.get(code, "Unknown")
