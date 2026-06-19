from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import re
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

@app.route('/bypass')
def bypass():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'url required'}), 400
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        try:
            page.goto(url, timeout=20000, wait_until='networkidle')
            page.wait_for_timeout(2000)
            content = page.content()
            final_url = page.url
            browser.close()
            m = re.search(r'FREE_[a-fA-F0-9]{32}', content)
            if m:
                return jsonify({'key': m.group(0)})
            qs = parse_qs(urlparse(final_url).query)
            for v in qs.values():
                if v[0].startswith('FREE_'):
                    return jsonify({'key': v[0]})
            return jsonify({'error': 'not found'}), 404
        except:
            browser.close()
            return jsonify({'error': 'failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
