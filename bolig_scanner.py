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

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        await page.goto(
            HEA_URL,
            wait_until="networkidle",
            timeout=60000
        )

        links = await page.locator("a").all()

        for link in links:

            tekst = await link.inner_text()

            href = await link.get_attribute(
                "href"
            )

            if (
                tekst
                and SOGEORD in tekst.upper()
            ):

                boliger.append(
                    {
                        "navn": tekst.strip(),
                        "link": href
                    }
                )

        await browser.close()

    return boliger


def hent_gamle():

    if not os.path.exists(FIL):

        return []

    with open(
        FIL,
        "r"
    ) as f:

        return json.load(f)



def gem(gamle):

    with open(
        FIL,
        "w"
    ) as f:

        json.dump(
            gamle,
            f,
            indent=2
        )



def send_telegram(besked):

    url = (
        "https://api.telegram.org/"
        f"bot{TELEGRAM_TOKEN}/sendMessage"
    )

    requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": besked
        }
    )



async def main():

    gamle = hent_gamle()

    fundet = await hent_boliger()

    nye = []


    for bolig in fundet:

        if bolig not in gamle:

            nye.append(
                bolig
            )


    if nye:

        besked = (
            "🚨 NYT HEA OPSLAG PÅ ENGDIGET\n\n"
        )


        for bolig in nye:

            linjer = bolig["navn"].split("\n")

            besked += (
                "📍 "
                + linjer[0]
                + "\n\n"
            )

            besked += (
                bolig["navn"]
                + "\n\n"
            )

            besked += (
                "🔗 Link:\n"
                + str(bolig["link"])
                + "\n\n"
            )

            gamle.append(
                bolig
            )


        send_telegram(
            besked
        )


    gem(
        gamle
    )



if __name__ == "__main__":

    asyncio.run(
        main()
    )
