from hashlib import new
import json
import unittest
from io import StringIO
from unittest.mock import patch, Mock
import os
import sys
from rss_reader import one_shot
import feedparser
from tests.fixtures import article_parser
from tests.fixtures import parsed_feed

def handle_exceptions_with(excepthook, target, /, *args, **kwargs):
    try:
        target(*args, **kwargs)
    except:
        excepthook(*sys.exc_info())
        raise

class TestExceptionHandler(unittest.TestCase):
    def test_should_print_traceback_only_if_set(self):
        """ Check logger output with DEBUG flag and without"""
        self.assertIs(sys.excepthook, one_shot.exception_handler)

        os.environ["DEBUG"] = "true"
        with self.assertLogs(one_shot.logger, level='ERROR') as logs:
            try:
                int("a")
            except ValueError:
                one_shot.exception_handler(*sys.exc_info())
        self.assertEqual(len(logs.output), 1)
        self.assertRegex(logs.output[0], r"ERROR.*ValueError")
        self.assertRegex(logs.output[0], r"Traceback \(most recent call last\)")

        os.environ["DEBUG"] = ""
        with self.assertLogs(one_shot.logger, level='ERROR') as logs:
            try:
                int("a")
            except ValueError:
                one_shot.exception_handler(*sys.exc_info())
        self.assertEqual(len(logs.output), 1)
        self.assertRegex(logs.output[0], r"ERROR.*ValueError")

class TestGetImageAttrs(unittest.TestCase):
    def test_should_return_parsed_attrs(self):
        img_obj = one_shot.BeautifulSoup(
            """
            <img alt=\"Some <em>text</em>\"
            data-src=\"https://www.example.com/img/1.png\"/>
            """,
            "html5lib")

        self.assertDictEqual(
            one_shot.get_image_attrs(img_obj.img),
            {"alt": "Some text", "src": "https://www.example.com/img/1.png"})

        img_obj = one_shot.BeautifulSoup(
            """
            <img alt=\"Some <em>text</em>\"
            src=\"https://www.example.com/img/1.png\"/>
            """,
            "html5lib")

        self.assertDictEqual(
            one_shot.get_image_attrs(img_obj.img),
            {"alt": "Some text", "src": "https://www.example.com/img/1.png"})

        img_obj = one_shot.BeautifulSoup(
            """
            <img
            src=\"https://www.example.com/img/1.png\"/>
            """,
            "html5lib")

        self.assertDictEqual(
            one_shot.get_image_attrs(img_obj.img),
            {"alt": "", "src": "https://www.example.com/img/1.png"})

    def test_should_raise_on_missing_src(self):
        img_obj = one_shot.BeautifulSoup(
            """
            <img alt=\"Some <em>text</em>\"/>
            """,
            "html5lib")

        with self.assertRaises(one_shot.ElementAttributeNotFound):
            one_shot.get_image_attrs(img_obj.img)

class TestParseArticle(unittest.TestCase):
    @patch('rss_reader.one_shot.links', [])
    @patch('rss_reader.one_shot.get', Mock())
    def test_should_return_parsed_article(self):
        one_shot.get("www.example.com").content = article_parser.article_web_page
        parsed_article = one_shot.parse_article("www.example.com")

        self.assertDictEqual(one_shot.links[0],
            {'id': 1, 'src': 'https://www.example.com/1.png', 'type': 'image'})
        self.assertDictEqual(one_shot.links[1],
            {'id': 2, 'src': 'https://www.example.com/2.png', 'type': 'image'})
        self.assertDictEqual(one_shot.links[2],
            {'id': 3, 'src': 'https://twitter.com/tweet/1', 'type': 'tweet'})
        self.assertRegex(parsed_article, r"[Image 1: Image description][1]")
        self.assertRegex(parsed_article, r"[Image 2: Image description][2]")
        self.assertRegex(parsed_article, r"[Tweet 3][3]")
        self.assertRegex(parsed_article, r"Article header")
        self.assertRegex(parsed_article, r"Some text here")
        self.assertRegex(parsed_article, r"Some more text here")

    @patch('rss_reader.one_shot.links', [])
    @patch('rss_reader.one_shot.get', Mock())
    def test_should_raise_on_missing_title(self):
        one_shot.get("www.example.com").content = article_parser.article_web_page_no_title

        with self.assertRaises(one_shot.ElementNotFound):
            parsed_article = one_shot.parse_article("www.example.com")

    @patch('rss_reader.one_shot.links', [])
    @patch('rss_reader.one_shot.get', Mock())
    def test_should_raise_on_missing_body(self):
        one_shot.get("www.example.com").content = article_parser.article_web_page_no_body

        with self.assertRaises(one_shot.ElementNotFound):
            parsed_article = one_shot.parse_article("www.example.com")

class TestPrintInFrame(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_should_print_framed_args(self, mocked_stdout):
        result = [
            "###########",
            "#         #",
            "#  text1  #",
            "#  text2  #",
            "#         #",
            "###########"
        ]
        one_shot.print_in_frame("text1", "text2")
        self.assertListEqual(mocked_stdout.getvalue().strip().split("\n"), result)

class TestPrintResult(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_should_print_proper_result(self, mocked_stdout):
        feed = json.loads(parsed_feed.parsed_feed, strict=False)
        one_shot.print_result(feed)
        output = mocked_stdout.getvalue().strip()

        self.maxDiff = None
        self.assertEqual(output, parsed_feed.expected_output)

class TestReadRss(unittest.TestCase):
    def setUp(self):
        with open("tests/fixtures/feed.xml", "r") as file:
            self.parsed_feed = feedparser.parse(file.read())
        with open("tests/fixtures/feed_parse_expected_result.json", "r") as file:
            self.expected_json = json.loads(file.read())

        with open("tests/fixtures/invalid_feed.xml", "r") as file:
            self.parsed_invalid_feed = feedparser.parse(file.read())

    @patch("sys.stdout", new_callable=StringIO)
    @patch("rss_reader.one_shot.feedparser")
    def test_should_print_proper_result(self, mocked_parser, mocked_stdout):
        mocked_parser.parse.return_value = self.parsed_feed
        one_shot.read_rss('http://www.example.com', limit=1, to_json=True)
        result = json.loads(mocked_stdout.getvalue().strip())

        self.assertDictEqual(result, self.expected_json)
        self.assertEqual(len(result["items"]), 1)

    @patch("rss_reader.one_shot.feedparser")
    def test_should_raise_on_invalid_xml(self, mocked_parser):
        mocked_parser.parse.return_value = self.parsed_invalid_feed

        with self.assertLogs(one_shot.logger, level='ERROR') as logs:
            with self.assertRaises(one_shot.FeedparserFeedFormattingError):
                try:
                    one_shot.read_rss('http://www.example.com', limit=1, to_json=True)
                except one_shot.FeedparserFeedFormattingError:
                    one_shot.exception_handler(*sys.exc_info())
                    raise one_shot.FeedparserFeedFormattingError

        self.assertRegex(logs.output[0], r"Unable to parse provided URL")


if __name__ == '__main__':
    unittest.main()
