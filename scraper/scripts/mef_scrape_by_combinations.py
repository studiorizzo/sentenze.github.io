#!/usr/bin/env python3
"""
MEF SCRAPER - Ricerca per combinazioni Materia+Classificazione
Esegue ricerche sistematiche su tutte le combinazioni Materia+Classificazione
con ottimizzazione per evitare ricerche duplicate inutili.

PROCESSO IN DUE FASI:
1. FASE 1 (massime=false): Testa tutte le combinazioni, traccia quelle con 0 risultati
2. FASE 2 (massime=true): Ripete SOLO per le combinazioni che hanno dato risultati

OTTIMIZZAZIONE:
Se una combinazione dà 0 risultati con massime=false, viene saltata nella fase con massime=true
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
        print(f"      ⚠️  Errore estrazione XML: {e}")

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
        print(f"      ⚠️  Errore parsing XML: {e}")
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
        print(f"      ✗ Errore navigazione pagina: {e}")
        return False


def search_combination(driver, materia_code, classificazione_code, anno, ente, solo_massimate, max_pages=None):
    """
    Esegue una ricerca per una specifica combinazione Materia+Classificazione

    Returns:
        dict: {
            'num_risultati': int,
            'sentenze': [...],
            'metadata': {...}
        }
    """
    try:
        # Vai alla pagina di ricerca
        url = "https://def.finanze.it/DocTribFrontend/callRicAvanzataGiurisprudenza.do"
        driver.get(url)

        # Attesa caricamento
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "dataEmissioneDa"))
        )
        time.sleep(2)

        # Compila filtri base
        # Data DA
        data_da = driver.find_element(By.NAME, "dataEmissioneDa")
        data_da.clear()
        data_da.send_keys(f"01/01/{anno}")

        # Data A
        data_a = driver.find_element(By.NAME, "dataEmissioneA")
        data_a.clear()
        data_a.send_keys(f"31/12/{anno}")

        # Ente
        try:
            ente_select = Select(driver.find_element(By.NAME, "ente"))
            ente_select.select_by_visible_text(ente)
        except:
            pass

        # MATERIA (select by value)
        try:
            materia_select = Select(driver.find_element(By.NAME, "materiaFiscale"))
            materia_select.select_by_value(materia_code)
            time.sleep(1)  # Attesa per caricamento classificazioni dinamiche
        except Exception as e:
            print(f"      ✗ Errore selezione materia {materia_code}: {e}")
            return {'num_risultati': -1, 'sentenze': [], 'metadata': {}, 'error': str(e)}

        # CLASSIFICAZIONE (select by value)
        try:
            classificazione_select = Select(driver.find_element(By.NAME, "classificazioneArgomento"))
            classificazione_select.select_by_value(classificazione_code)
        except Exception as e:
            print(f"      ✗ Errore selezione classificazione {classificazione_code}: {e}")
            return {'num_risultati': -1, 'sentenze': [], 'metadata': {}, 'error': str(e)}

        # Solo massimate
        if solo_massimate:
            try:
                massimate_checkbox = driver.find_element(By.NAME, "ricercaNelTitolo")
                if not massimate_checkbox.is_selected():
                    massimate_checkbox.click()
            except:
                pass

        # Submit
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_button.click()
        time.sleep(3)

        # Verifica risultati
        page_source = driver.page_source
        if "Documenti trovati" not in page_source:
            # 0 risultati
            return {'num_risultati': 0, 'sentenze': [], 'metadata': {}}

        # Estrai risultati (prima pagina)
        all_sentenze = []
        page_num = 1
        metadata = {}

        while True:
            xml_string = extract_xml_from_page(driver)
            if not xml_string:
                break

            page_data = parse_xml_results(xml_string)

            if page_num == 1:
                metadata = page_data.get('metadata', {})

            provvedimenti = page_data.get('provvedimenti', [])
            all_sentenze.extend(provvedimenti)

            # Controlla se ci sono altre pagine
            ultima_pagina = int(metadata.get('ultima_pagina', '1'))

            # Se max_pages è specificato, rispettalo
            if max_pages and page_num >= max_pages:
                break

            if page_num >= ultima_pagina:
                break

            # Vai alla pagina successiva
            if not click_next_page(driver):
                break

            page_num += 1
            time.sleep(2)

        num_risultati = int(metadata.get('contatore_giurisprudenza', len(all_sentenze)))

        return {
            'num_risultati': num_risultati,
            'sentenze': all_sentenze,
            'metadata': metadata
        }

    except Exception as e:
        print(f"      ✗ Errore ricerca: {e}")
        return {'num_risultati': -1, 'sentenze': [], 'metadata': {}, 'error': str(e)}


def load_combinations(json_file):
    """
    Carica tutte le combinazioni Materia+Classificazione dal JSON

    Returns:
        list: [
            {
                'materia_code': 'Z270',
                'materia_desc': 'NC Accertamento imposte',
                'classificazione_code': '0010',
                'classificazione_desc': 'Documenti non classificati'
            },
            ...
        ]
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    combinations = []
    for classif in data['classificazioni']:
        classif_code = classif['codiceClassificazione']
        classif_desc = classif['descrizioneVC']

        for materia in classif['materie']:
            mat_code = materia['codice']
            mat_desc = materia['descrizione']

            combinations.append({
                'materia_code': mat_code,
                'materia_desc': mat_desc,
                'classificazione_code': classif_code,
                'classificazione_desc': classif_desc
            })

    return combinations


def scrape_by_combinations(
    combinations_file,
    anno,
    ente="Corte di Cassazione",
    output_dir="scraper/data/mef_combinations",
    headless=True,
    max_pages_per_search=None
):
    """
    Main function: esegue scraping per tutte le combinazioni in DUE FASI

    FASE 1: massime=false -> traccia combinazioni con 0 risultati
    FASE 2: massime=true -> solo per combinazioni con risultati

    Args:
        combinations_file: Path al JSON con le combinazioni
        anno: Anno da cercare
        ente: Autorità emanante
        output_dir: Directory output
        headless: Modalità headless
        max_pages_per_search: Numero massimo pagine per ricerca (None=illimitato)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("🚀 MEF SCRAPER - Ricerca per Combinazioni Materia+Classificazione")
    print("="*80)
    print(f"📁 Output: {output_path.absolute()}")
    print(f"📅 Anno: {anno}")
    print(f"🏛️  Ente: {ente}")
    print(f"🕐 Timestamp: {timestamp}\n")

    # Carica combinazioni
    print("📋 Caricamento combinazioni...")
    combinations = load_combinations(combinations_file)
    total_combinations = len(combinations)
    print(f"✓ Caricate {total_combinations} combinazioni\n")

    # File per tracciare combinazioni con 0 risultati
    zero_results_file = output_path / f"zero_results_{anno}_{timestamp}.json"
    zero_results = []

    # File risultati finali
    results_file = output_path / f"results_{anno}_{timestamp}.json"
    all_results = {
        'timestamp': timestamp,
        'anno': anno,
        'ente': ente,
        'total_combinations': total_combinations,
        'phases': []
    }

    driver = None

    try:
        driver = setup_driver(headless)

        # ============================================================
        # FASE 1: massime=false
        # ============================================================
        print("="*80)
        print("🔍 FASE 1: Ricerca con massime=false")
        print("="*80)

        phase1_results = []
        phase1_start = time.time()

        for i, combo in enumerate(combinations, 1):
            print(f"\n[{i}/{total_combinations}] Materia: {combo['materia_desc'][:40]}")
            print(f"              Classificazione: {combo['classificazione_desc'][:40]}")

            result = search_combination(
                driver,
                combo['materia_code'],
                combo['classificazione_code'],
                anno,
                ente,
                solo_massimate=False,
                max_pages=max_pages_per_search
            )

            num_risultati = result['num_risultati']

            if num_risultati == 0:
                print(f"              ⊘ 0 risultati (verrà saltata in fase 2)")
                zero_results.append({
                    'materia_code': combo['materia_code'],
                    'materia_desc': combo['materia_desc'],
                    'classificazione_code': combo['classificazione_code'],
                    'classificazione_desc': combo['classificazione_desc']
                })
            elif num_risultati > 0:
                print(f"              ✓ {num_risultati} risultati trovati")
            else:
                print(f"              ✗ Errore nella ricerca")

            phase1_results.append({
                'combination': combo,
                'num_risultati': num_risultati,
                'sentenze': result.get('sentenze', []),
                'metadata': result.get('metadata', {}),
                'error': result.get('error')
            })

            # Salva progressivamente
            if i % 50 == 0:
                print(f"\n💾 Salvataggio intermedio (processate {i}/{total_combinations})...")
                with open(zero_results_file, 'w', encoding='utf-8') as f:
                    json.dump(zero_results, f, ensure_ascii=False, indent=2)

            time.sleep(1)  # Pausa tra ricerche

        phase1_duration = time.time() - phase1_start

        # Salva risultati fase 1
        with open(zero_results_file, 'w', encoding='utf-8') as f:
            json.dump(zero_results, f, ensure_ascii=False, indent=2)

        print(f"\n✅ FASE 1 completata in {phase1_duration/60:.1f} minuti")
        print(f"📊 Combinazioni con 0 risultati: {len(zero_results)}/{total_combinations}")
        print(f"📊 Combinazioni con risultati: {total_combinations - len(zero_results)}")
        print(f"💾 File zero results: {zero_results_file}")

        all_results['phases'].append({
            'phase': 1,
            'massime': False,
            'duration_seconds': phase1_duration,
            'total_tested': total_combinations,
            'zero_results_count': len(zero_results),
            'results': phase1_results
        })

        # ============================================================
        # FASE 2: massime=true (SOLO per combinazioni con risultati)
        # ============================================================
        print("\n" + "="*80)
        print("🔍 FASE 2: Ricerca con massime=true (solo combinazioni con risultati)")
        print("="*80)

        # Filtra combinazioni: ESCLUDI quelle con 0 risultati
        zero_results_keys = {
            (zr['materia_code'], zr['classificazione_code'])
            for zr in zero_results
        }

        combinations_with_results = [
            combo for combo in combinations
            if (combo['materia_code'], combo['classificazione_code']) not in zero_results_keys
        ]

        total_phase2 = len(combinations_with_results)
        print(f"📋 Combinazioni da testare in fase 2: {total_phase2}\n")

        phase2_results = []
        phase2_start = time.time()

        for i, combo in enumerate(combinations_with_results, 1):
            print(f"\n[{i}/{total_phase2}] Materia: {combo['materia_desc'][:40]}")
            print(f"              Classificazione: {combo['classificazione_desc'][:40]}")

            result = search_combination(
                driver,
                combo['materia_code'],
                combo['classificazione_code'],
                anno,
                ente,
                solo_massimate=True,
                max_pages=max_pages_per_search
            )

            num_risultati = result['num_risultati']

            if num_risultati > 0:
                print(f"              ✓ {num_risultati} risultati (massimate) trovati")
            elif num_risultati == 0:
                print(f"              ⊘ 0 risultati (massimate)")
            else:
                print(f"              ✗ Errore nella ricerca")

            phase2_results.append({
                'combination': combo,
                'num_risultati': num_risultati,
                'sentenze': result.get('sentenze', []),
                'metadata': result.get('metadata', {}),
                'error': result.get('error')
            })

            time.sleep(1)

        phase2_duration = time.time() - phase2_start

        print(f"\n✅ FASE 2 completata in {phase2_duration/60:.1f} minuti")
        print(f"📊 Combinazioni testate: {total_phase2}")

        all_results['phases'].append({
            'phase': 2,
            'massime': True,
            'duration_seconds': phase2_duration,
            'total_tested': total_phase2,
            'skipped_zero_results': len(zero_results),
            'results': phase2_results
        })

        # ============================================================
        # Salvataggio finale
        # ============================================================
        print("\n" + "="*80)
        print("💾 Salvataggio risultati finali...")

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        print(f"✓ File risultati: {results_file}")

        # Statistiche finali
        total_duration = phase1_duration + phase2_duration

        print("\n" + "="*80)
        print("📊 STATISTICHE FINALI")
        print("="*80)
        print(f"⏱️  Tempo totale: {total_duration/60:.1f} minuti")
        print(f"📋 Combinazioni totali: {total_combinations}")
        print(f"⊘  Combinazioni con 0 risultati (saltate in fase 2): {len(zero_results)}")
        print(f"✓  Combinazioni con risultati: {total_phase2}")
        print(f"⚡ Ricerche risparmiate: {len(zero_results)} ({len(zero_results)/total_combinations*100:.1f}%)")

        # Conta sentenze totali
        total_sentenze_fase1 = sum(r['num_risultati'] for r in phase1_results if r['num_risultati'] > 0)
        total_sentenze_fase2 = sum(r['num_risultati'] for r in phase2_results if r['num_risultati'] > 0)

        print(f"\n📄 Sentenze trovate fase 1 (massime=false): {total_sentenze_fase1}")
        print(f"📄 Sentenze trovate fase 2 (massime=true): {total_sentenze_fase2}")

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
        description="MEF SCRAPER - Ricerca per combinazioni Materia+Classificazione"
    )
    parser.add_argument(
        "--combinations",
        type=str,
        default="pattern/mef/mef_by_classificazioni.json",
        help="File JSON con le combinazioni"
    )
    parser.add_argument(
        "--anno",
        type=str,
        required=True,
        help="Anno sentenze (es: 2022)"
    )
    parser.add_argument(
        "--ente",
        type=str,
        default="Corte di Cassazione",
        help="Autorità emanante"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="scraper/data/mef_combinations",
        help="Directory output"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Numero massimo pagine per ricerca (default: illimitato)"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Mostra browser"
    )

    args = parser.parse_args()

    scrape_by_combinations(
        combinations_file=args.combinations,
        anno=args.anno,
        ente=args.ente,
        output_dir=args.output,
        headless=not args.no_headless,
        max_pages_per_search=args.max_pages
    )


if __name__ == "__main__":
    main()
