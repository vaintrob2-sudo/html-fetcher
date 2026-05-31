from flask import Flask, request, jsonify
import os

app = Flask(__name__)
API_KEY = os.environ.get("API_KEY", "mysecret1")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/fetch-html-scrapfly")
def fetch_html_scrapfly():
    if request.headers.get("X-API-Key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing url"}), 400

    try:
        from scrapfly import ScrapeConfig, ScrapflyClient
        SCRAPFLY_KEY = os.environ.get("SCRAPFLY_KEY")
        client = ScrapflyClient(key=SCRAPFLY_KEY)
        result = client.scrape(ScrapeConfig(
            url=url,
            asp=True,  # עוקף Cloudflare
            render_js=True,  # מריץ JavaScript
        ))
        return jsonify({
            "html": result.scrape_result["content"],
            "status_code": 200
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
