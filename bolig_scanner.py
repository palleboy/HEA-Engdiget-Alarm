import requests
from bs4 import BeautifulSoup
import json
import os

HEA_URL = "https://hea.dk/lejemaal/"

SOGEORD = "engdiget"

FIL = "sete_boliger.json"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def hent_boliger():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "da-DK,da;q=0.9,en;q=0.8"
    }

    svar = requests.get(
        HEA_URL,
        headers=headers,
        timeout=30
    )

    svar.raise_for_status()

    soup = BeautifulSoup(svar.text, "html.parser")

    boliger = []

    for link in soup.find_all("a", href=True):

        tekst = link.get_text(" ", strip=True)

        if SOGEORD.lower() in tekst.lower():

            boliger.append({
                "navn": tekst,
                "link": link["href"]
            })

    return boliger

    gamle = hent_gamle()

    fundet = hent_boliger()

    nye = []

    for bolig in fundet:

        if bolig["link"] not in gamle:

            nye.append(bolig)


    if nye:

        besked = "🏠 NY LEJLIGHED PÅ ENGDIGET!\n\n"

        for bolig in nye:

            besked += (
                bolig["navn"]
                + "\n"
                + bolig["link"]
                + "\n\n"
            )

            gamle.append(bolig["link"])


        send_telegram(besked)

        gem(gamle)


    else:

        print("Ingen nye lejligheder")


if __name__ == "__main__":
    main()
