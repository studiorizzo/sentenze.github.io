#!/usr/bin/env python3
"""
MEF SCRAPER - STEP 1: Scraping lista sentenze
Estrae lista sentenze da def.finanze.it con filtri specificati
Output: JSON con lista sentenze (ID, URL, estremi, titoli)
"""

import os
import re
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from xml.etree import ElementTree as ET
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def setup_driver(headless=True):
    """Configura driver Selenium con Chrome"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def extract_xml_from_page(driver):
    """Estrae XML embedded dalla variabile JavaScript 'xmlResult'"""
    try:
        script = "return (typeof xmlResult !== 'undefined') ? xmlResult : null;"
        xml_string = driver.execute_script(script)

        if xml_string:
            xml_string = xml_string.replace('\\"', '"').replace('\\/', '/')
            return xml_string
        else:
            # Fallback: regex sul page source
            page_source = driver.page_source
            match = re.search(r"var xmlResult = '(.+?)';", page_source, re.DOTALL)
            if match:
                xml_string = match.group(1)
                xml_string = xml_string.replace('\\/', '/').replace('\\"', '"')
                return xml_string
    except Exception as e:
        print(f"⚠️  Errore estrazione XML: {e}")

    return None


def parse_xml_results(xml_string):
    """Parse XML e ritorna dizionario con metadata + provvedimenti"""
    if not xml_string:
        return {'metadata': {}, 'provvedimenti': []}

    try:
        root = ET.fromstring(xml_string)

        metadata = {
            'contatore_giurisprudenza': root.find('.//contatoreGiurisprudenza').text if root.find('.//contatoreGiurisprudenza') is not None else '0',
            'pagina': root.find('.//pagina').text if root.find('.//pagina') is not None else '1',
            'ultima_pagina': root.find('.//ultimaPagina').text if root.find('.//ultimaPagina') is not None else '1',
            'totale_provvedimenti': root.find('.//totaleProvvedimenti').text if root.find('.//totaleProvvedimenti') is not None else '0',
            'ulteriori_risultati': root.find('.//ulterioriRisultati').text if root.find('.//ulterioriRisultati') is not None else 'false'
        }

        provvedimenti = []
        for prov in root.findall('.//Provvedimento'):
            id_prov = prov.get('idProvvedimento', '')
            estremi_elem = prov.find('estremi')
            estremi = estremi_elem.text if estremi_elem is not None else ''

            titoli = []
            for titolo_elem in prov.findall('.//titoloProvvedimento'):
                titolo_text = ''.join(titolo_elem.itertext()).strip()
                if titolo_text:
                    titoli.append(titolo_text)

            url = f"https://def.finanze.it/DocTribFrontend/getGiurisprudenzaDetail.do?id={id_prov}"

            provvedimenti.append({
                'id': id_prov,
                'url': url,
                'estremi': estremi,
                'titoli': titoli
            })

        return {
            'metadata': metadata,
            'provvedimenti': provvedimenti
        }

    except ET.ParseError as e:
        print(f"⚠️  Errore parsing XML: {e}")
        return {'metadata': {}, 'provvedimenti': []}


def click_next_page(driver):
    """Clicca sul link 'Avanti' per prossima pagina"""
    try:
        avanti_links = driver.find_elements(By.CLASS_NAME, "avanti")
        if avanti_links:
            avanti_links[0].click()
            time.sleep(2)
            return True
        return False
    except Exception as e:
        print(f"✗ Errore navigazione pagina: {e}")
        return False


def scrape_lista_sentenze(anno, ente="Corte di Cassazione", solo_massimate=False, output_dir="scraper/data/mef", headless=True):
    """
    Scraping lista sentenze con filtri

    Returns:
        dict: {
            'timestamp': ...,
            'filters': {...},
            'metadata': {...},
            'sentenze': [...]
        }
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("🚀 MEF SCRAPER - STEP 1: Lista Sentenze")
    print("="*70)
    print(f"📁 Output: {output_path.absolute()}")
    print(f"📅 Anno: {anno}")
    print(f"🏛️  Ente: {ente}")
    print(f"📋 Solo massimate: {solo_massimate}")
    print(f"🕐 Timestamp: {timestamp}\n")

    driver = None
    all_results = {
        'timestamp': timestamp,
        'filters': {
            'anno': anno,
            'ente': ente,
            'solo_massimate': solo_massimate,
            'data_da': f'01/01/{anno}',
            'data_a': f'31/12/{anno}'
        },
        'metadata': {},
        'sentenze': []
    }

    try:
        driver = setup_driver(headless)

        # Vai alla pagina di ricerca avanzata
        url = "https://def.finanze.it/DocTribFrontend/callRicAvanzataGiurisprudenza.do"
        print(f"🌐 Caricamento {url}...")
        driver.get(url)

        # Attesa caricamento
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "dataEmissioneDa"))
        )
        time.sleep(2)
        print("✓ Pagina caricata\n")

        # Compila form
        print("📝 Compilazione filtri ricerca...")

        # Data DA
        data_da = driver.find_element(By.NAME, "dataEmissioneDa")
        data_da.clear()
        data_da.send_keys(f"01/01/{anno}")

        # Data A
        data_a = driver.find_element(By.NAME, "dataEmissioneA")
        data_a.clear()
        data_a.send_keys(f"31/12/{anno}")

        # Ente (se select)
        try:
            ente_select = Select(driver.find_element(By.NAME, "ente"))
            ente_select.select_by_visible_text(ente)
        except:
            pass

        # Solo massimate
        if solo_massimate:
            try:
                massimate_checkbox = driver.find_element(By.NAME, "ricercaNelTitolo")
                if not massimate_checkbox.is_selected():
                    massimate_checkbox.click()
            except:
                pass

        print("✓ Filtri applicati\n")

        # Submit
        print("🔍 Invio ricerca...")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_button.click()
        time.sleep(3)

        # Verifica risultati
        page_source = driver.page_source
        if "Documenti trovati" not in page_source:
            print("⚠️  Nessun risultato trovato")
            return all_results

        print("✓ Risultati trovati!\n")

        # Loop pagine
        page_num = 1
        while True:
            print(f"📄 Elaborazione pagina {page_num}...")

            xml_string = extract_xml_from_page(driver)
            if not xml_string:
                print(f"⚠️  Impossibile estrarre XML pagina {page_num}")
                break

            page_data = parse_xml_results(xml_string)

            if page_num == 1:
                all_results['metadata'] = page_data.get('metadata', {})
                print(f"📊 Totale documenti: {all_results['metadata'].get('contatore_giurisprudenza', '?')}")
                print(f"📊 Totale pagine: {all_results['metadata'].get('ultima_pagina', '?')}\n")

            provvedimenti = page_data.get('provvedimenti', [])
            all_results['sentenze'].extend(provvedimenti)
            print(f"✓ Estratti {len(provvedimenti)} provvedimenti\n")

            ultima_pagina = int(all_results['metadata'].get('ultima_pagina', '1'))
            if page_num >= ultima_pagina:
                print(f"✅ Raggiunta ultima pagina ({ultima_pagina})")
                break

            if not click_next_page(driver):
                break

            page_num += 1
            time.sleep(2)

        # Salva risultati
        output_file = output_path / f"sentenze_lista_{anno}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Scraping lista completato!")
        print(f"📊 Totale sentenze: {len(all_results['sentenze'])}")
        print(f"📁 File salvato: {output_file}")

    except KeyboardInterrupt:
        print("\n⚠️  Interrotto dall'utente")
    except Exception as e:
        print(f"\n✗ Errore: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="MEF SCRAPER - STEP 1: Scraping lista sentenze"
    )
    parser.add_argument("--anno", type=str, required=True, help="Anno sentenze (es: 2022)")
    parser.add_argument("--ente", type=str, default="Corte di Cassazione", help="Autorità emanante")
    parser.add_argument("--massimate", action="store_true", help="Solo sentenze massimate")
    parser.add_argument("--output", type=str, default="scraper/data/mef", help="Directory output")
    parser.add_argument("--no-headless", action="store_true", help="Mostra browser")

    args = parser.parse_args()

    scrape_lista_sentenze(
        anno=args.anno,
        ente=args.ente,
        solo_massimate=args.massimate,
        output_dir=args.output,
        headless=not args.no_headless
    )


if __name__ == "__main__":
    main()
