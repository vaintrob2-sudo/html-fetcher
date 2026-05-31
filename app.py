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
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)  # המתן 5 שניות ל-Cloudflare
            html = page.content()
            browser.close()
        return jsonify({"html": html, "status_code": 200})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
