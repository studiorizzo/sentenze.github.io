#!/usr/bin/env python3
"""
STEP 2: Parse HTML to JSON
Estrae i metadata dalle pagine HTML e li salva in metadata/metadata_cassazione.json
"""

import os
import json
import re
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import unquote
from datetime import datetime


def extract_sentence_from_card(card_div):
    """Estrae i metadata di una singola sentenza da un div.card"""
    try:
        # ID univoco sentenza
        sentence_id_span = card_div.find('span', {'data-role': 'content', 'data-arg': 'id'})
        if not sentence_id_span:
            return None

        sentence_id = sentence_id_span.get_text(strip=True)

        # Link PDF
        pdf_link_img = card_div.find('img', {'alt': 'formato pdf'})
        pdf_url = None
        if pdf_link_img and pdf_link_img.get('data-arg'):
            pdf_path = unquote(pdf_link_img['data-arg'])
            # Rimuovi l'encoding URL manuale e costruisci l'URL completo
            pdf_url = f"https://www.italgiure.giustizia.it{pdf_path}"

        # Estrai tutti i metadata usando data-arg
        def get_field(arg_name):
            span = card_div.find('span', {'data-role': 'content', 'data-arg': arg_name})
            return span.get_text(strip=True) if span else None

        metadata = {
            'id': sentence_id,
            'sezione': get_field('szdec'),
            'archivio': get_field('kind'),
            'tipo_provvedimento': get_field('tipoprov'),
            'numero': get_field('numcard'),
            'data_pubblicazione': get_field('datdep'),
            'ecli': get_field('ecli'),
            'anno': get_field('anno'),
            'data_udienza': get_field('datdec'),
            'presidente': get_field('presidente'),
            'relatore': get_field('relatore'),
            'pdf_url': pdf_url,
        }

        # Pulisci ECLI (rimuovi spazi e parentesi)
        if metadata['ecli']:
            metadata['ecli'] = metadata['ecli'].strip().replace('(', '').replace(')', '')

        return metadata

    except Exception as e:
        print(f"Errore estrazione metadata: {e}")
        return None


def parse_html_file(html_path):
    """Parsa un file HTML e restituisce la lista delle sentenze"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Trova tutti i div con class="card"
        cards = soup.find_all('div', class_='card')

        sentences = []
        for card in cards:
            metadata = extract_sentence_from_card(card)
            if metadata and metadata['id']:
                sentences.append(metadata)

        return sentences

    except Exception as e:
        print(f"✗ Errore parsing {html_path.name}: {e}")
        return []


def parse_all_html_files(html_dir, output_json):
    """
    Parsa tutti i file HTML e genera il JSON dei metadata

    Args:
        html_dir: Directory contenente i file HTML
        output_json: Percorso del file JSON di output
    """
    html_path = Path(html_dir)
    if not html_path.exists():
        print(f"✗ Directory non trovata: {html_dir}")
        return

    # Trova tutti i file HTML
    html_files = sorted(html_path.glob('*.html'))
    if not html_files:
        print(f"✗ Nessun file HTML trovato in {html_dir}")
        return

    print(f"🚀 Parsing HTML → JSON")
    print(f"📁 Input:  {html_path.absolute()}")
    print(f"📄 File HTML: {len(html_files)}")
    print(f"💾 Output: {output_json}\n")

    all_sentences = []
    sentence_ids = set()

    for html_file in html_files:
        print(f"📖 {html_file.name}...", end=" ")

        sentences = parse_html_file(html_file)

        # Evita duplicati (può capitare se scarichi la stessa pagina più volte)
        new_count = 0
        for sent in sentences:
            if sent['id'] not in sentence_ids:
                all_sentences.append(sent)
                sentence_ids.add(sent['id'])
                new_count += 1

        print(f"✓ {new_count} sentenze")

    # Ordina per ID (che contiene la data e il numero)
    all_sentences.sort(key=lambda x: x['id'], reverse=True)

    # Prepara il JSON finale
    output_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_sentences': len(all_sentences),
            'html_files_processed': len(html_files),
            'source': 'italgiure.giustizia.it',
            'filters': 'CIVILE - QUINTA SEZIONE'
        },
        'sentences': all_sentences
    }

    # Salva il JSON
    output_path = Path(output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Parsing completato!")
    print(f"📊 Sentenze totali: {len(all_sentences)}")
    print(f"💾 JSON salvato in: {output_path.absolute()}")

    # Mostra alcune statistiche
    if all_sentences:
        print(f"\n📈 Statistiche:")
        print(f"   - Prima sentenza: {all_sentences[-1]['id']} ({all_sentences[-1]['data_pubblicazione']})")
        print(f"   - Ultima sentenza: {all_sentences[0]['id']} ({all_sentences[0]['data_pubblicazione']})")

        # Conta per tipo
        tipi = {}
        for s in all_sentences:
            tipo = s['tipo_provvedimento']
            tipi[tipo] = tipi.get(tipo, 0) + 1

        print(f"\n   Tipi provvedimenti:")
        for tipo, count in sorted(tipi.items(), key=lambda x: -x[1]):
            print(f"   - {tipo}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="STEP 2: Parsa HTML e genera JSON dei metadata"
    )
    parser.add_argument(
        "--html-dir",
        type=str,
        default="scraper/data/html",
        help="Directory con i file HTML (default: scraper/data/html)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="metadata/metadata_cassazione.json",
        help="File JSON di output (default: metadata/metadata_cassazione.json)"
    )

    args = parser.parse_args()

    parse_all_html_files(args.html_dir, args.output)


if __name__ == "__main__":
    main()
