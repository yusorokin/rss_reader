"""
Reads RSS feed.

Reads, parses and outputs parsed RSS feed from given URL.
Optionally outputs the result as JSON to stdout.

Usage:

    read_rss(rss_url, limit=3, to_json=False, verbose=False):

"""
from urllib.parse import urlparse
import feedparser
from requests import get
from bs4 import BeautifulSoup
import time
import json
import logging
from logging import StreamHandler, Formatter
import sys
import os
from unicodedata import normalize

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(handler)


class FeedparserFeedFormattingError(Exception):
    pass

class ElementAttributeNotFound(Exception):
    pass

class ElementNotFound(Exception):
    pass


def exception_handler(
        exception_type,
        exception,
        traceback):
    """
    Exception hook that disables traceback
    unless DEBUG env var will become 'true'
    and uses logger for output.
    """
    # print(f'>>>>> {os.getenv("DEBUG")} <<<<<')
    # TODO: remove ' or 1 == 2' after debug is finished
    if os.getenv("DEBUG") == "true":
        logger.error(f"{exception_type.__name__}: {exception}", exc_info=(exception_type, exception, traceback))
    else:
        logger.error(f"{exception_type.__name__}: {exception}")

def get_image_attrs(img):
    """
    Gets 'src' and 'alt' attributes as dict from given 'img' element.
    Also parses 'alt' as is could be also contain tags in text.
    """
    if img.has_attr('alt'):
        alt = BeautifulSoup(img.get('alt'), 'html5lib').get_text()
    else:
        alt = ""
    if img.has_attr('src'):
        src = img.get('src')
    elif img.has_attr('data-src'):
        src = img.get('data-src')
    else:
        raise ElementAttributeNotFound("Required img attribute 'src' or 'data-src not found'")
    return {"alt": alt, "src": src}

def parse_article(url):
    """
    Parses given article html page.

    Searches article body, title, title image
    and images and tweets in the article body itself.
    Appends image links into existing 'links' list variable.
    Works only for Yahhoo news only.

    Input parameters:
        url - URL to the article that needs to be parsed

    Returns:
        Formatted article body as a string

    """

    parsed_text = ""
    article = get(url).content
    soup1 = BeautifulSoup(article, 'html5lib')

    cover = soup1.find('figure', class_='caas-cover')
    if cover:
        cover_img = cover.find("img")
        if cover_img:
            cover_img_attrs = get_image_attrs(cover_img)
            links.append({
                        "id": len(links) + 1,
                        "src": cover_img_attrs['src'],
                        "type": "image"
                        })
            parsed_text += (f"[Image {len(links)}: "
                            + f"{cover_img_attrs['alt']}][{len(links)}]\n")
    try:
        article_title = soup1.find('header',
                                    class_='caas-title-wrapper').get_text()
    except AttributeError:
        raise ElementNotFound("Expected 'header' element wasn't found during article parsing")
    parsed_text += article_title + "\n\n"

    article_body = soup1.find('div', class_='caas-body')
    if article_body == None:
        raise ElementNotFound("Expected 'div' element wasn't found during article parsing")
    for el in article_body.children:
        if el.name == "figure":
            img = el.find("img")
            if img:
                img_attrs = get_image_attrs(img)
                links.append({
                            "id": len(links) + 1,
                            "src": img_attrs['src'],
                            "type": "image"
                            })
                parsed_text += (f"[Image {len(links)}: "
                                + f"{img_attrs['alt']}][{len(links)}]\n")
        elif el.name == "div" and "twitter-tweet-wrapper" in el.get("class"):
            tweet = el.find("a")
            if tweet:
                links.append({
                            "id": len(links) + 1,
                            "src": tweet.get("href"),
                            "type": "tweet"
                            })
                parsed_text += (f"[Tweet {len(links)}][{len(links)}]\n")
        else:
            parsed_text += el.get_text(separator=' ', strip=True) + "\n"
    return parsed_text


def print_in_frame(*args):
    """
    Gets one or more string params and prints them
    surrounded by frame made of symbols.

    Example:

        ###########
        #         #
        #  text1  #
        #  text2  #
        #         #
        ###########
    """
    max_len = 0
    for string in args:
        string = str(string)
        if max_len < len(string):
            max_len = len(string)
    print('#'*(max_len + 6))
    print('#' + ' '*(max_len + 4) + '#')
    for string in args:
        string = str(string)
        print('#  ' + f"{string}" + ' '*(max_len - len(string)) + '  #')
    print('#' + ' '*(max_len + 4) + '#')
    print('#'*(max_len + 6))
    print()


def print_result(parsed_rss):
    """
    Prints RSS reader result to stdout.

    Input parameters:
        parsed_rss (dict) - the result of reading RSS feed
    """
    print_in_frame(f"Feed: {parsed_rss['feed']}", parsed_rss['url'])

    for item in parsed_rss['items']:
        print("="*30 + "\n")
        print(f"Title: {item['title']}")
        print(f"Date: {item['date']}")
        print(f"Link: {item['link']}")
        print()
        if item['links'][1] and item['links'][0]['type'] == 'image':
            print(f"[Image {item['links'][0]['id']}: "
                  + f"{item['title']}][{item['links'][0]['id']}]")
        if len(item['summary']) > 0:
            print(item['summary'])
        print()
        print("-"*30)
        if len(item['article_content']) > 0:
            print(item['article_content'])
            print()
        print("Links:")
        for link in item['links']:
            print(f"[{link['id']}]: {link['src']} ({link['type']})")
        print()
        pass


def read_rss(rss_url, limit=3, to_json=False, verbose=False):
    """
    Reads and parses RSS.

    This function reads RSS feed by provided URL, parses it
    and outputs in given format.

    Input parameters:
        rss_url - RSS feed URL to be read.
        limit - The amount of entries to be read from the feed.
        to_json - JSON output flag. Prints JSON if 'True'.
        verbose - Prints additional information if 'True'.
    """
    if verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.ERROR)
    logger.info("Start reading")

    rss_url_parsed = urlparse(rss_url)
    if rss_url_parsed.netloc + rss_url_parsed.path == "news.yahoo.com/rss/":
        parse_article_page = True
    else:
        parse_article_page = False

    logger.info(f"Parsing article web-page set to {parse_article_page}")
    parsed_feed = feedparser.parse(rss_url)
    if parsed_feed.bozo > 0:
        raise FeedparserFeedFormattingError(
            "Unable to parse provided URL " +
            f"({parsed_feed.bozo_exception.getMessage()}:" +
            f"{parsed_feed.bozo_exception.getLineNumber()})")

    feed["feed"] = parsed_feed.feed.title
    feed["url"] = rss_url
    feed["items"] = []

    entries = parsed_feed.entries
    limit = limit if limit <= len(entries) else len(entries)
    logger.info(f"Start reading {limit} entries from feed")
    for k in range(limit):
        logger.info(f"Entry {k + 1} start")
        links.clear()
        summary = ""
        article_content = ""
        title = entries[k]['title']
        date = time.strftime('%a, %-d %b %Y %H:%M:%S %z',
                             entries[k]['published_parsed'])
        links.append({
                    "id": len(links) + 1,
                    "src": entries[k]['link'],
                    "type": "link"})
        link = entries[k]['link']
        if "media_content" in entries[k] \
                and len(entries[k]['media_content']) > 0 \
                and entries[k]['media_content'][0] != {}:
            for media in entries[k]['media_content']:
                links.append({
                            "id": len(links) + 1,
                            "src": media["url"],
                            "type": "image"
                            })
                summary += (f"[Image {len(links)}: "
                            + f"{entries[k]['title']}][{len(links)}]")
        if "media_thumbnail" in entries[k] \
                and len(entries[k]['media_thumbnail']) > 0 \
                and entries[k]['media_thumbnail'][0] != {}:
            if len(summary) > 0:
                summary += "\n"
            for media in entries[k]['media_thumbnail']:
                links.append({
                            "id": len(links) + 1,
                            "src": media["url"],
                            "type": "image"
                            })
                summary += (f"[Image {len(links)}: "
                            + f"{entries[k]['title']}][{len(links)}]")
        if "summary" in entries[k]:
            summary += f"\n{entries[k]['summary']}"
        else:
            summary += "\nNo summary"

        if parse_article_page:
            article_content = parse_article(entries[k]['link'])

        feed["items"].append({
            "title": title,
            "date": date,
            "link": link,
            "summary": summary,
            "article_content": article_content,
            "links": links.copy()
        })
        logger.info(f"Entry {k + 1} end")

    if to_json:
        logger.info(f"Printing JSON")
        print(json.dumps(feed, sort_keys=False, indent=4, ensure_ascii=False))
    else:
        logger.info(f"Printing formatted output")
        print_result(normalize("NFKD", feed))

sys.excepthook = exception_handler

feed = {}
links = []


if __name__ == "__main__":
    # read_rss('https://news.yahoo.com/rss/', limit=3, verbose=False)
    read_rss('http://www.newyorker.com/feed/news', limit=3, to_json=True)
    # read_rss('http://ya.ru')
    # print(parse_article("https://news.yahoo.com/dark-brandon-strikes-again-joe-081130226.html"))
    # print(links)
