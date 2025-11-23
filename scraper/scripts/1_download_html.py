#!/usr/bin/env python3
"""
STEP 1: Download HTML pages
Scarica le prime N pagine di sentenze CIVILE - QUINTA SEZIONE
Usa: settimanalmente per trovare nuove sentenze
"""

import os
import time
import argparse
import json
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def setup_driver(headless=True):
    """Configura e ritorna il driver Selenium"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def wait_for_page_load(driver, timeout=20):
    """Attende il caricamento della pagina"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dataset"))
        )
        time.sleep(0.5)  # Attesa aggiuntiva per JavaScript (ridotto per HTML)
        return True
    except TimeoutException:
        return False


def get_current_page_number(driver):
    """Ottiene il numero della pagina corrente"""
    try:
        title = driver.find_element(By.ID, "contentData").get_attribute("title")
        # Estrae da "pagina X di YYYY"
        page_num = int(title.split("pagina")[1].split("di")[0].strip())
        return page_num
    except Exception:
        return None


def check_for_captcha(driver):
    """Controlla se è apparso un CAPTCHA"""
    try:
        # Cerca elementi comuni di CAPTCHA
        if driver.find_elements(By.ID, "captcha") or \
           driver.find_elements(By.CLASS_NAME, "g-recaptcha") or \
           "captcha" in driver.page_source.lower():
            return True
        return False
    except Exception:
        return False


def get_page_sentence_ids(driver):
    """Estrae tutti gli ID delle sentenze dalla pagina corrente"""
    try:
        # Trova tutti gli span con data-arg="id"
        id_elements = driver.find_elements(By.CSS_SELECTOR, 'span[data-arg="id"]')
        ids = [elem.text.strip() for elem in id_elements if elem.text.strip()]
        return ids
    except Exception:
        return []


def load_latest_sentence_id(year=None):
    """Carica l'ultimo ID di sentenza dal JSON esistente"""
    try:
        if year:
            json_path = Path(f"metadata/metadata_cassazione_{year}.json")
        else:
            json_path = Path("metadata/metadata_cassazione.json")

        if not json_path.exists():
            return None

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            sentences = data.get('sentences', [])
            if sentences:
                # Il primo è l'ultimo (ordinamento inverso per ID)
                return sentences[0]['id']
    except Exception as e:
        print(f"⚠️  Errore caricamento ultimo ID: {e}")
    return None


def click_next_page(driver):
    """Clicca sul pulsante pagina successiva"""
    try:
        next_btn = driver.find_element(
            By.CSS_SELECTOR,
            'span.pager.pagerArrow[title="pagina successiva"]'
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", next_btn)
        return True
    except NoSuchElementException:
        return False


def save_page_html(driver, output_dir, timestamp):
    """Salva l'HTML della pagina corrente con timestamp"""
    try:
        page_num = get_current_page_number(driver)
        if not page_num:
            return False

        html_content = driver.page_source

        # Nome file con timestamp per tracciare quando è stato scaricato
        filename = f"page_{page_num:04d}_{timestamp}.html"
        filepath = output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✓ Salvata pagina {page_num}: {filename}")
        return True
    except Exception as e:
        print(f"✗ Errore salvataggio: {e}")
        return False


def download_html_pages(num_pages=10, output_dir="scraper/data/html", headless=True, year=None, stop_at_id=None, auto_stop=False):
    """
    Scarica le prime N pagine di sentenze CIVILE - QUINTA SEZIONE

    Args:
        num_pages: Numero massimo di pagine da scaricare (default: 10)
        output_dir: Directory dove salvare i file HTML
        headless: Esegui in modalità headless (default: True)
        year: Anno per filtrare le sentenze (opzionale)
        stop_at_id: ID sentenza dove fermarsi (stop incrementale)
        auto_stop: Se True, carica automaticamente l'ultimo ID dal JSON e si ferma lì
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Auto-stop: carica ultimo ID dal JSON
    if auto_stop and not stop_at_id:
        stop_at_id = load_latest_sentence_id(year)
        if stop_at_id:
            print(f"🔄 Modalità aggiornamento incrementale: stop at ID {stop_at_id}")

    print(f"🚀 Download HTML - Sentenze CIVILE QUINTA SEZIONE")
    print(f"📁 Output: {output_path.absolute()}")
    print(f"📄 Pagine massime: {num_pages}")
    if year:
        print(f"📅 Anno filtro: {year}")
    if stop_at_id:
        print(f"🛑 Stop at ID: {stop_at_id}")
    print(f"🕐 Timestamp: {timestamp}\n")

    driver = None
    downloaded = 0
    found_stop_id = False

    try:
        driver = setup_driver(headless)
        url = "https://www.italgiure.giustizia.it/sncass/"

        print(f"🌐 Caricamento {url}...")
        driver.get(url)

        if not wait_for_page_load(driver):
            print("✗ Errore caricamento pagina iniziale")
            return

        time.sleep(1)  # Ridotto per velocità

        # Verifica e applica filtro CIVILE solo se non è già selezionato
        print("🔍 Verifica filtro CIVILE...")
        try:
            civile_btn = driver.find_element(By.XPATH, '//tr[@id="1.[kind]"]')
            is_selected = civile_btn.get_attribute("style").find("background-color") != -1

            if not is_selected:
                print("  Applicazione filtro CIVILE...")
                driver.execute_script("arguments[0].click();", civile_btn)
                time.sleep(1)
            else:
                print("  ✓ Filtro CIVILE già attivo")
        except Exception as e:
            print(f"  ⚠️  Errore filtro CIVILE: {e}")

        # Verifica e applica filtro QUINTA solo se non è già selezionato
        print("🔍 Verifica filtro QUINTA SEZIONE...")
        try:
            quinta_btn = driver.find_element(By.XPATH, '//tr[@id="4.[szdec]"]')
            is_selected = quinta_btn.get_attribute("style").find("background-color") != -1

            if not is_selected:
                print("  Applicazione filtro QUINTA SEZIONE...")
                driver.execute_script("arguments[0].click();", quinta_btn)
                time.sleep(1)
                print("  ✓ Filtro QUINTA applicato")
            else:
                print("  ✓ Filtro QUINTA già attivo")
        except Exception as e:
            print(f"  ⚠️  Errore filtro QUINTA: {e}")

        # Verifica filtri applicati leggendo gli input nascosti
        print("\n✅ Verifica filtri applicati:")
        try:
            kind_value = driver.find_element(By.CSS_SELECTOR, 'input[name="[kind]"]').get_attribute("value")
            szdec_value = driver.find_element(By.CSS_SELECTOR, 'input[name="[szdec]"]').get_attribute("value")
            print(f"  ARCHIVIO [kind]: {kind_value}")
            print(f"  SEZIONE [szdec]: {szdec_value}")

            # Verifica che i filtri siano corretti
            if kind_value and 'snciv' in kind_value:
                print("  ✓ CIVILE confermato")
            else:
                print(f"  ⚠️  ATTENZIONE: CIVILE non attivo! Valore: {kind_value}")

            if szdec_value and '5' in szdec_value:
                print("  ✓ QUINTA confermato")
            else:
                print(f"  ⚠️  ATTENZIONE: QUINTA non attiva! Valore: {szdec_value}")
        except Exception as e:
            print(f"  ⚠️  Errore verifica filtri: {e}")

        # NOTA: Filtro anno NON disponibile via web (selettore non trovato)
        # Il filtro viene applicato durante il parsing HTML (script 2_parse_html_to_json.py)
        # Strategia: scarica TUTTI gli HTML, poi filtra per anno durante parsing
        if year:
            print(f"ℹ️  Filtro anno {year} sarà applicato durante parsing (non disponibile via web)")

        print(f"\n📥 Inizio download...\n")

        # Scarica la prima pagina
        page_ids = get_page_sentence_ids(driver)
        if stop_at_id and stop_at_id in page_ids:
            print(f"🛑 ID {stop_at_id} trovato nella prima pagina - stop incrementale")
            found_stop_id = True

        if save_page_html(driver, output_path, timestamp):
            downloaded += 1

        # Verifica CAPTCHA
        if check_for_captcha(driver):
            print("⚠️  CAPTCHA rilevato! Impossibile continuare.")
            return downloaded

        # Se abbiamo già trovato lo stop ID, fermiamoci
        if found_stop_id:
            print(f"✅ Download completato (stop incrementale)")
            print(f"📊 Pagine scaricate: {downloaded}")
            print(f"📁 File in: {output_path.absolute()}")
            return downloaded

        # Scarica le pagine successive
        for i in range(2, num_pages + 1):
            if not click_next_page(driver):
                print(f"✗ Impossibile navigare alla pagina {i} (ultima pagina raggiunta)")
                break

            if not wait_for_page_load(driver):
                print(f"✗ Timeout pagina {i}")
                break

            # Controlla se abbiamo trovato lo stop ID
            if stop_at_id:
                page_ids = get_page_sentence_ids(driver)
                if stop_at_id in page_ids:
                    print(f"🛑 ID {stop_at_id} trovato a pagina {i} - stop incrementale")
                    # Salva comunque questa pagina (per avere le nuove sentenze prima dello stop ID)
                    if save_page_html(driver, output_path, timestamp):
                        downloaded += 1
                    found_stop_id = True
                    break

            if save_page_html(driver, output_path, timestamp):
                downloaded += 1

            # Controlla CAPTCHA
            if check_for_captcha(driver):
                print("⚠️  CAPTCHA rilevato! Stop download.")
                break

            # Pausa tra le richieste (ridotta per HTML)
            time.sleep(0.5)

        print(f"\n✅ Download completato!")
        print(f"📊 Pagine scaricate: {downloaded}{f'/{num_pages}' if not found_stop_id else ' (stop incrementale)'}")
        print(f"📁 File in: {output_path.absolute()}")

    except KeyboardInterrupt:
        print("\n⚠️  Interrotto dall'utente")
    except Exception as e:
        print(f"\n✗ Errore: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

        return downloaded


def main():
    parser = argparse.ArgumentParser(
        description="STEP 1: Scarica HTML delle pagine di sentenze (con stop incrementale)"
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=10,
        help="Numero massimo di pagine da scaricare (default: 10)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="scraper/data/html",
        help="Directory di output (default: scraper/data/html)"
    )
    parser.add_argument(
        "--year",
        type=str,
        default=None,
        help="Filtra per anno specifico (es: 2020)"
    )
    parser.add_argument(
        "--stop-at-id",
        type=str,
        default=None,
        help="ID sentenza dove fermarsi (per aggiornamento incrementale)"
    )
    parser.add_argument(
        "--auto-stop",
        action="store_true",
        help="Carica automaticamente ultimo ID dal JSON e ferma lì (modalità incrementale)"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Mostra il browser durante l'esecuzione"
    )

    args = parser.parse_args()

    download_html_pages(
        num_pages=args.pages,
        output_dir=args.output,
        headless=not args.no_headless,
        year=args.year,
        stop_at_id=args.stop_at_id,
        auto_stop=args.auto_stop
    )


if __name__ == "__main__":
    main()
