import asyncio
import json
import os

import requests
from playwright.async_api import async_playwright

HEA_URL = "https://hea.dk/lejemaal/"
SOGEORD = "ENGDIGET"
FIL = "sete_boliger.json"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


async def hent_boliger():
    boliger = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.goto(
            HEA_URL,
            wait_until="networkidle",
            timeout=60000,
        )

        links = await page.locator("a").all()

        for link in links:

            tekst = (await link.inner_text()).strip()
            href = await link.get_attribute("href")

            if not tekst or not href:
                continue

            if SOGEORD not in tekst.upper():
                continue

            if href.startswith("/"):
                href = "https://hea.dk" + href

            boliger.append(
                {
                    "navn": tekst,
                    "link": href.strip(),
                }
            )

        await browser.close()

    return boliger


def hent_gamle_links():

    if not os.path.exists(FIL):
        return set()

    with open(FIL, "r", encoding="utf-8") as f:
        data = json.load(f)

    return set(data)


def gem_links(links):

    with open(FIL, "w", encoding="utf-8") as f:
        json.dump(
            sorted(list(links)),
            f,
            ensure_ascii=False,
            indent=2,
        )


def send_telegram(besked):

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": besked,
        },
        timeout=30,
    )


async def main():

    gamle_links = hent_gamle_links()

    fundet = await hent_boliger()

    nye = []

    for bolig in fundet:

        if bolig["link"] not in gamle_links:

            print(f"NY: {bolig['link']}")

            gamle_links.add(bolig["link"])

            nye.append(bolig)

        else:

            print(f"Kendt: {bolig['link']}")

    if nye:

        besked = "🚨 NYT HEA OPSLAG PÅ ENGDIGET\n\n"

        for bolig in nye:

            besked += f"📍 {bolig['navn']}\n\n"
            besked += f"🔗 {bolig['link']}\n\n"

        send_telegram(besked)

    gem_links(gamle_links)


if __name__ == "__main__":
    asyncio.run(main())
