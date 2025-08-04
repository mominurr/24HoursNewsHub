import curl_cffi
from bs4 import BeautifulSoup as bs
from dateutil import parser
from datetime import datetime, timezone
import random
from .init_db import init_db, delete_old_news, upload_news
import warnings
warnings.filterwarnings("ignore")
init_db()  # Ensure the database is initialized
delete_old_news() # delete old more than 3 days news

BrowserNames = [
    "chrome",
    "chrome99",
    "chrome100",
    "chrome101",
    "chrome104",
    "chrome107",
    "chrome110",
    "chrome116",
    "chrome119",
    "chrome120",
    "chrome123",
    "chrome124",
    "chrome131",
    "chrome133a",
    "chrome136",
    "chrome99_android",
    "chrome131_android",
    "edge99",
    "edge101",
    "safari",
    "safari15_3",
    "safari15_5",
    "safari17_0",
    "safari17_2_ios",
    "safari18_0",
    "safari18_0_ios",
    "firefox133",
    "firefox135",
    "safari172_ios",
    "safari180_ios",
    "safari184_ios",
    "safari260_ios",
    "safari153",
    "safari155",
    "safari170",
    "safari180",
    "safari184",
    "safari260",

]



# Function to get a response from a URL
# with a specified method (GET or POST)
def get_response(url,method="GET"):
    if method == "GET":
        try:
            response = curl_cffi.get(url, impersonate=random.choice(BrowserNames), timeout=(10,10))
            return response
        except:
            return None
    elif method == "POST":
        try:
            response = curl_cffi.post(url, impersonate=random.choice(BrowserNames), timeout=(10,10))
            return response
        except:
            return None
    else:
        return None


# Function to format ISO 8601 datetime strings
# to a more readable format (e.g., "2023-10-01 12:00") 
# and check if they are within the last 24 hours
# this function will also handle various datetime formats
# and return a tuple of formatted datetime string and a boolean
def smart_datetime_format_and_check(dt_input):
    try:
        # Step 1: Convert Unix timestamp if input is numeric string or int/float
        if isinstance(dt_input, (int, float)) or (isinstance(dt_input, str) and dt_input.isdigit()):
            dt = datetime.fromtimestamp(float(dt_input), tz=timezone.utc)
        else:
            # Step 2: Otherwise, treat it as a date string
            dt = parser.parse(dt_input)

            # Make timezone-aware if it isn't
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

        # Step 3: Compare with current time
        now = datetime.now(timezone.utc)
        time_difference = now - dt
        is_within_24_hours = time_difference.total_seconds() <= 86400  # 24 hours

        # Step 4: Format output
        formatted = dt.strftime("%Y-%m-%d %H:%M")
        return formatted, is_within_24_hours

    except Exception:
        return None, False


def extract_news_from_prothomalo(response):
    prothomalo_news = []
    try:
        url_tags = bs(response.content, 'lxml').find_all('url')
        for url_tag in url_tags:
            try:
                source_url = url_tag.find('loc').get_text(strip=True)
                title = url_tag.find('news:title').get_text(strip=True)
                published_date = url_tag.find('news:publication_date').get_text(strip=True)
                upload_date = datetime.now().strftime('%Y-%m-%d %H:%M')
                try:
                    image_url = url_tag.find('image:loc').get_text(strip=True)
                except:
                    image_url = None
                formatted_date, is_within_24_hours = smart_datetime_format_and_check(published_date)
                if is_within_24_hours:
                    prothomalo_news.append({
                        'title': title,
                        'published_date': formatted_date,
                        'source_url': source_url,
                        'upload_date': upload_date,
                        'image_url': image_url,
                        'category': 'bangla_news'
                    })
            except:
                pass
    except:
        pass
    
    return prothomalo_news


def extract_news_from_kalerkantho(response):
    kalerkantho_news = []
    try:
        url_tags = bs(response.content, 'lxml').find_all('url')
        for url_tag in url_tags:
            try:
                source_url = url_tag.find('loc').get_text(strip=True)
                title = url_tag.find('image:caption').get_text(strip=True)
                published_date = url_tag.find('lastmod').get_text(strip=True)
                upload_date = datetime.now().strftime('%Y-%m-%d %H:%M')
                try:
                    image_url = url_tag.find('image:loc').get_text(strip=True)
                except:
                    image_url = None
                formatted_date, is_within_24_hours = smart_datetime_format_and_check(published_date)
                if is_within_24_hours:
                    kalerkantho_news.append({
                        'title': title,
                        'published_date': formatted_date,
                        'source_url': source_url,
                        'upload_date': upload_date,
                        'image_url': image_url,
                        'category': 'bangla_news'
                    })
            except:
                pass
    except:
        pass
    return kalerkantho_news




def extract_news_from_ittefaq(response):
    ittefaq_news = []
    try:
        html = response.json().get('html', '')
        div_tags = bs(html, 'lxml').select('div.content_type_news')
        for div_tag in div_tags:
            try:
                source_url = div_tag.find('a',attrs={"class":"link_overlay"}).get('href')
                if source_url and not source_url.startswith('http'):
                    source_url = f"https:{source_url}"
                title = div_tag.find('a',attrs={"class":"link_overlay"}).get_text(strip=True)
                published_date = div_tag.find('span',attrs={"class":"time aitm"}).get('data-published')
                upload_date = datetime.now().strftime('%Y-%m-%d %H:%M')
                image_url = div_tag.find('img').get('src')
                if image_url and not image_url.startswith('http'):
                    image_url = f"https:{image_url}"
                formatted_date, is_within_24_hours = smart_datetime_format_and_check(published_date)
                if is_within_24_hours:
                    ittefaq_news.append({
                        'title': title,
                        'published_date': formatted_date,
                        'source_url': source_url,
                        'upload_date': upload_date,
                        'image_url': image_url,
                        'category': 'bangla_news'
                    })
            except:
                pass
    except:
        pass
    return ittefaq_news



def extract_news_from_tbsnews(response):
    tbsnews = []
    try:
        url_tags = bs(response.content, 'lxml').find_all('url')
        for url_tag in url_tags:
            try:
                source_url = url_tag.find('loc').get_text(strip=True)
                title = url_tag.find('news:title').get_text(strip=True)
                published_date = url_tag.find('news:publication_date').get_text(strip=True)
                upload_date = datetime.now().strftime('%Y-%m-%d %H:%M')
                image_url = None
                formatted_date, is_within_24_hours = smart_datetime_format_and_check(published_date)
                if is_within_24_hours:
                    tbsnews.append({
                        'title': title,
                        'published_date': formatted_date,
                        'source_url': source_url,
                        'upload_date': upload_date,
                        'image_url': image_url,
                        'category': 'bangla_news'
                    })
            except:
                pass
    except:
        pass
    return tbsnews


# Example function for scraping (to be expanded for each category/source)
def scrape_bangla_news():
    bangla_news_urls = {
        "prothomalo":"https://www.prothomalo.com/news_sitemap.xml",
        "kalerkantho":f"https://www.kalerkantho.com/daily-sitemap/{datetime.now().strftime('%Y-%m-%d')}/sitemap.xml",
        "ittefaq":"https://www.ittefaq.com.bd/api/theme_engine/get_ajax_contents?widget=476&start=0&count=200&page_id=0&subpage_id=0&author=0&tags=&archive_time=&filter=",
        "tbsnews":"https://www.tbsnews.net/bangla/googlenews.xml"

    }
    bangla_news = []
    for key, bangla_news_url in bangla_news_urls.items():
        response = get_response(bangla_news_url)
        if response:
            if key == "prothomalo":
                bangla_news.extend(extract_news_from_prothomalo(response))
            elif key == "kalerkantho":
                bangla_news.extend(extract_news_from_kalerkantho(response))
            elif key == "ittefaq":
                bangla_news.extend(extract_news_from_ittefaq(response))
            elif key == "tbsnews":
                bangla_news.extend(extract_news_from_tbsnews(response))
    return bangla_news



def extract_news_from_middleeastmonitor(url):
    middleeastmonitor_news = []
    try:
        response = get_response(url)
        tr_tags = bs(response.content,"lxml").find_all('tr')[1:]
        for tr_tag in tr_tags:
            try:
                td_tags = tr_tag.find_all('td')[1:]
                source_url = td_tags[0].get_text(strip=True)
                title = td_tags[1].get_text(strip=True)
                published_date = td_tags[2].get_text(strip=True)
                upload_date = datetime.now().strftime('%Y-%m-%d %H:%M')
                image_url = None
                formatted_date, is_within_24_hours = smart_datetime_format_and_check(published_date)
                if is_within_24_hours:
                    middleeastmonitor_news.append({
                        'title': title,
                        'published_date': formatted_date,
                        'source_url': source_url,
                        'upload_date': upload_date,
                        'image_url': image_url,
                        'category': 'english_news'
                    })
            except:
                pass
    except:
        pass

    return middleeastmonitor_news



def extract_news_from_businessStandard(url):
    businessStandard_news = []
    try:
        response = get_response(url)
        article_lists = response.json().get('data',{}).get('rows',[])
        for article in article_lists:
            try:
                published_date = article.get('published_date','')
                formatted_date, is_within_24_hours = smart_datetime_format_and_check(published_date)
                if is_within_24_hours:
                        businessStandard_news.append({
                            'title': article.get('heading1'),
                            'published_date': formatted_date,
                            'source_url': f"https://www.business-standard.com{article.get('article_url')}",
                            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                            'image_url': article.get('article_media_maps')[0].get('url') if article.get('article_media_maps',[]) and len(article.get('article_media_maps',[])) > 0 else None,
                            'category': 'english_news'
                        })
            except:
                pass
    except:
        pass

    return businessStandard_news



def extract_news_from_sitemap(url):
    the_news = []
    try:
        response = get_response(url)
        url_tags = bs(response.content,'lxml').find_all('url')
        for url_tag in url_tags:
            try:
                source_url = url_tag.find('loc').get_text(strip=True)
                title = url_tag.find('news:title').get_text(strip=True)
                published_date = url_tag.find('news:publication_date').get_text(strip=True)
                upload_date = datetime.now().strftime('%Y-%m-%d %H:%M')
                image_url = url_tag.find('image:loc').get_text(strip=True)
                formatted_date, is_within_24_hours = smart_datetime_format_and_check(published_date)
                if is_within_24_hours:
                    the_news.append({
                        'title': title,
                        'published_date': formatted_date,
                        'source_url': source_url,
                        'upload_date': upload_date,
                        'image_url': image_url,
                        'category': 'english_news'
                    })
            except:
                pass
    except:
        pass

    return the_news





def scrape_english_news():
    news_english_urls = {
        "middleeastmonitor":"https://www.middleeastmonitor.com/news-sitemap.xml",
        "businessStandard":"https://apibs.business-standard.com/article/list?categoryCreationId=221&page=0&limit=100&offset=0",
        "thehindu":"https://www.thehindu.com/sitemap/googlenews/all/all.xml",
        "telegraph":'https://www.telegraph.co.uk/custom/daily-news/sitemap.xml',
        "theguardian":"https://www.theguardian.com/sitemaps/news.xml",
        "cnn":"https://edition.cnn.com/sitemap/news.xml"
    }

    # https://www.tbsnews.net/googlenews.xml
    # https://www.dhakatribune.com/news-sitemap.xml
    # https://www.thedailystar.net/googlenews.xml

    english_news = []

    for key, url in news_english_urls.items():
        if key == "middleeastmonitor":
            english_news.extend(extract_news_from_middleeastmonitor(url))
        elif key == "businessStandard":
            english_news.extend(extract_news_from_businessStandard(url))
        else:
            english_news.extend(extract_news_from_sitemap(url))

    return english_news



def scrape_all():
    all_news = []
    all_news.extend(scrape_bangla_news())
    all_news.extend(scrape_english_news())
    # print(f"Scraped {len(all_news)} news articles.")
    msg = upload_news(all_news)
    return msg

# if __name__ == "__main__":
#     all_news = []
#     all_news.extend(scrape_bangla_news())
#     all_news.extend(scrape_english_news())
#     # print(f"Scraped {len(all_news)} news articles.")
#     upload_news(all_news)
