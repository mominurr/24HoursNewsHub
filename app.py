from flask import Flask, render_template, request
import sqlite3
from scraper.scrape_task import run_scraper
import threading
import time
import os
app = Flask(__name__)
WITH_LOCK_FLAG = True
SCRAPE_TIMESTAMP_FILE = 'last_scrape.txt'

def get_last_scrape_time():
    if os.path.exists(SCRAPE_TIMESTAMP_FILE):
        with open(SCRAPE_TIMESTAMP_FILE, 'r') as f:
            try:
                return float(f.read().strip())
            except:
                return 0.0
    return 0.0

def set_last_scrape_time(ts):
    with open(SCRAPE_TIMESTAMP_FILE, 'w') as f:
        f.write(str(ts))

def maybe_scrape():
    global WITH_LOCK_FLAG
    if not WITH_LOCK_FLAG:
        return False
    WITH_LOCK_FLAG = False
    now = time.time()
    last_scrape = get_last_scrape_time()
    # 3 hours = 10800 seconds
    # 1 hour=60 minutes×60 seconds=3600 seconds
    if now - last_scrape < 3600:
        return False
    result = run_scraper()
    set_last_scrape_time(now)
    WITH_LOCK_FLAG = True
    return True


def get_news(category, page, per_page=20, search=None):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    offset = (page - 1) * per_page
    params = [category]
    query = "SELECT title, published_date, source_url, upload_date, image_url FROM news WHERE category=?"
    if search:
        # Use fuzzy matching with SQLite's LIKE and lower() for case-insensitivity
        query += " AND lower(title) LIKE lower(?)"
        params.append(f"%{search}%")
    query += " ORDER BY published_date DESC LIMIT ? OFFSET ?"
    params.extend([per_page, offset])
    c.execute(query, params)
    news_items = c.fetchall()
    # Get total count for pagination
    count_query = "SELECT COUNT(*) FROM news WHERE category=?"
    count_params = [category]
    if search:
        count_query += " AND lower(title) LIKE lower(?)"
        count_params.append(f"%{search}%")
    c.execute(count_query, count_params)
    total = c.fetchone()[0]
    conn.close()
    return news_items, total

@app.route('/')
def index():
    threading.Thread(target=maybe_scrape, daemon=True).start()  # Only runs if last scrape was >3 hours ago
    category = request.args.get('category', 'bangla_news')
    page = int(request.args.get('page', 1))
    per_page = 20
    search = request.args.get('search', None)
    news_items, total = get_news(category, page, per_page, search)
    total_pages = (total + per_page - 1) // per_page
    no_results = search and not news_items
    return render_template('index.html', category=category, news_items=news_items, page=page, total_pages=total_pages, request=request, no_results=no_results)

if __name__ == '__main__':
    app.run(debug=True)
