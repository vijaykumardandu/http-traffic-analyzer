# ─────────────────────────────────────────────
# analyzer/comparator.py
# Compares two HTTP responses — super useful for CDN/edge QA
# (e.g. "is the prod server returning the same thing as staging?")
# ─────────────────────────────────────────────


def compare_responses(record_a: dict, record_b: dict) -> dict:
    """
    Compares two captured response records (from capture.py) and
    returns a structured diff of all differences.

    Useful for:
    - Comparing prod vs staging
    - Comparing CDN cached vs origin response
    - Validating that a code deploy didn't change API behavior
    """
    diffs = []
    matches = []

    def _check(field_name, val_a, val_b):
        if val_a == val_b:
            matches.append(field_name)
        else:
            diffs.append({
                "field": field_name,
                "url_a": record_a["request"]["url"],
                "url_b": record_b["request"]["url"],
                "value_a": val_a,
                "value_b": val_b,
            })

    # Compare status codes
    if record_a["response"] and record_b["response"]:
        _check("status_code",
               record_a["response"]["status_code"],
               record_b["response"]["status_code"])

        _check("content_type",
               record_a["response"]["content_type"],
               record_b["response"]["content_type"])

        _check("body_size_bytes",
               record_a["response"]["body_size_bytes"],
               record_b["response"]["body_size_bytes"])

        # Compare key headers
        important_headers = [
            "Cache-Control", "Content-Encoding",
            "Access-Control-Allow-Origin", "Strict-Transport-Security"
        ]
        for h in important_headers:
            _check(
                f"header:{h}",
                record_a["response"]["headers"].get(h),
                record_b["response"]["headers"].get(h),
            )

        # Compare redirect count
        _check("redirect_count",
               len(record_a["redirects"]),
               len(record_b["redirects"]))

    return {
        "url_a": record_a["request"]["url"],
        "url_b": record_b["request"]["url"],
        "differences": diffs,
        "matches": matches,
        "identical": len(diffs) == 0,
    }
