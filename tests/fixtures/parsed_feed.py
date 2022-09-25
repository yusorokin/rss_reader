parsed_feed = """{
    "feed": "News, Politics, Opinion, Commentary, and Analysis",
    "url": "http://www.newyorker.com/feed/news",
    "items": [
        {
            "title": "The Queen’s Funeral Went Off Without a Hitch",
            "date": "Mon, 19 Sep 2022 20:49:19 +0600",
            "link": "https://www.newyorker.com/news/letter-from-the-uk/the-queens-funeral-went-off-without-a-hitch",
            "summary": "[Image 2: The Queen’s Funeral Went Off Without a Hitch][2]\nIt was an unprecedented and unrepeatable event, the definitive end of a life of service.",
            "article_content": "",
            "links": [
                {
                    "id": 1,
                    "src": "https://www.newyorker.com/news/letter-from-the-uk/the-queens-funeral-went-off-without-a-hitch",
                    "type": "link"
                },
                {
                    "id": 2,
                    "src": "https://media.newyorker.com/photos/6328959286debd54e201411a/master/pass/mead-funeral.jpg",
                    "type": "image"
                }
            ]
        }
    ]
}
"""

expected_output = """#############################################################
#                                                           #
#  Feed: News, Politics, Opinion, Commentary, and Analysis  #
#  http://www.newyorker.com/feed/news                       #
#                                                           #
#############################################################

==============================

Title: The Queen’s Funeral Went Off Without a Hitch
Date: Mon, 19 Sep 2022 20:49:19 +0600
Link: https://www.newyorker.com/news/letter-from-the-uk/the-queens-funeral-went-off-without-a-hitch

[Image 2: The Queen’s Funeral Went Off Without a Hitch][2]
It was an unprecedented and unrepeatable event, the definitive end of a life of service.

------------------------------
Links:
[1]: https://www.newyorker.com/news/letter-from-the-uk/the-queens-funeral-went-off-without-a-hitch (link)
[2]: https://media.newyorker.com/photos/6328959286debd54e201411a/master/pass/mead-funeral.jpg (image)"""
