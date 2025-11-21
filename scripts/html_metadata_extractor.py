#!/usr/bin/env python3
"""
HTML Metadata Extractor - Step 0
Estrae metadata strutturati dagli HTML delle sentenze
"""

from bs4 import BeautifulSoup
import json
import re
from pathlib import Path
from typing import Dict, List

def extract_sentenze_from_html(html_path: Path) -> List[Dict]:
    """
    Estrae metadata di tutte le sentenze da un file HTML

    Args:
        html_path: Path al file HTML

    Returns:
        Lista di dizionari con metadata sentenze
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    cards = soup.find_all('div', class_='card')

    sentenze = []

    for card in cards:
        sentenza = {}

        # ID univoco (es: snciv2025530039O)
        id_elem = card.find('span', {'data-role': 'content', 'data-arg': 'id'})
        if not id_elem:
            continue
        sentenza['id'] = id_elem.text.strip()

        # Link PDF
        pdf_elem = card.find('img', class_='pdf')
        if pdf_elem and pdf_elem.get('data-arg'):
            pdf_path = pdf_elem['data-arg']
            # Decodifica URL encoding
            pdf_path = pdf_path.replace('%3F', '?').replace('%3D', '=').replace('%26', '&').replace('%2F', '/')
            sentenza['pdf_url'] = f"https://www.italgiure.giustizia.it{pdf_path}"
            sentenza['pdf_path_relative'] = pdf_path

            # Estrai nome file PDF
            match = re.search(r'(sn(?:civ|pen)@[^/]+\.clean\.pdf)', pdf_path)
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

        # Tipo provvedimento (Ordinanza/Decreto/Sentenza)
        tipoprov_elem = card.find('span', {'data-role': 'content', 'data-arg': 'tipoprov'})
        if tipoprov_elem:
            sentenza['tipo_provvedimento'] = tipoprov_elem.text.strip()

        # Numero
        numcard_elem = card.find('span', {'data-role': 'content', 'data-arg': 'numcard'})
        if numcard_elem:
            sentenza['numero'] = numcard_elem.text.strip()

        # Anno
        anno_elem = card.find('span', {'data-role': 'content', 'data-arg': 'anno'})
        if anno_elem:
            sentenza['anno'] = int(anno_elem.text.strip())

        # Data deposito/pubblicazione
        datdep_elem = card.find('span', {'data-role': 'content', 'data-arg': 'datdep'})
        if datdep_elem:
            sentenza['data_deposito'] = datdep_elem.text.strip()

        # Data udienza/decisione
        datdec_elem = card.find('span', {'data-role': 'content', 'data-arg': 'datdec'})
        if datdec_elem:
            sentenza['data_decisione'] = datdec_elem.text.strip()

        # Oggetto
        oggetto_elem = card.find('span', {'data-role': 'content', 'data-arg': 'oggetto'})
        if oggetto_elem:
            sentenza['oggetto'] = oggetto_elem.text.strip()

        # Presidente
        pres_elem = card.find('span', {'data-role': 'content', 'data-arg': 'pres'})
        if pres_elem:
            sentenza['presidente'] = pres_elem.text.strip()

        # Relatore
        rel_elem = card.find('span', {'data-role': 'content', 'data-arg': 'rel'})
        if rel_elem:
            sentenza['relatore'] = rel_elem.text.strip()

        sentenze.append(sentenza)

    return sentenze


def save_metadata(sentenza: Dict, output_dir: Path):
    """Salva metadata di una singola sentenza in JSON"""
    output_path = output_dir / f"{sentenza['id']}_metadata.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sentenza, f, ensure_ascii=False, indent=2)

    return output_path


def process_all_html(html_dir: Path, output_dir: Path) -> Dict:
    """
    Processa tutti gli HTML e genera metadata JSON

    Args:
        html_dir: Directory con file HTML
        output_dir: Directory output per JSON

    Returns:
        Statistiche processing
    """
    html_files = sorted(html_dir.glob('*.html'))

    all_sentenze = []
    total_processed = 0

    for html_file in html_files:
        print(f"📄 Processing: {html_file.name}")
        sentenze = extract_sentenze_from_html(html_file)

        print(f"   → {len(sentenze)} sentenze trovate")

        for sentenza in sentenze:
            save_metadata(sentenza, output_dir)
            all_sentenze.append(sentenza)
            total_processed += 1

    # Salva anche un file aggregato
    summary_path = output_dir / "_all_sentenze.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(all_sentenze, f, ensure_ascii=False, indent=2)

    return {
        'total_html': len(html_files),
        'total_sentenze': total_processed,
        'summary_file': str(summary_path)
    }


if __name__ == '__main__':
    print("="*80)
    print("HTML METADATA EXTRACTOR - Step 0")
    print("="*80)
    print()

    # Directory
    html_dir = Path('data/html')
    output_dir = Path('metadata')
    output_dir.mkdir(exist_ok=True)

    # Process
    stats = process_all_html(html_dir, output_dir)

    print("\n" + "="*80)
    print("RISULTATI:")
    print("="*80)
    print(f"HTML processati: {stats['total_html']}")
    print(f"Sentenze estratte: {stats['total_sentenze']}")
    print(f"Metadata JSON generati: {stats['total_sentenze']} file")
    print(f"File aggregato: {stats['summary_file']}")
    print("="*80)
