#!/usr/bin/env python3
"""
Script per scaricare automaticamente le sentenze CIVILE - QUINTA SEZIONE
dalla Cassazione (italgiure.giustizia.it)
"""

import os
import time
import argparse
from pathlib import Path
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


def wait_for_page_load(driver, page_num):
    """Attende il caricamento della pagina verificando il numero di pagina nel title"""
    try:
        WebDriverWait(driver, 20).until(
            lambda d: f"pagina {page_num} di" in d.find_element(By.ID, "contentData").get_attribute("title").lower()
        )
        time.sleep(2)  # Attesa aggiuntiva per completare il rendering
        return True
    except TimeoutException:
        print(f"Timeout durante il caricamento della pagina {page_num}")
        return False


def click_page(driver, page_num):
    """Clicca sul numero di pagina specificato"""
    try:
        # Trova il link della pagina tramite data-arg
        pager = driver.find_element(By.CSS_SELECTOR, f'a.pager[data-arg="{page_num}"]')

        # Scroll all'elemento se necessario
        driver.execute_script("arguments[0].scrollIntoView(true);", pager)
        time.sleep(0.5)

        # Click JavaScript
        driver.execute_script("arguments[0].click();", pager)

        return wait_for_page_load(driver, page_num)
    except NoSuchElementException:
        print(f"Pulsante pagina {page_num} non trovato")
        return False


def get_total_pages(driver):
    """Estrae il numero totale di pagine"""
    try:
        title = driver.find_element(By.ID, "contentData").get_attribute("title")
        # Estrae da "pagina X di YYYY"
        total = int(title.split("di")[1].strip())
        return total
    except (NoSuchElementException, IndexError, ValueError):
        print("Impossibile determinare il numero totale di pagine")
        return None


def save_page_html(driver, page_num, output_dir):
    """Salva l'HTML della pagina corrente"""
    try:
        # Attende che il contenuto sia caricato
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dataset"))
        )

        # Ottiene l'HTML completo
        html_content = driver.page_source

        # Ottiene il titolo della pagina per il nome file
        title = driver.find_element(By.ID, "contentData").get_attribute("title")
        filename = f"{title}.html"

        filepath = output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✓ Salvata: {filename}")
        return True
    except Exception as e:
        print(f"✗ Errore nel salvataggio della pagina {page_num}: {e}")
        return False


def scrape_sentenze(start_page=1, end_page=None, output_dir="data/html", headless=True):
    """
    Scarica le sentenze CIVILE - QUINTA SEZIONE

    Args:
        start_page: Numero della pagina iniziale (default: 1)
        end_page: Numero della pagina finale (default: None = tutte)
        output_dir: Directory dove salvare i file HTML
        headless: Esegui in modalità headless (default: True)
    """
    # Crea la directory di output se non esiste
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Avvio scraping sentenze CIVILE - QUINTA SEZIONE")
    print(f"Directory output: {output_path.absolute()}")

    driver = None
    try:
        driver = setup_driver(headless)

        # URL del sito (nota: potrebbe essere necessario costruire l'URL con i filtri già applicati)
        # Per ora uso l'URL base e applico i filtri via JavaScript
        url = "https://www.italgiure.giustizia.it/sncass/"

        print(f"Caricamento pagina iniziale: {url}")
        driver.get(url)

        # Attende il caricamento completo
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "contentData"))
        )
        time.sleep(3)

        # Applica filtro CIVILE
        print("Applicazione filtro CIVILE...")
        try:
            civile_btn = driver.find_element(By.CSS_SELECTOR, 'tr#1\\.\\[kind\\]')
            driver.execute_script("arguments[0].click();", civile_btn)
            time.sleep(2)
        except Exception as e:
            print(f"Nota: filtro CIVILE potrebbe essere già applicato: {e}")

        # Applica filtro QUINTA
        print("Applicazione filtro QUINTA SEZIONE...")
        try:
            quinta_btn = driver.find_element(By.CSS_SELECTOR, 'tr#4\\.\\[szdec\\]')
            driver.execute_script("arguments[0].click();", quinta_btn)
            time.sleep(3)
        except Exception as e:
            print(f"Nota: filtro QUINTA potrebbe essere già applicato: {e}")

        # Ottiene il numero totale di pagine
        total_pages = get_total_pages(driver)
        if not total_pages:
            print("Impossibile determinare il numero totale di pagine. Uscita.")
            return

        print(f"Numero totale di pagine: {total_pages}")

        # Determina l'intervallo di pagine da scaricare
        if end_page is None:
            end_page = total_pages
        else:
            end_page = min(end_page, total_pages)

        print(f"Scarico pagine da {start_page} a {end_page}")

        # Salva la prima pagina
        if start_page == 1:
            print(f"\nPagina 1/{total_pages}")
            save_page_html(driver, 1, output_path)

        # Naviga e salva le altre pagine
        current_page = 1
        for page_num in range(max(2, start_page), end_page + 1):
            print(f"\nPagina {page_num}/{total_pages}")

            # Se la pagina è più avanti, potrebbe essere necessario cliccare più volte
            # o usare un approccio diverso
            if page_num <= 10:
                # Le prime 10 pagine sono direttamente accessibili
                if click_page(driver, page_num):
                    save_page_html(driver, page_num, output_path)
                    current_page = page_num
                else:
                    print(f"Impossibile navigare alla pagina {page_num}")
            else:
                # Per le pagine successive, usa il pulsante ">"
                while current_page < page_num:
                    try:
                        next_btn = driver.find_element(By.CSS_SELECTOR, 'span.pager.pagerArrow[title="pagina successiva"]')
                        driver.execute_script("arguments[0].click();", next_btn)
                        current_page += 1
                        if wait_for_page_load(driver, current_page):
                            if current_page == page_num:
                                save_page_html(driver, page_num, output_path)
                        else:
                            print(f"Timeout alla pagina {current_page}")
                            break
                    except NoSuchElementException:
                        print("Pulsante 'pagina successiva' non trovato")
                        break

            # Pausa tra le richieste per non sovraccaricare il server
            time.sleep(1)

        print(f"\n✓ Scraping completato!")
        print(f"File salvati in: {output_path.absolute()}")

    except KeyboardInterrupt:
        print("\n\nInterrotto dall'utente")
    except Exception as e:
        print(f"\n✗ Errore durante lo scraping: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()


def main():
    parser = argparse.ArgumentParser(
        description="Scarica sentenze CIVILE - QUINTA SEZIONE dalla Cassazione"
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Pagina iniziale (default: 1)"
    )
    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="Pagina finale (default: tutte)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/html",
        help="Directory di output (default: data/html)"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Mostra il browser durante l'esecuzione"
    )

    args = parser.parse_args()

    scrape_sentenze(
        start_page=args.start,
        end_page=args.end,
        output_dir=args.output,
        headless=not args.no_headless
    )


if __name__ == "__main__":
    main()
