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
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="he-IL",
                timezone_id="Asia/Jerusalem",
            )
            page = context.new_page()

            # הסתרת סימני אוטומציה
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
                window.chrome = {runtime: {}};
            """)

            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(8000)
            html = page.content()
            browser.close()
        return jsonify({"html": html, "status_code": 200})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
