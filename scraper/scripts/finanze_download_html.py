#!/usr/bin/env python3
"""
SCRAPER SENTENZE MEF - Ministero Economia e Finanze
Estrae sentenze da def.finanze.it usando Selenium

SUPER EFFICIENTE perché:
1. I dati sono già in XML embedded nella pagina
2. Non serve parsing HTML complesso
3. Estrazione velocissima con xpath/regex
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
    """Configura e ritorna il driver Selenium"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # Headers realistici per evitare 403
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def extract_xml_from_page(driver):
    """
    Estrae l'XML embedded dalla variabile JavaScript 'xmlResult'
    Questo è il cuore dell'efficienza: i dati sono già strutturati!
    """
    try:
        # Estrai la variabile JavaScript con l'XML
        script = """
        return (typeof xmlResult !== 'undefined') ? xmlResult : null;
        """
        xml_string = driver.execute_script(script)

        if xml_string:
            # Unescape caratteri speciali
            xml_string = xml_string.replace('\\"', '"').replace('\\/', '/')
            return xml_string
        else:
            # Fallback: cerca nel page source con regex
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
    """
    Parsing veloce dell'XML con tutti i risultati
    Ritorna lista di dizionari con i dati delle sentenze
    """
    if not xml_string:
        return []

    try:
        # Parse XML
        root = ET.fromstring(xml_string)

        # Estrai metadati
        metadata = {
            'contatore_giurisprudenza': root.find('.//contatoreGiurisprudenza').text if root.find('.//contatoreGiurisprudenza') is not None else '0',
            'pagina': root.find('.//pagina').text if root.find('.//pagina') is not None else '1',
            'ultima_pagina': root.find('.//ultimaPagina').text if root.find('.//ultimaPagina') is not None else '1',
            'totale_provvedimenti': root.find('.//totaleProvvedimenti').text if root.find('.//totaleProvvedimenti') is not None else '0',
            'ulteriori_risultati': root.find('.//ulterioriRisultati').text if root.find('.//ulterioriRisultati') is not None else 'false'
        }

        # Estrai tutti i provvedimenti
        provvedimenti = []
        for prov in root.findall('.//Provvedimento'):
            id_prov = prov.get('idProvvedimento', '')
            estremi_elem = prov.find('estremi')
            estremi = estremi_elem.text if estremi_elem is not None else ''

            # Estrai titoli (possono essere HTML/CDATA)
            titoli = []
            for titolo_elem in prov.findall('.//titoloProvvedimento'):
                titolo_text = ''.join(titolo_elem.itertext()).strip()
                if titolo_text:
                    titoli.append(titolo_text)

            provvedimenti.append({
                'id': id_prov,
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


def compile_search_form(driver, filters):
    """
    Compila il form di ricerca con i filtri specificati

    filters = {
        'ente': 'Corte di Cassazione',  # o 'Commissione Tributaria', ecc.
        'data_da': '01/01/2022',
        'data_a': '31/12/2022',
        'numero': '',
        'anno': '',
        'parole': '',
        'ricerca_massimate': True/False
    }
    """
    print(f"📝 Compilazione form con filtri:")
    for k, v in filters.items():
        print(f"   {k}: {v}")

    try:
        # Selezione ente (dropdown o campo nascosto)
        if filters.get('ente'):
            try:
                ente_select = Select(driver.find_element(By.NAME, "ente"))
                ente_select.select_by_visible_text(filters['ente'])
            except NoSuchElementException:
                # Se non è un select, potrebbe essere già impostato
                pass

        # Data emissione DA
        if filters.get('data_da'):
            data_da_input = driver.find_element(By.NAME, "dataEmissioneDa")
            data_da_input.clear()
            data_da_input.send_keys(filters['data_da'])

        # Data emissione A
        if filters.get('data_a'):
            data_a_input = driver.find_element(By.NAME, "dataEmissioneA")
            data_a_input.clear()
            data_a_input.send_keys(filters['data_a'])

        # Numero sentenza
        if filters.get('numero'):
            numero_input = driver.find_element(By.NAME, "numero")
            numero_input.clear()
            numero_input.send_keys(filters['numero'])

        # Anno
        if filters.get('anno'):
            anno_input = driver.find_element(By.NAME, "anno")
            anno_input.clear()
            anno_input.send_keys(filters['anno'])

        # Parole chiave
        if filters.get('parole'):
            parole_input = driver.find_element(By.NAME, "parole")
            parole_input.clear()
            parole_input.send_keys(filters['parole'])

        # Ricerca solo massimate
        if filters.get('ricerca_massimate'):
            try:
                massimate_checkbox = driver.find_element(By.NAME, "ricercaNelTitolo")
                if not massimate_checkbox.is_selected():
                    massimate_checkbox.click()
            except NoSuchElementException:
                pass

        print("✓ Form compilato")
        return True

    except Exception as e:
        print(f"✗ Errore compilazione form: {e}")
        return False


def click_next_page(driver):
    """Clicca sul link 'Avanti' per andare alla pagina successiva"""
    try:
        # Cerca il link "Avanti" (ce ne sono 2, uno sopra e uno sotto)
        avanti_links = driver.find_elements(By.CLASS_NAME, "avanti")
        if avanti_links:
            # Usa il primo link "Avanti" trovato
            avanti_links[0].click()
            time.sleep(2)  # Attesa caricamento
            return True
        else:
            print("⚠️  Link 'Avanti' non trovato")
            return False
    except Exception as e:
        print(f"✗ Errore click pagina successiva: {e}")
        return False


def scrape_finanze(filters, output_dir="scraper/data/finanze", headless=True):
    """
    Main function: esegue lo scraping completo del sito MEF

    Args:
        filters: dizionario con i filtri di ricerca
        output_dir: directory dove salvare i risultati
        headless: modalità headless del browser

    Returns:
        dict con tutti i risultati raccolti
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("🚀 SCRAPER SENTENZE MEF - Ministero Economia e Finanze")
    print("="*70)
    print(f"📁 Output: {output_path.absolute()}")
    print(f"🕐 Timestamp: {timestamp}\n")

    driver = None
    all_results = {
        'timestamp': timestamp,
        'filters': filters,
        'metadata': {},
        'sentenze': []
    }

    try:
        driver = setup_driver(headless)

        # URL della pagina di ricerca avanzata
        url = "https://def.finanze.it/DocTribFrontend/callRicAvanzataGiurisprudenza.do"
        print(f"🌐 Caricamento {url}...")
        driver.get(url)

        # Attesa caricamento
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "dataEmissioneDa"))
        )
        time.sleep(2)

        print("✓ Pagina caricata")

        # Compila il form di ricerca
        if not compile_search_form(driver, filters):
            print("✗ Impossibile compilare il form")
            return all_results

        # Submit del form
        print("\n🔍 Invio ricerca...")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_button.click()

        # Attesa risultati
        time.sleep(3)

        # Controlla se ci sono risultati
        page_source = driver.page_source
        if "Documenti trovati" not in page_source:
            print("⚠️  Nessun risultato trovato o errore nella ricerca")
            # Salva HTML per debug
            debug_file = output_path / f"debug_no_results_{timestamp}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(page_source)
            print(f"📄 HTML salvato in {debug_file} per debug")
            return all_results

        print("✓ Risultati trovati!\n")

        # Loop attraverso tutte le pagine
        page_num = 1
        while True:
            print(f"📄 Elaborazione pagina {page_num}...")

            # Estrai XML dalla pagina corrente
            xml_string = extract_xml_from_page(driver)

            if not xml_string:
                print(f"⚠️  Impossibile estrarre XML da pagina {page_num}")
                break

            # Parse XML
            page_data = parse_xml_results(xml_string)

            if page_num == 1:
                # Salva metadata dalla prima pagina
                all_results['metadata'] = page_data.get('metadata', {})
                print(f"📊 Totale documenti: {all_results['metadata'].get('contatore_giurisprudenza', '?')}")
                print(f"📊 Totale pagine: {all_results['metadata'].get('ultima_pagina', '?')}")

            # Aggiungi sentenze alla lista
            provvedimenti = page_data.get('provvedimenti', [])
            all_results['sentenze'].extend(provvedimenti)
            print(f"✓ Estratti {len(provvedimenti)} provvedimenti da pagina {page_num}")

            # Controlla se ci sono altre pagine
            ultima_pagina = int(all_results['metadata'].get('ultima_pagina', '1'))
            if page_num >= ultima_pagina:
                print(f"\n✅ Raggiunta ultima pagina ({ultima_pagina})")
                break

            # Vai alla pagina successiva
            if not click_next_page(driver):
                print(f"⚠️  Impossibile andare alla pagina successiva")
                break

            page_num += 1
            time.sleep(2)  # Pausa tra pagine

        # Salva risultati finali
        output_file = output_path / f"sentenze_mef_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Scraping completato!")
        print(f"📊 Totale sentenze raccolte: {len(all_results['sentenze'])}")
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
        description="SCRAPER sentenze MEF - Ministero Economia e Finanze"
    )
    parser.add_argument(
        "--ente",
        type=str,
        default="Corte di Cassazione",
        help="Autorità emanante (default: Corte di Cassazione)"
    )
    parser.add_argument(
        "--data-da",
        type=str,
        default=None,
        help="Data emissione DA (formato: GG/MM/AAAA)"
    )
    parser.add_argument(
        "--data-a",
        type=str,
        default=None,
        help="Data emissione A (formato: GG/MM/AAAA)"
    )
    parser.add_argument(
        "--anno",
        type=str,
        default=None,
        help="Anno sentenza (es: 2022)"
    )
    parser.add_argument(
        "--numero",
        type=str,
        default=None,
        help="Numero sentenza"
    )
    parser.add_argument(
        "--parole",
        type=str,
        default=None,
        help="Parole chiave da cercare"
    )
    parser.add_argument(
        "--massimate",
        action="store_true",
        help="Cerca solo sentenze massimate"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="scraper/data/finanze",
        help="Directory di output (default: scraper/data/finanze)"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Mostra il browser durante l'esecuzione"
    )

    args = parser.parse_args()

    # Prepara filtri
    filters = {
        'ente': args.ente,
        'data_da': args.data_da,
        'data_a': args.data_a,
        'anno': args.anno,
        'numero': args.numero,
        'parole': args.parole,
        'ricerca_massimate': args.massimate
    }

    # Rimuovi filtri None
    filters = {k: v for k, v in filters.items() if v is not None}

    # Esegui scraping
    scrape_finanze(
        filters=filters,
        output_dir=args.output,
        headless=not args.no_headless
    )


if __name__ == "__main__":
    main()
