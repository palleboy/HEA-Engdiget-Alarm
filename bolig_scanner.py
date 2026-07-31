import asyncio
from playwright.async_api import async_playwright
import json
import os
import requests


HEA_URL = "https://hea.dk/lejemaal/"

SOGEORD = "engdiget"

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

        kort = await page.locator("a").all()

        for element in kort:

            tekst = await element.inner_text()

            if (
                tekst
                and "ENGDIGET" in tekst.upper()
            ):

        

                link = await element.get_attribute(
                    "href"
                )

                boliger.append(
                    {
                        "navn": tekst.strip(),
                        "link": link
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

        if bolig["link"] not in gamle:

            nye.append(
                bolig
            )


    if nye:

        besked = (
            "🏠 NY LEJLIGHED PÅ ENGDIGET!\n\n"
        )


        for bolig in nye:

            besked += (
                "📍 "
                + bolig["navn"]
                + "\n"
            )

            besked += (
                "🔗 "
                + str(bolig["link"])
                + "\n\n"
            )


            gamle.append(
                bolig["link"]
            )


        send_telegram(
            besked
        )


    else:

        print(
            "Ingen nye Engdiget boliger fundet"
        )


    gem(
        gamle
    )



if __name__ == "__main__":

    asyncio.run(
        main()
            )
