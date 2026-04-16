def validate_response(response, expected_status, max_response_time, required_fields):
    results = []
    passed = True

    # 1. Status code check
    if response.status_code == expected_status:
        results.append(("✅ Status Code", f"{response.status_code} — as expected"))
    else:
        results.append(("❌ Status Code", f"{response.status_code} — expected {expected_status}"))
        passed = False

    # 2. Response time check
    elapsed_ms = response.elapsed.total_seconds() * 1000
    if elapsed_ms <= max_response_time:
        results.append(("✅ Response Time", f"{elapsed_ms:.0f} ms — within {max_response_time} ms threshold"))
    else:
        results.append(("⚠️ Response Time", f"{elapsed_ms:.0f} ms — SLOW (threshold: {max_response_time} ms)"))
        passed = False

    # 3. JSON parse check
    try:
        json_body = response.json()
        results.append(("✅ JSON Parse", "Valid JSON response"))
    except Exception:
        results.append(("❌ JSON Parse", "Response is not valid JSON"))
        return results, False, elapsed_ms, {}

    # 4. Required fields check
    if required_fields:
        fields = [f.strip() for f in required_fields.split(",") if f.strip()]
        missing = [f for f in fields if f not in json_body]
        if not missing:
            results.append(("✅ Required Fields", f"All fields present: {fields}"))
        else:
            results.append(("❌ Required Fields", f"Missing fields: {missing}"))
            passed = False

    # 5. Anomaly flags
    if response.status_code >= 500:
        results.append(("🚨 Anomaly", "Server error (5xx) — API is broken or down"))
        passed = False
    elif response.status_code >= 400:
        results.append(("⚠️ Anomaly", "Client error (4xx) — bad request or unauthorized"))
        passed = False
    elif response.status_code >= 300:
        results.append(("⚠️ Anomaly", "Redirect (3xx) — endpoint may have moved"))

    return results, passed, elapsed_ms, json_body