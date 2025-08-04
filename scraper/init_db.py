import sqlite3
from datetime import datetime, timedelta
import os
# Path to DB one level above 'scraper' folder
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'news.db'))

# print("DB_PATH:", DB_PATH)

def init_db():
    """Creates the news database and table if they do not already exist."""

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        published_date TEXT NOT NULL,
        source_url TEXT NOT NULL,
        upload_date TEXT NOT NULL,
        image_url TEXT DEFAULT NULL,
        category TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()


def delete_old_news():
    """Delete old news more than 3 days ago"""
    # Cutoff datetime: 3 days ago from now
    cutoff_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Delete rows where published_date is older than 3 days
    c.execute('''
        DELETE FROM news
        WHERE published_date < ?
    ''', (cutoff_date,))

    conn.commit()
    conn.close()



def upload_news(news_list):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Fetch all existing titles once
    c.execute('SELECT title FROM news')
    existing_titles = set(row[0] for row in c.fetchall())

    to_insert = []
    for news in news_list:
        if news['title'] not in existing_titles:
            to_insert.append((
                news['title'],
                news['published_date'],
                news['source_url'],
                news['upload_date'],
                news['image_url'],
                news['category']
            ))
            existing_titles.add(news['title'])

    if to_insert:
        c.executemany('''
            INSERT INTO news (title, published_date, source_url, upload_date, image_url, category)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', to_insert)

    conn.commit()
    conn.close()
    return f"Scraped and uploaded {len(to_insert)} news articles."



