import asyncio
from playwright.async_api import async_playwright
import json
import os
import requests

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

            tekst = await link.inner_text()
            href = await link.get_attribute("href")

            if (
                tekst
                and href
                and SOGEORD in tekst.upper()
            ):

                if href.startswith("/"):
                    href = "https://hea.dk" + href

                boliger.append(
                    {
                        "navn": tekst.strip(),
                        "link": href.strip(),
                    }
                )

        await browser.close()

    return boliger


def hent_gamle():

    if not os.path.exists(FIL):
        return []

    with open(FIL, "r", encoding="utf-8") as f:
        return json.load(f)


def gem(gamle):

    with open(FIL, "w", encoding="utf-8") as f:
        json.dump(
            gamle,
            f,
            ensure_ascii=False,
            indent=2,
        )


def send_telegram(besked):

    url = (
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    )

    requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": besked,
        },
        timeout=30,
    )


async def main():

    gamle = hent_gamle()

    gamle_links = {
        bolig["link"]
        for bolig in gamle
    }

    fundet = await hent_boliger()

    nye = []

    for bolig in fundet:

        if bolig["link"] not in gamle_links:

            print("Ny annonce:", bolig["link"])

            nye.append(bolig)

            gamle.append(bolig)

            gamle_links.add(bolig["link"])

        else:

            print("Annonce allerede kendt:", bolig["link"])

    if nye:

        besked = "🚨 NYT HEA OPSLAG PÅ ENGDIGET\n\n"

        for bolig in nye:

            besked += f"📍 {bolig['navn']}\n\n"
            besked += f"🔗 {bolig['link']}\n\n"

        send_telegram(besked)

    gem(gamle)


if __name__ == "__main__":
    asyncio.run(main())
