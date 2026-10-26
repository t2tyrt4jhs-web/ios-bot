import os
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = "8958998286:AAGSrF5OHg1eEJKIiSpDbkLJzTkBRm1rtdQ"
CHAT_ID = "8543771153"
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

URL_OLX = "https://www.olx.pl/elektronika/telefony/smartfony/iphone/?search%5Bfilter_float_price%3Ato%5D=2000&search%5Bsort_by%5D=created_at%3Adesc"

WYSYLANE_FILE = "wyslane.txt"

def wczytaj_wyslane():
    if os.path.exists(WYSYLANE_FILE):
        with open(WYSYLANE_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def zapisz_wyslane(wyslane):
    with open(WYSYLANE_FILE, "w", encoding="utf-8") as f:
        for link in wyslane:
            f.write(link + "\n")

def wyslij_telegram(tekst):
    try:
        requests.post(
            TELEGRAM_URL, 
            json={"chat_id": CHAT_ID, "text": tekst, "parse_mode": "Markdown"}, 
            timeout=10
        )
    except Exception as e:
        print(f"Błąd Telegrama: {e}")

def sprawdz():
    wyslane = wczytaj_wyslane()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(URL_OLX, headers=headers, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            oferty = soup.find_all('div', {'data-testid': 'l-card'})
            
            zmiana = False
            for o in oferty:
                lt = o.find('a')
                if not lt or 'href' not in lt.attrs:
                    continue
                
                link = lt['href']
                if link.startswith('/'):
                    link = "https://www.olx.pl" + link
                    
                if link in wyslane:
                    continue
                    
                t_elem = o.find('h6')
                tytul = t_elem.text.strip() if t_elem else "Brak tytułu"
                
                c_elem = o.find('p', {'data-testid': 'ad-price'})
                cena = c_elem.text.strip() if c_elem else "Brak ceny"
                
                wyslane.add(link)
                zmiana = True
                wyslij_telegram(f"🚨 *NOWA OFERTA OLX!* 🚨\n\n📌 *{tytul}*\n💰 *Cena:* {cena}\n\n🔗 [OTWÓRZ OGŁOSZENIE]({link})")
            
            if zmiana:
                zapisz_wyslane(wyslane)
        else:
            print(f"Błąd pobierania OLX: {r.status_code}")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")

if __name__ == "__main__":
    sprawdz()
