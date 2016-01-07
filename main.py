#!/usr/bin/env python3
import TelegramAPI
import requests
import sys
import os
import time

session = requests.Session()
session.headers["User-Agent"] = ("DerpibooruImageBot for Telegram (Python {version.major}.{version.minor}.{version.micro},"
                                 " using Requests)").format(version=sys.version_info)
if "TELEGRAMKEY" not in os.environ:
    print("Set $TELEGRAMKEY to the Telegram Bot API key, and then start the bot.")
    exit(1)
bot = TelegramAPI.TelegramBot(os.environ["TELEGRAMKEY"])


@bot.inline_request_hook
def do_query(query):
    if len(query) < 2 or query[-1:] == " " or query[-1:] == ",":
        return []
    response = session.get("https://derpiboo.ru/search.json", params={"q": query.replace(" ", "+")}).json()
    output = []
    for image in response["search"]:
        print("   Adding {}.".format(image["id_number"]))
        this_img = {
            "type": "photo",
            "id": "{}".format(image["id_number"]),
            "caption": "https://derpiboo.ru/{} (query used was '{}')".format(
                    image["id_number"], query),
            "photo_url": "https:" + image["image"],
            "photo_width": image["width"],
            "photo_height": image["height"],
            "thumb_url": "https:" + image["representations"]["thumb"]
        }
        if len(output) > 49:
            break
        output.append(this_img)
    return output

while True:
    bot.poll_once()
    time.sleep(1)
