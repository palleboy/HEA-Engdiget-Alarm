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
    svar = requests.get(HEA_URL)
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


def hent_gamle():

    with open(FIL, "r") as f:
        return json.load(f)


def gem(gamle):

    with open(FIL, "w") as f:
        json.dump(gamle, f, indent=2)


def send_telegram(besked):

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_TOKEN}/sendMessage"
    )

    requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": besked
        }
    )


def main():

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
