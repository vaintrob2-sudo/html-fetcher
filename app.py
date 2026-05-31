from flask import Flask, request, jsonify
import os

app = Flask(__name__)
API_KEY = os.environ.get("API_KEY", "mysecret1")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/fetch-html")
def fetch_html():
    if request.headers.get("X-API-Key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing url"}), 400

    try:
        from curl_cffi import requests as curl_requests
        response = curl_requests.get(
            url,
            impersonate="chrome",
            timeout=30
        )
        return jsonify({
            "html": response.text,
            "status_code": response.status_code
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
