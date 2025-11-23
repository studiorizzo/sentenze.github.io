#!/usr/bin/env python3
"""
STEP 1 (RANGE): Download HTML pages for specific page range
Scarica un range specifico di pagine di sentenze CIVILE - QUINTA SEZIONE
Usa: per recuperare pagine mancanti o errori precedenti
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException


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
        time.sleep(0.5)
        return True
    except TimeoutException:
        return False


def wait_for_results_update(driver, timeout=15):
    """Attende che i risultati siano aggiornati dopo l'applicazione dei filtri"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-role="content"][data-arg="szdec"]'))
        )
        time.sleep(3)
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


def navigate_to_page(driver, target_page):
    """Naviga a una pagina specifica inserendo il numero"""
    try:
        # Trova il campo input per il numero di pagina
        page_input = driver.find_element(By.ID, "pagerInputValue")

        # Cancella il contenuto attuale
        page_input.clear()

        # Inserisci il numero di pagina target
        page_input.send_keys(str(target_page))

        # Trova e clicca il pulsante "vai" per confermare
        go_button = driver.find_element(By.CSS_SELECTOR, 'span[title="vai alla pagina"][data-role="internalaction"]')
        driver.execute_script("arguments[0].click();", go_button)

        # Attendi il caricamento
        time.sleep(2)
        if not wait_for_page_load(driver):
            return False

        # Verifica che siamo arrivati alla pagina corretta
        current = get_current_page_number(driver)
        if current == target_page:
            return True
        else:
            print(f"  ⚠️  Navigato a pagina {current} invece di {target_page}")
            return False

    except Exception as e:
        print(f"  ✗ Errore navigazione a pagina {target_page}: {e}")
        return False


def click_next_page(driver, max_retries=3):
    """Clicca sul pulsante pagina successiva con retry automatico per stale element"""
    for attempt in range(max_retries):
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
        except StaleElementReferenceException:
            if attempt < max_retries - 1:
                print(f"  ⚠️  Stale element (tentativo {attempt + 1}/{max_retries}), retry...")
                time.sleep(1)
                continue
            else:
                print(f"  ✗ Stale element dopo {max_retries} tentativi")
                raise
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


def download_html_pages_range(start_page, end_page, output_dir="scraper/data/html", headless=True):
    """
    Scarica un range specifico di pagine di sentenze CIVILE - QUINTA SEZIONE

    Args:
        start_page: Numero della prima pagina da scaricare
        end_page: Numero dell'ultima pagina da scaricare (inclusa)
        output_dir: Directory dove salvare i file HTML
        headless: Esegui in modalità headless (default: True)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    num_pages = end_page - start_page + 1

    print(f"🚀 Download HTML RANGE - Sentenze CIVILE QUINTA SEZIONE")
    print(f"📁 Output: {output_path.absolute()}")
    print(f"📄 Range pagine: {start_page} → {end_page} ({num_pages} pagine totali)")
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
            return 0

        time.sleep(1)

        # Applica filtro CIVILE
        print("🔍 Applicazione filtro CIVILE...")
        try:
            kind_input = driver.find_element(By.CSS_SELECTOR, 'input[name="[kind]"]')
            current_value = kind_input.get_attribute("value") or ""
            is_civile_selected = 'snciv' in current_value and 'snpen' not in current_value

            if not is_civile_selected:
                civile_btn = driver.find_element(By.XPATH, '//tr[@id="1.[kind]"]')
                driver.execute_script("arguments[0].click();", civile_btn)
                print("  Attesa aggiornamento risultati...")
                if not wait_for_results_update(driver):
                    print("  ⚠️  Timeout aggiornamento risultati")
                print("  ✓ Filtro CIVILE applicato")
            else:
                print("  ✓ Filtro CIVILE già attivo")
        except Exception as e:
            print(f"  ⚠️  Errore filtro CIVILE: {e}")
            return 0

        time.sleep(2)

        # Applica filtro QUINTA
        print("🔍 Applicazione filtro QUINTA SEZIONE...")
        try:
            szdec_input = driver.find_element(By.CSS_SELECTOR, 'input[name="[szdec]"]')
            current_value = szdec_input.get_attribute("value") or ""
            is_quinta_selected = '5' in current_value

            if not is_quinta_selected:
                quinta_btn = driver.find_element(
                    By.XPATH,
                    '//span[text()="QUINTA"]/ancestor::tr[contains(@id, "[szdec]")]'
                )
                driver.execute_script("arguments[0].click();", quinta_btn)
                print("  Attesa aggiornamento risultati...")
                if not wait_for_results_update(driver):
                    print("  ⚠️  Timeout aggiornamento risultati")
                print("  ✓ Filtro QUINTA applicato")
            else:
                print("  ✓ Filtro QUINTA già attivo")
        except Exception as e:
            print(f"  ⚠️  Errore filtro QUINTA: {e}")
            return 0

        # Verifica filtri
        print("\n✅ Verifica filtri applicati:")
        try:
            kind_value = driver.find_element(By.CSS_SELECTOR, 'input[name="[kind]"]').get_attribute("value")
            szdec_value = driver.find_element(By.CSS_SELECTOR, 'input[name="[szdec]"]').get_attribute("value")
            print(f"  ARCHIVIO [kind]: {kind_value}")
            print(f"  SEZIONE [szdec]: {szdec_value}")

            if kind_value and 'snciv' in kind_value:
                print("  ✓ CIVILE confermato")
            else:
                print(f"  ⚠️  ATTENZIONE: CIVILE non attivo!")
                return 0

            if szdec_value and '5' in szdec_value:
                print("  ✓ QUINTA confermato")
            else:
                print(f"  ⚠️  ATTENZIONE: QUINTA non attiva!")
                return 0
        except Exception as e:
            print(f"  ⚠️  Errore verifica filtri: {e}")
            return 0

        # Naviga alla pagina iniziale
        if start_page > 1:
            print(f"\n🔄 Navigazione alla pagina {start_page}...")
            if not navigate_to_page(driver, start_page):
                print(f"✗ Impossibile navigare alla pagina {start_page}")
                return 0
            print(f"✓ Arrivato a pagina {start_page}")

        print(f"\n📥 Inizio download range {start_page}-{end_page}...\n")

        # Scarica le pagine nel range
        current_page = start_page
        while current_page <= end_page:
            try:
                # Verifica numero pagina corrente
                actual_page = get_current_page_number(driver)
                if actual_page != current_page:
                    print(f"⚠️  Pagina attuale {actual_page} diversa da attesa {current_page}, sincronizzazione...")
                    current_page = actual_page
                    if current_page > end_page:
                        print(f"✓ Superato end_page {end_page}, stop")
                        break

                # Salva la pagina corrente
                if save_page_html(driver, output_path, timestamp):
                    downloaded += 1

                # Se abbiamo raggiunto l'ultima pagina, fermiamoci
                if current_page >= end_page:
                    print(f"✓ Raggiunta pagina finale {end_page}")
                    break

                # Salva numero pagina prima del click
                page_before_click = get_current_page_number(driver)

                # Vai alla pagina successiva
                if not click_next_page(driver):
                    print(f"✗ Impossibile andare alla pagina successiva (ultima pagina raggiunta)")
                    break

                # Attendi caricamento
                if not wait_for_page_load(driver):
                    print(f"✗ Timeout caricamento pagina successiva")
                    break

                # Verifica che il numero di pagina sia cambiato
                page_after_click = get_current_page_number(driver)
                if page_after_click == page_before_click:
                    print(f"⚠️  Numero pagina non cambiato ({page_after_click}), attesa aggiuntiva...")
                    time.sleep(2)
                    page_after_click = get_current_page_number(driver)

                    if page_after_click == page_before_click:
                        print(f"✗ Errore: pagina bloccata su {page_after_click}")
                        break

                current_page = page_after_click

                # Progress report ogni 50 pagine
                if downloaded % 50 == 0:
                    progress_pct = ((downloaded) / num_pages) * 100
                    print(f"📊 Progresso: {downloaded}/{num_pages} pagine ({progress_pct:.1f}%)")

                # Pausa tra le richieste
                time.sleep(0.5)

            except StaleElementReferenceException as e:
                print(f"⚠️  Errore stale element a pagina {current_page}: {e}")
                print(f"💾 Salvati {downloaded} file HTML fino a questo punto")
                time.sleep(2)
                continue
            except Exception as e:
                print(f"⚠️  Errore inaspettato a pagina {current_page}: {e}")
                print(f"💾 Salvati {downloaded} file HTML fino a questo punto")
                time.sleep(2)
                continue

        print(f"\n✅ Download range completato!")
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
        description="STEP 1 (RANGE): Scarica HTML di un range specifico di pagine"
    )
    parser.add_argument(
        "--start",
        type=int,
        required=True,
        help="Numero della prima pagina da scaricare (es: 3688)"
    )
    parser.add_argument(
        "--end",
        type=int,
        required=True,
        help="Numero dell'ultima pagina da scaricare (es: 4064)"
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

    if args.start < 1:
        print("✗ Errore: start deve essere >= 1")
        return

    if args.end < args.start:
        print("✗ Errore: end deve essere >= start")
        return

    download_html_pages_range(
        start_page=args.start,
        end_page=args.end,
        output_dir=args.output,
        headless=not args.no_headless
    )


if __name__ == "__main__":
    main()
