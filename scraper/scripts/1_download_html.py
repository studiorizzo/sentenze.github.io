#!/usr/bin/env python3
"""
STEP 1: Download HTML pages
Scarica le prime N pagine di sentenze CIVILE - QUINTA SEZIONE
Usa: settimanalmente per trovare nuove sentenze
"""

import os
import time
import argparse
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
        time.sleep(2)  # Attesa aggiuntiva per JavaScript
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


def download_html_pages(num_pages=10, output_dir="scraper/data/html", headless=True):
    """
    Scarica le prime N pagine di sentenze CIVILE - QUINTA SEZIONE

    Args:
        num_pages: Numero di pagine da scaricare (default: 10)
        output_dir: Directory dove salvare i file HTML
        headless: Esegui in modalità headless (default: True)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"🚀 Download HTML - Sentenze CIVILE QUINTA SEZIONE")
    print(f"📁 Output: {output_path.absolute()}")
    print(f"📄 Pagine da scaricare: {num_pages}")
    print(f"🕐 Timestamp: {timestamp}\n")

    driver = None
    downloaded = 0

    try:
        driver = setup_driver(headless)
        url = "https://www.italgiure.giustizia.it/sncass/"

        print(f"🌐 Caricamento {url}...")
        driver.get(url)

        if not wait_for_page_load(driver):
            print("✗ Errore caricamento pagina iniziale")
            return

        time.sleep(3)

        # Applica filtro CIVILE
        print("🔍 Applicazione filtro CIVILE...")
        try:
            civile_btn = driver.find_element(By.CSS_SELECTOR, 'tr#1\\.\\[kind\\]')
            driver.execute_script("arguments[0].click();", civile_btn)
            time.sleep(2)
        except Exception as e:
            print(f"ℹ️  Filtro CIVILE già applicato o non trovato: {e}")

        # Applica filtro QUINTA
        print("🔍 Applicazione filtro QUINTA SEZIONE...")
        try:
            quinta_btn = driver.find_element(By.CSS_SELECTOR, 'tr#4\\.\\[szdec\\]')
            driver.execute_script("arguments[0].click();", quinta_btn)
            time.sleep(3)
        except Exception as e:
            print(f"ℹ️  Filtro QUINTA già applicato o non trovato: {e}")

        print(f"\n📥 Inizio download...\n")

        # Scarica la prima pagina
        if save_page_html(driver, output_path, timestamp):
            downloaded += 1

        # Scarica le pagine successive
        for i in range(2, num_pages + 1):
            if not click_next_page(driver):
                print(f"✗ Impossibile navigare alla pagina {i}")
                break

            if not wait_for_page_load(driver):
                print(f"✗ Timeout pagina {i}")
                break

            if save_page_html(driver, output_path, timestamp):
                downloaded += 1

            # Pausa tra le richieste
            time.sleep(1)

        print(f"\n✅ Download completato!")
        print(f"📊 Pagine scaricate: {downloaded}/{num_pages}")
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
        description="STEP 1: Scarica HTML delle prime N pagine di sentenze"
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=10,
        help="Numero di pagine da scaricare (default: 10)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="scraper/data/html",
        help="Directory di output (default: scraper/data/html)"
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
        headless=not args.no_headless
    )


if __name__ == "__main__":
    main()
