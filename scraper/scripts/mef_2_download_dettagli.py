#!/usr/bin/env python3
"""
MEF SCRAPER - STEP 2: Download dettagli completi sentenze
Input: JSON lista sentenze (da step 1)
Output:
  - metadata JSON (compatibile con metadata_cassazione_YYYY.json)
  - file TXT per ogni sentenza
  - entities estratte dai link nel testo

Estrae:
- Testo completo sentenza
- Massima (principio di diritto)
- Intitolazione
- Entities (link a leggi, precedenti) già taggati nel testo
- Tab "Documenti citati"
"""

import os
import re
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def setup_driver(headless=True):
    """Configura driver Selenium"""
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


def extract_xml_dettaglio(driver):
    """Estrae XML dettaglio dalla variabile JavaScript 'xmlDettaglio'"""
    try:
        script = "return (typeof xmlDettaglio !== 'undefined') ? xmlDettaglio : null;"
        xml_string = driver.execute_script(script)

        if xml_string:
            xml_string = xml_string.replace('\\"', '"').replace('\\/', '/')
            return xml_string
        else:
            # Fallback: regex
            page_source = driver.page_source
            match = re.search(r"var xmlDettaglio = '(.+?)';", page_source, re.DOTALL)
            if match:
                xml_string = match.group(1)
                xml_string = xml_string.replace('\\/', '/').replace('\\"', '"')
                return xml_string
    except Exception as e:
        print(f"      ⚠️  Errore estrazione XML: {e}")

    return None


def extract_entities_from_html(html_text):
    """
    Estrae entities dai link presenti nel testo HTML
    I link sono nel formato: <a href="decodeurn?urn=...">testo</a>

    Returns:
        list: [{'type': 'normativa'/'giurisprudenza', 'urn': '...', 'text': '...', 'parsed': {...}}]
    """
    entities = []

    if not html_text:
        return entities

    try:
        soup = BeautifulSoup(html_text, 'html.parser')

        # Trova tutti i link con URN
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)

            if 'decodeurn?urn=' in href:
                # Estrai URN
                urn_match = re.search(r'urn=([^&"\']+)', href)
                if urn_match:
                    urn = urn_match.group(1)

                    # Parse URN per estrarre info strutturate
                    parsed = parse_urn(urn)

                    entity = {
                        'type': parsed.get('type', 'unknown'),
                        'urn': urn,
                        'text': text,
                        'parsed': parsed
                    }

                    entities.append(entity)

    except Exception as e:
        print(f"      ⚠️  Errore estrazione entities: {e}")

    return entities


def parse_urn(urn):
    """
    Parse URN per estrarre info strutturate

    Esempi:
      urn:doctrib::DLG:1995;504_art7 -> {'type': 'normativa', 'kind': 'DLG', 'year': 1995, 'number': 504, 'article': 7}
      urn:doctrib:CCO:SEN:2020;142 -> {'type': 'giurisprudenza', 'court': 'CCO', 'kind': 'SEN', 'year': 2020, 'number': 142}
    """
    parsed = {'raw_urn': urn}

    try:
        # URN format: urn:doctrib:[...]
        if not urn.startswith('urn:doctrib'):
            return parsed

        # Normativa: urn:doctrib::KIND:YEAR;NUMBER_artXX
        if '::' in urn:
            parsed['type'] = 'normativa'

            # Estrai kind (DLG, DPR, L, DL, ecc.)
            kind_match = re.search(r'::([A-Z]+):', urn)
            if kind_match:
                parsed['kind'] = kind_match.group(1)

            # Estrai anno e numero
            year_num_match = re.search(r':(\d{4});(\d+)', urn)
            if year_num_match:
                parsed['year'] = int(year_num_match.group(1))
                parsed['number'] = int(year_num_match.group(2))

            # Estrai articolo
            art_match = re.search(r'_art(\d+)', urn)
            if art_match:
                parsed['article'] = int(art_match.group(1))

            # Estrai comma
            com_match = re.search(r'-com(\d+)', urn)
            if com_match:
                parsed['comma'] = int(com_match.group(1))

        # Giurisprudenza: urn:doctrib:COURT:KIND:YEAR;NUMBER
        elif ':' in urn and '::' not in urn:
            parsed['type'] = 'giurisprudenza'

            parts = urn.split(':')
            if len(parts) >= 4:
                parsed['court'] = parts[2]  # CCO, CTR, CTP, ecc.
                parsed['kind'] = parts[3].split(';')[0]  # SEN, ORD, ecc.

                # Estrai anno e numero
                year_num = parts[3]
                year_num_match = re.search(r':(\d{4});(\d+)', year_num)
                if year_num_match:
                    parsed['year'] = int(year_num_match.group(1))
                    parsed['number'] = int(year_num_match.group(2))

    except Exception as e:
        pass

    return parsed


def extract_documenti_citati(driver):
    """
    Estrae contenuto del tab 'Documenti citati'
    Contiene altri riferimenti normativi e giurisprudenziali linkati

    Returns:
        dict: {'html': '...', 'entities': [...]}
    """
    try:
        # Trova il tab "Documenti citati" e cliccalo
        # Cerca per testo del titolo
        tabs = driver.find_elements(By.CSS_SELECTOR, ".tabnav .titolo")

        for tab in tabs:
            if "Documenti citati" in tab.text:
                tab.click()
                time.sleep(1)
                break

        # Estrai contenuto
        contenuto_citati = driver.find_element(By.CSS_SELECTOR, ".tabnav .contenuto.citati")
        html_citati = contenuto_citati.get_attribute('innerHTML')

        # Estrai entities dai link
        entities = extract_entities_from_html(html_citati)

        return {
            'html': html_citati,
            'entities': entities
        }

    except Exception as e:
        print(f"      ⚠️  Errore estrazione documenti citati: {e}")
        return {'html': '', 'entities': []}


def parse_xml_dettaglio(xml_string, driver=None):
    """
    Parse XML dettaglio completo

    Returns:
        dict: {
            'id': '...',
            'estremi': '...',
            'intitolazione': '...',
            'intitolazione_html': '...',
            'massima': '...',
            'massima_html': '...',
            'testo': '...',
            'testo_html': '...',
            'entities_testo': [...],
            'entities_massima': [...],
            'documenti_citati': {...},
            'metadata': {...}
        }
    """
    if not xml_string:
        return None

    try:
        root = ET.fromstring(xml_string)

        prov = root.find('.//Provvedimento')
        if prov is None:
            return None

        id_prov = prov.get('idProvvedimento', '')
        sentenza_sicot = prov.get('sentenzaSicot', 'false')
        flag_stato = prov.get('flagStato', '0')
        allegato = prov.get('allegato', 'false')

        estremi_elem = prov.find('estremi')
        estremi = estremi_elem.text if estremi_elem is not None else ''

        # Intitolazione
        intitolazione_elem = prov.find('.//intitolazione')
        intitolazione_html = ''
        intitolazione_text = ''
        if intitolazione_elem is not None:
            intitolazione_html = ''.join(ET.tostring(child, encoding='unicode', method='html') for child in intitolazione_elem)
            intitolazione_text = ''.join(intitolazione_elem.itertext()).strip()

        # Massima
        massima_elem = prov.find('.//massima')
        massima_html = ''
        massima_text = ''
        entities_massima = []
        if massima_elem is not None:
            massima_html = ''.join(ET.tostring(child, encoding='unicode', method='html') for child in massima_elem)
            massima_text = ''.join(massima_elem.itertext()).strip()
            entities_massima = extract_entities_from_html(massima_html)

        # Testo completo
        testo_elem = prov.find('.//testo')
        testo_html = ''
        testo_text = ''
        entities_testo = []
        if testo_elem is not None:
            testo_html = ''.join(ET.tostring(child, encoding='unicode', method='html') for child in testo_elem)
            testo_text = ''.join(testo_elem.itertext()).strip()
            entities_testo = extract_entities_from_html(testo_html)

        # Documenti citati (se driver disponibile)
        documenti_citati = {'html': '', 'entities': []}
        if driver:
            documenti_citati = extract_documenti_citati(driver)

        return {
            'id': id_prov,
            'estremi': estremi,
            'intitolazione': intitolazione_text,
            'intitolazione_html': intitolazione_html,
            'massima': massima_text,
            'massima_html': massima_html,
            'testo': testo_text,
            'testo_html': testo_html,
            'entities_testo': entities_testo,
            'entities_massima': entities_massima,
            'documenti_citati': documenti_citati,
            'metadata': {
                'sentenza_sicot': sentenza_sicot == 'true',
                'flag_stato': int(flag_stato),
                'allegato': allegato == 'true'
            }
        }

    except Exception as e:
        print(f"      ⚠️  Errore parsing XML dettaglio: {e}")
        import traceback
        traceback.print_exc()
        return None


def parse_estremi(estremi_str):
    """
    Parse stringa estremi per estrarre campi strutturati

    Esempio: "Sentenza del 30/12/2022 n. 38131 - Corte di Cassazione - Sezione/Collegio 5"

    Returns:
        dict: {
            'tipo_provvedimento': 'Sentenza',
            'data_pubblicazione': '30/12/2022',
            'numero': '38131',
            'autorita': 'Corte di Cassazione',
            'sezione': '5',
            'anno': '2022'
        }
    """
    parsed = {}

    try:
        # Tipo provvedimento
        tipo_match = re.match(r'(Sentenza|Ordinanza|Decreto)', estremi_str, re.IGNORECASE)
        if tipo_match:
            parsed['tipo_provvedimento'] = tipo_match.group(1)

        # Data
        data_match = re.search(r'del (\d{2}/\d{2}/\d{4})', estremi_str)
        if data_match:
            data = data_match.group(1)
            parsed['data_pubblicazione'] = data
            # Estrai anno dalla data
            anno = data.split('/')[-1]
            parsed['anno'] = anno

        # Numero
        numero_match = re.search(r'n\.\s*(\d+)', estremi_str)
        if numero_match:
            parsed['numero'] = numero_match.group(1)

        # Autorità
        if '-' in estremi_str:
            parts = estremi_str.split('-')
            if len(parts) >= 2:
                autorita = parts[1].strip()
                parsed['autorita'] = autorita

        # Sezione
        sezione_match = re.search(r'Sezione/?Collegio\s+(\d+|[IVXLC]+)', estremi_str)
        if sezione_match:
            parsed['sezione'] = sezione_match.group(1)

    except Exception as e:
        pass

    return parsed


def create_txt_content(dettaglio):
    """
    Crea contenuto TXT formattato (compatibile con formato Cassazione)
    """
    parsed_estremi = parse_estremi(dettaglio['estremi'])

    lines = []
    lines.append("=" * 70)

    # Header simile a Cassazione
    tipo = parsed_estremi.get('tipo_provvedimento', 'Sentenza')
    numero = parsed_estremi.get('numero', '?')
    anno = parsed_estremi.get('anno', '?')
    autorita = parsed_estremi.get('autorita', '?')
    sezione = parsed_estremi.get('sezione', '?')

    lines.append(f"{autorita} {tipo} Num. {numero}  Anno {anno}")
    if sezione:
        lines.append(f"Sezione: {sezione}")

    data_pub = parsed_estremi.get('data_pubblicazione', '')
    if data_pub:
        lines.append(f"Data pubblicazione: {data_pub}")

    lines.append("=" * 70)
    lines.append("")

    # Intitolazione
    if dettaglio.get('intitolazione'):
        lines.append(dettaglio['intitolazione'])
        lines.append("")

    # Massima (se presente)
    if dettaglio.get('massima'):
        lines.append("MASSIMA")
        lines.append("-" * 70)
        lines.append(dettaglio['massima'])
        lines.append("")

    # Testo completo
    if dettaglio.get('testo'):
        lines.append("TESTO COMPLETO")
        lines.append("-" * 70)
        lines.append(dettaglio['testo'])

    return '\n'.join(lines)


def create_metadata_entry(sentenza_base, dettaglio):
    """
    Crea entry metadata compatibile con formato metadata_cassazione_YYYY.json
    """
    parsed_estremi = parse_estremi(dettaglio['estremi'])

    # Genera ID compatibile (usando GUID MEF)
    id_mef = dettaglio['id'].replace('{', '').replace('}', '').replace('-', '')[:16]
    tipo_code = parsed_estremi.get('tipo_provvedimento', 'S')[0].upper()  # S, O, D
    anno = parsed_estremi.get('anno', '????')
    numero = parsed_estremi.get('numero', '0')

    # ID format: mef{anno}{sezione}{numero}{tipo}
    sezione = parsed_estremi.get('sezione', '0')
    sentence_id = f"mef{anno}{sezione}{numero}{tipo_code}"

    entry = {
        'id': sentence_id,
        'id_mef_guid': dettaglio['id'],  # Mantieni GUID originale
        'url': sentenza_base['url'],
        'fonte': 'MEF - Ministero Economia e Finanze',
        'autorita': parsed_estremi.get('autorita', ''),
        'sezione': parsed_estremi.get('sezione', ''),
        'tipo_provvedimento': parsed_estremi.get('tipo_provvedimento', ''),
        'numero': parsed_estremi.get('numero', ''),
        'anno': parsed_estremi.get('anno', ''),
        'data_pubblicazione': parsed_estremi.get('data_pubblicazione', ''),
        'estremi': dettaglio['estremi'],
        'intitolazione': dettaglio.get('intitolazione', ''),
        'has_massima': bool(dettaglio.get('massima')),
        'massima': dettaglio.get('massima', ''),
        'entities_count': len(dettaglio.get('entities_testo', [])) + len(dettaglio.get('entities_massima', [])),
        'entities_testo': dettaglio.get('entities_testo', []),
        'entities_massima': dettaglio.get('entities_massima', []),
        'documenti_citati_count': len(dettaglio.get('documenti_citati', {}).get('entities', [])),
        'metadata': dettaglio.get('metadata', {})
    }

    return entry


def download_dettagli(input_file, output_json, output_txt_dir, delay=2, headless=True):
    """
    Download dettagli completi per ogni sentenza nella lista

    Args:
        input_file: JSON lista sentenze (output step 1)
        output_json: File JSON output metadata
        output_txt_dir: Directory output TXT files
        delay: Secondi tra richieste
        headless: Modalità headless
    """
    print("🚀 MEF SCRAPER - STEP 2: Download Dettagli")
    print("="*70)

    # Carica lista sentenze
    with open(input_file, 'r', encoding='utf-8') as f:
        lista_data = json.load(f)

    sentenze = lista_data.get('sentenze', [])
    total = len(sentenze)

    print(f"📋 Sentenze da elaborare: {total}")
    print(f"📁 Output JSON: {output_json}")
    print(f"📁 Output TXT: {output_txt_dir}\n")

    # Crea directory TXT
    txt_path = Path(output_txt_dir)
    txt_path.mkdir(parents=True, exist_ok=True)

    # Setup driver
    driver = setup_driver(headless)

    metadata = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'anno': lista_data['filters'].get('anno', ''),
            'total_sentences': 0,
            'fonte': 'MEF - def.finanze.it',
            'filters': lista_data['filters']
        },
        'sentences': []
    }

    processed = 0
    errors = 0

    try:
        for i, sentenza in enumerate(sentenze, 1):
            print(f"[{i}/{total}] {sentenza['estremi'][:60]}...")

            try:
                # Vai alla pagina dettaglio
                driver.get(sentenza['url'])
                time.sleep(delay)

                # Estrai XML dettaglio
                xml_dettaglio = extract_xml_dettaglio(driver)
                if not xml_dettaglio:
                    print(f"      ✗ XML non trovato")
                    errors += 1
                    continue

                # Parse dettaglio
                dettaglio = parse_xml_dettaglio(xml_dettaglio, driver)
                if not dettaglio:
                    print(f"      ✗ Parsing fallito")
                    errors += 1
                    continue

                # Crea entry metadata
                entry = create_metadata_entry(sentenza, dettaglio)
                metadata['sentences'].append(entry)

                # Salva TXT
                txt_content = create_txt_content(dettaglio)
                txt_file = txt_path / f"{entry['id']}.txt"
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(txt_content)

                print(f"      ✓ Salvato: {entry['id']}.txt")
                print(f"      ✓ Entities: {entry['entities_count']} (testo: {len(entry['entities_testo'])}, massima: {len(entry['entities_massima'])})")
                print(f"      ✓ Documenti citati: {entry['documenti_citati_count']}")

                processed += 1

            except Exception as e:
                print(f"      ✗ Errore: {e}")
                errors += 1
                continue

        # Aggiorna totale
        metadata['metadata']['total_sentences'] = processed
        metadata['metadata']['errors'] = errors

        # Salva metadata JSON
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Download completato!")
        print(f"📊 Processate: {processed}/{total}")
        print(f"❌ Errori: {errors}")
        print(f"📁 Metadata: {output_json}")
        print(f"📁 TXT files: {txt_path}")

    finally:
        driver.quit()

    return metadata


def main():
    parser = argparse.ArgumentParser(
        description="MEF SCRAPER - STEP 2: Download dettagli sentenze"
    )
    parser.add_argument("--input", required=True, help="JSON lista sentenze (da step 1)")
    parser.add_argument("--output-json", required=True, help="File output metadata JSON")
    parser.add_argument("--output-txt", required=True, help="Directory output TXT")
    parser.add_argument("--delay", type=float, default=2.0, help="Secondi tra richieste")
    parser.add_argument("--no-headless", action="store_true", help="Mostra browser")

    args = parser.parse_args()

    download_dettagli(
        input_file=args.input,
        output_json=args.output_json,
        output_txt_dir=args.output_txt,
        delay=args.delay,
        headless=not args.no_headless
    )


if __name__ == "__main__":
    main()
