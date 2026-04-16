import streamlit as st
import pandas as pd
import json
from utils import fire_request
from validator import validate_response

st.set_page_config(page_title="API Testing Dashboard", layout="wide")
st.title("🧪 API Testing Dashboard")
st.caption("Test public API endpoints — validate status, response time, schema, and anomalies")

# ---------- Session state for history ----------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- Sidebar: Request Builder ----------
with st.sidebar:
    st.header("⚙️ Request Builder")

    url = st.text_input("API Endpoint URL", placeholder="https://jsonplaceholder.typicode.com/posts/1")
    method = st.selectbox("HTTP Method", ["GET", "POST", "PUT", "DELETE"])

    st.subheader("Headers (optional)")
    headers_input = st.text_area("JSON format", value='{"Content-Type": "application/json"}', height=80)

    st.subheader("Request Body (POST/PUT only)")
    body_input = st.text_area("JSON format", value="{}", height=100)

    st.divider()
    st.subheader("🔍 Validation Rules")
    expected_status = st.number_input("Expected Status Code", value=200, step=1)
    max_response_time = st.slider("Max Response Time (ms)", 100, 5000, 1000, step=100)
    required_fields = st.text_input("Required Fields in Response (comma-separated)", placeholder="id, title, body")

    send = st.button("🚀 Send Request", use_container_width=True)

# ---------- Main Panel ----------
if send:
    if not url:
        st.error("Please enter a URL.")
    else:
        # Parse headers and body
        try:
            headers = json.loads(headers_input) if headers_input.strip() else {}
        except:
            headers = {}
            st.warning("Invalid headers JSON — sending without headers.")

        try:
            body = json.loads(body_input) if body_input.strip() else {}
        except:
            body = {}
            st.warning("Invalid body JSON — sending empty body.")

        with st.spinner("Firing request..."):
            response, error = fire_request(method, url, headers, body)

        if error:
            st.error(f"Request Failed: {error}")
        else:
            col1, col2, col3 = st.columns(3)
            elapsed_ms = response.elapsed.total_seconds() * 1000
            col1.metric("Status Code", response.status_code)
            col2.metric("Response Time", f"{elapsed_ms:.0f} ms")
            col3.metric("Content Size", f"{len(response.content)} bytes")

            # Validation
            st.subheader("🔎 Validation Results")
            validation_results, passed, elapsed_ms, json_body = validate_response(
                response, expected_status, max_response_time, required_fields
            )

            overall = "✅ ALL CHECKS PASSED" if passed else "❌ ONE OR MORE CHECKS FAILED"
            if passed:
                st.success(overall)
            else:
                st.error(overall)

            for check, detail in validation_results:
                st.write(f"**{check}** — {detail}")

            # Response body
            st.subheader("📦 Response Body")
            if json_body:
                st.json(json_body)
            else:
                st.code(response.text)

            # Add to history
            st.session_state.history.append({
                "URL": url,
                "Method": method,
                "Status": response.status_code,
                "Time (ms)": round(elapsed_ms),
                "Result": "PASS" if passed else "FAIL"
            })

# ---------- Test History ----------
st.divider()
st.subheader("📋 Test History (This Session)")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    
    def color_result(val):
        return "background-color: #d4edda" if val == "PASS" else "background-color: #f8d7da"
    
    st.dataframe(df.style.applymap(color_result, subset=["Result"]), use_container_width=True)

    pass_count = sum(1 for h in st.session_state.history if h["Result"] == "PASS")
    fail_count = len(st.session_state.history) - pass_count
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Requests", len(st.session_state.history))
    c2.metric("Passed", pass_count)
    c3.metric("Failed", fail_count)

    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.rerun()
else:
    st.info("No requests fired yet. Use the sidebar to send your first request.")