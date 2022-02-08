import time

base_valid_data = {
    "bozo": False,
    "status": 200,
    "etag": "0jy9tuaV/9Y3bTOOSmdmqIjGpRc",
    "href": "https://feeds.feedburner.com/tweakers/mixed",
    "updated_parsed": time.struct_time((2022, 2, 8, 1, 20, 16, 1, 39, 0)),
    "feed": {
        "image": {"href": "https://tweakers.net/g/if/logo.gif"},
        "subtitle": "Tweakers is de grootste hardwaresite en techcommunity "
        "van Nederland.",
        "title": "Tweakers Mixed RSS Feed",
    },
    "entries": [
        {
            "link": "https://tweakers.net/"
            "nieuws/192970/steam-deck-haalt-36-160fps-en-1-komma-5-6-uur-accuduur-in-eerste-benchmarks.html",
            "title": "Steam Deck haalt 36-160fps en 1,5-6 uur accuduur in "
            "eerste benchmarks",
            "published_parsed": time.struct_time((2022, 2, 7, 20, 29, 47, 0, 38, 0)),
            "summary": "Enkele YouTubers hebben de eerste benchmarks van de "
            "Steam Deck gepubliceerd. Daaruit blijkt dat de "
            "handheld-pc de meegeleverde games met tenminste "
            "36fps kan afspelen. De beloofde accuduur van tussen "
            "de 2 en 8 uur blijkt onder normale omstandigheden "
            "ook relatief accuraat.",
        },
        {
            "link": "https://tweakers.net/downloads/59260/bulk-crap-uninstaller-52.html",
            "title": "Bulk Crap Uninstaller 5.2",
            "published_parsed": time.struct_time((2022, 2, 7, 19, 31, 54, 0, 38, 0)),
            "summary": "Klocman Software heeft versie 5.2 van Bulk Crap "
            "Uninstaller uitgebracht. Met dit programma, dat "
            "onder een opensourcelicentie wordt uitgebracht, "
            "kunnen in een keer diverse programma's en Windows "
            "Store-apps van de computer worden verwijderd. Het "
            "voert eerst de standaard verwijderprocedure uit en "
            "scant vervolgens de computer op overgebleven "
            "snelkoppelingen en registersleutels om die ook nog "
            "te verwijderen. Na afloop kunnen eventueel ook nog "
            "externe programma's zoals CCleaner worden gestart. "
            "Ten slotte bevat het een start-upmanager, waarmee "
            "programma's die met Windows meestarten uitgeschakeld "
            "kunnen worden. De release notes voor deze uitgave "
            "kunnen hieronder worden gevonden. Changes in Bulk "
            "Crap Uninstaller version 5.2:",
        },
        {
            "link": "https://tweakers.net/"
            "geek/192904/gerucht-disney+-serie-gebaseerd-op-obi-wan-kenobi-komt-in-mei-uit.html",
            "title": "Gerucht: Disney+-serie gebaseerd op Obi-Wan Kenobi "
            "komt in mei uit",
            "published_parsed": time.struct_time((2022, 2, 5, 12, 40, 40, 5, 36, 0)),
            "summary": "De Disney+-serie die zich focust op Star "
            "Wars-personage Obi-Wan Kenobi komt mogelijk in mei "
            "van dit jaar uit. Een Disney-topman tweette de "
            "bekendmaking, maar verwijderde die weer snel. Andere "
            "bronnen bevestigen de datum echter wel.",
        },
    ],
}

base_not_valid_data = {
    "bozo": True,
    "bozo_exception": "NonXMLContentType('text/html; charset=ISO-8859-2 is not an XML media type')",
    "status": 404,
    "entries": [],
    "feed": {},
    "href": "http://rss.gazeta.pl/pub/rss/wiadomosci.htm",
    "updated_parsed": time.struct_time((2022, 2, 8, 1, 7, 18, 1, 39, 0)),
}

valid_parsed_feed_content = base_valid_data.copy()

not_valid_feed = base_not_valid_data.copy()

feed_content_not_changed_data = {
    "bozo": False,
    "status": 304,
    "entries": [],
    "feed": {},
    "href": "http://rss.gazeta.pl/pub/rss/wiadomosci.htm",
    "updated_parsed": time.struct_time((2022, 2, 8, 1, 7, 18, 1, 39, 0)),
}

feed_is_gone_data = not_valid_feed.copy()
feed_is_gone_data.update(
    {"status": 410, "href": "https://feeds.feedburner.com/tweakers/mixed/gone/"}
)

feed_url_changed_with_valid_data = base_valid_data.copy()
feed_url_changed_with_valid_data.update(
    {"status": 301, "href": "https://feeds.feedburner.com/tweakers/mixed/changed/"}
)

feed_url_changed_without_valid_data = base_not_valid_data.copy()
feed_url_changed_without_valid_data.update(
    {"status": 301, "href": "https://feeds.feedburner.com/tweakers/mixed/changed/"}
)
