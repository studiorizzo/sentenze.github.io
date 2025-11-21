#!/usr/bin/env python3
"""
Test completo del pipeline: HTML -> metadati -> download PDF -> estrazione testo
"""

from bs4 import BeautifulSoup
import json
import re
import pymupdf
import requests
import os
from pathlib import Path
import time


def parse_sentenze_html(html_path):
    """Estrae tutti i metadati delle sentenze da un file HTML"""

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    cards = soup.find_all('div', class_='card')

    sentenze = []

    for card in cards:
        sentenza = {}

        # ID univoco
        id_elem = card.find('span', {'data-role': 'content', 'data-arg': 'id'})
        if id_elem:
            sentenza['id'] = id_elem.text.strip()

        # Link al PDF
        pdf_elem = card.find('img', class_='pdf')
        if pdf_elem and pdf_elem.get('data-arg'):
            pdf_path = pdf_elem['data-arg']
            pdf_path = pdf_path.replace('%3F', '?').replace('%3D', '=').replace('%26', '&').replace('%2F', '/')
            sentenza['pdf_url'] = f"https://www.italgiure.giustizia.it{pdf_path}"
            sentenza['pdf_path_relative'] = pdf_path

            if 'snciv@' in pdf_path or 'snpen@' in pdf_path:
                match = re.search(r'(sn(?:civ|pen)@[^/]+\.pdf)', pdf_path)
                if match:
                    sentenza['pdf_filename'] = match.group(1)

        # Sezione
        szdec_elem = card.find('span', {'data-role': 'content', 'data-arg': 'szdec'})
        if szdec_elem:
            sentenza['sezione'] = szdec_elem.text.strip()

        # Tipo archivio (CIVILE/PENALE)
        kind_elem = card.find('span', {'data-role': 'content', 'data-arg': 'kind'})
        if kind_elem:
            sentenza['archivio'] = kind_elem.text.strip()

        # Tipo provvedimento
        tipoprov_elem = card.find('span', {'data-role': 'content', 'data-arg': 'tipoprov'})
        if tipoprov_elem:
            sentenza['tipo_provvedimento'] = tipoprov_elem.text.strip()

        # Numero sentenza
        numcard_elem = card.find('span', {'data-role': 'content', 'data-arg': 'numcard'})
        if numcard_elem:
            sentenza['numero'] = numcard_elem.text.strip()

        # Anno
        anno_elem = card.find('span', {'data-role': 'content', 'data-arg': 'anno'})
        if anno_elem:
            sentenza['anno'] = anno_elem.text.strip()

        # Data deposito/pubblicazione
        datdep_elem = card.find('span', {'data-role': 'content', 'data-arg': 'datdep'})
        if datdep_elem:
            sentenza['data_deposito'] = datdep_elem.text.strip()

        # Data udienza/decisione
        datdec_elem = card.find('span', {'data-role': 'content', 'data-arg': 'datdec'})
        if datdec_elem:
            sentenza['data_udienza'] = datdec_elem.find('span').text.strip() if datdec_elem.find('span') else datdec_elem.text.strip()

        # ECLI
        ecli_elem = card.find('span', {'data-role': 'content', 'data-arg': 'ecli'})
        if ecli_elem:
            sentenza['ecli'] = ecli_elem.text.strip()

        # Presidente
        presidente_elem = card.find('span', {'data-role': 'content', 'data-arg': 'presidente'})
        if presidente_elem:
            sentenza['presidente'] = presidente_elem.text.strip()

        # Relatore
        relatore_elem = card.find('span', {'data-role': 'content', 'data-arg': 'relatore'})
        if relatore_elem:
            sentenza['relatore'] = relatore_elem.text.strip()

        sentenze.append(sentenza)

    return sentenze


def download_pdf(url, output_path, timeout=30):
    """Scarica un PDF da URL"""
    try:
        print(f"  📥 Downloading from: {url}")

        # Header per simulare un browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.italgiure.giustizia.it/sncass/'
        }

        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return True
    except Exception as e:
        print(f"  ❌ Error downloading: {e}")
        return False


def extract_text_from_pdf(pdf_path):
    """Estrae il testo completo da un PDF"""
    try:
        doc = pymupdf.open(pdf_path)

        full_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            full_text += text + "\n\n"

        doc.close()

        return {
            'success': True,
            'num_pages': len(doc),
            'text': full_text.strip(),
            'text_length': len(full_text.strip())
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def main():
    print("="*80)
    print("TEST COMPLETO PIPELINE: HTML → Metadati → Download PDF → Estrazione Testo")
    print("="*80)

    html_file = '/home/user/sentenze.github.io/html/pagina 1 di 5563.html'
    pdf_output_dir = Path('/home/user/sentenze.github.io/test_pdf_downloads')
    pdf_output_dir.mkdir(exist_ok=True)

    # Step 1: Estrai metadati dall'HTML
    print("\n📋 Step 1: Estrazione metadati dall'HTML...")
    sentenze = parse_sentenze_html(html_file)
    print(f"✅ Estratte {len(sentenze)} sentenze")

    # Step 2: Testa il download e l'estrazione per le prime 3 sentenze
    print("\n📥 Step 2: Test download e estrazione testo (prime 3 sentenze)...")
    print("-"*80)

    results = []

    for i, sentenza in enumerate(sentenze[:3], 1):  # Solo prime 3 per test
        print(f"\n[{i}/3] Sentenza {sentenza.get('numero', 'N/A')}/{sentenza.get('anno', 'N/A')}")
        print(f"  ID: {sentenza.get('id', 'N/A')}")

        pdf_url = sentenza.get('pdf_url')
        if not pdf_url:
            print("  ⚠️  Nessun URL PDF trovato")
            continue

        # Nome file per il download
        pdf_filename = sentenza.get('pdf_filename', f"sentenza_{i}.pdf")
        pdf_local_path = pdf_output_dir / pdf_filename

        # Download PDF
        if download_pdf(pdf_url, pdf_local_path):
            file_size = os.path.getsize(pdf_local_path)
            print(f"  ✅ Download completato: {file_size:,} bytes")

            # Estrazione testo
            print(f"  📄 Estrazione testo...")
            result = extract_text_from_pdf(pdf_local_path)

            if result['success']:
                print(f"  ✅ Testo estratto: {result['text_length']:,} caratteri, {result['num_pages']} pagine")

                # Preview del testo
                preview = result['text'][:300].replace('\n', ' ')
                print(f"  📖 Preview: {preview}...")

                # Salva risultato
                results.append({
                    'sentenza': sentenza,
                    'pdf_local_path': str(pdf_local_path),
                    'pdf_size_bytes': file_size,
                    'extraction_result': {
                        'num_pages': result['num_pages'],
                        'text_length': result['text_length'],
                        'text': result['text']
                    }
                })
            else:
                print(f"  ❌ Errore estrazione: {result['error']}")

        # Pausa tra i download per non sovraccaricare il server
        if i < 3:
            time.sleep(2)

    # Step 3: Salva i risultati
    print("\n" + "="*80)
    print("📊 RIEPILOGO RISULTATI")
    print("="*80)

    output_file = pdf_output_dir / 'test_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Elaborati: {len(results)} PDF")
    print(f"💾 Risultati salvati in: {output_file}")

    # Statistiche
    if results:
        total_chars = sum(r['extraction_result']['text_length'] for r in results)
        total_pages = sum(r['extraction_result']['num_pages'] for r in results)
        total_size = sum(r['pdf_size_bytes'] for r in results)

        print(f"\n📈 Statistiche:")
        print(f"  - Totale caratteri estratti: {total_chars:,}")
        print(f"  - Totale pagine: {total_pages}")
        print(f"  - Dimensione totale PDF: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
        print(f"  - Media caratteri per sentenza: {total_chars//len(results):,}")
        print(f"  - Media pagine per sentenza: {total_pages//len(results):.1f}")

    print("\n" + "="*80)
    print("✅ TEST COMPLETATO!")
    print("="*80)


if __name__ == '__main__':
    main()
