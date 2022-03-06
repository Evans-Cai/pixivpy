#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ssl
import sys
from datetime import datetime, timedelta

from pixivpy3 import AppPixivAPI

sys.dont_write_bytecode = True

# disable SSL verify
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

_REQUESTS_KWARGS = {
    "proxies": {
        "https": "http://127.0.0.1:1087",
    },
}

# get your refresh_token, and replace _REFRESH_TOKEN
#  https://github.com/upbit/pixivpy/issues/158#issuecomment-778919084
_REFRESH_TOKEN = "0zeYA-PllRYp1tfrsq_w3vHGU1rPy237JMf5oDt73c4"


def main():
    api = AppPixivAPI(**_REQUESTS_KWARGS)
    # aapi.set_additional_headers({'Accept-Language':'en-US'})
    api.set_accept_language("en-us")  # zh-cn
    api.auth(refresh_token=_REFRESH_TOKEN)

    target_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    json_result = api.illust_ranking("day", date=target_date)

    print(
        "Printing image titles and tags with English tag translations present when available"
    )
    print_results(json_result.illusts[:3])

    next_qs = api.parse_qs(json_result.next_url)
    if next_qs is not None:
        print(">>> next page")
        json_result = api.illust_ranking(**next_qs)
        print_results(json_result.illusts[:3])


def print_results(illusts):
    for illust in illusts:
        print(
            'Illustration: "'
            + str(illust.title)
            + '"\nTags: '
            + str(illust.tags)
            + "\n"
        )


if __name__ == "__main__":
    main()
