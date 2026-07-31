import requests
from bs4 import BeautifulSoup
import json

HEA_URL = "https://hea.dk/lejemaal/"

SOGEORD = "engdiget"

FIL = "sete_boliger.json"


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


def gem(boliger):
    with open(FIL, "w") as f:
        json.dump(boliger, f, indent=2)


def main():

    gamle = hent_gamle()

    fundet = hent_boliger()

    nye = []

    for bolig in fundet:
        if bolig["link"] not in gamle:
            nye.append(bolig["link"])

    if nye:
        print("Nye lejligheder fundet:")
        for bolig in nye:
            print(bolig)

        gamle.extend(nye)
        gem(gamle)

    else:
        print("Ingen nye lejligheder")


if __name__ == "__main__":
    main()
