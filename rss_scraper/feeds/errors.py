class Error(Exception):
    pass


class FeedParsingError(Error):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class FeedIsGoneError(FeedParsingError):
    """
    Feed is gone permanently. We should stop polling the feed.
    Expected status code: 410

    Source: https://feedparser.readthedocs.io/en/latest/reference-status.html
    """

    pass


class FeedUrlChangedError(FeedParsingError):
    """
    Feed permanently redirected to a new URL. We should update the url at the feed DB instance.
    Expected status code: 301

    Source: https://feedparser.readthedocs.io/en/latest/reference-status.html
    """

    pass


class FeedContentNotChangedError(FeedParsingError):
    """
    When taking advantage of the ETag and Last-Modified headers, we expect receiving 304 status code
        meaning that there is no need to update feed or items DB info as there is no change since the last time.
    Expected status code: 304

    Source: https://feedparser.readthedocs.io/en/latest/http-etag.html#http-etag
    """

    pass


class FeedNotAvailableError(FeedParsingError):
    """
    The server returned non-well formed feed data.

    feedparser package response returns a `bozo` bool if its True it means that it couldn't parse valid XML from source.
    We can log the raised bozo_exception at such a case for further analysis.

    Source:
        - https://feedparser.readthedocs.io/en/latest/reference-bozo.html
        - https://feedparser.readthedocs.io/en/latest/reference-bozo_exception.html
    """

    pass
