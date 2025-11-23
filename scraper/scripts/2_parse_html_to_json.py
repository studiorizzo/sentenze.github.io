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


def load_existing_json(output_json):
    """Carica JSON esistente se presente"""
    output_path = Path(output_json)
    if output_path.exists():
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('sentences', []), set(s['id'] for s in data.get('sentences', []))
        except Exception as e:
            print(f"⚠️  Errore caricamento JSON esistente: {e}")
    return [], set()


def parse_all_html_files(html_dir, output_json, delete_html_after=False, filter_year=None):
    """
    Parsa tutti i file HTML e aggiorna il JSON dei metadata (incrementale)

    Args:
        html_dir: Directory contenente i file HTML
        output_json: Percorso del file JSON di output
        delete_html_after: Se True, cancella gli HTML dopo parsing riuscito
        filter_year: Se specificato, filtra solo sentenze di quell'anno
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

    print(f"🚀 Parsing HTML → JSON (Aggiornamento Incrementale)")
    print(f"📁 Input:  {html_path.absolute()}")
    print(f"📄 File HTML: {len(html_files)}")
    if filter_year:
        print(f"🔍 Filtro anno: {filter_year}")
    print(f"💾 Output: {output_json}\n")

    # Carica sentenze esistenti
    all_sentences, sentence_ids = load_existing_json(output_json)
    existing_count = len(all_sentences)

    if existing_count > 0:
        print(f"📚 Sentenze già presenti in JSON: {existing_count}")

    new_sentences_count = 0
    filtered_count = 0

    for html_file in html_files:
        print(f"📖 {html_file.name}...", end=" ")

        sentences = parse_html_file(html_file)

        # Aggiungi solo sentenze nuove (aggiornamento incrementale) con filtro anno
        new_count = 0
        for sent in sentences:
            # Filtra per anno se specificato
            if filter_year and sent.get('anno') != filter_year:
                filtered_count += 1
                continue

            if sent['id'] not in sentence_ids:
                all_sentences.append(sent)
                sentence_ids.add(sent['id'])
                new_count += 1
                new_sentences_count += 1

        print(f"✓ {len(sentences)} trovate, {new_count} nuove{f', {len(sentences) - new_count} filtrate' if filter_year else ''}")

    # Ordina per ID (che contiene la data e il numero)
    all_sentences.sort(key=lambda x: x['id'], reverse=True)

    # Prepara il JSON finale
    output_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'last_update': datetime.now().isoformat(),
            'total_sentences': len(all_sentences),
            'new_sentences_added': new_sentences_count,
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
    print(f"📊 Sentenze totali: {len(all_sentences)} ({existing_count} esistenti + {new_sentences_count} nuove)")
    print(f"💾 JSON salvato in: {output_path.absolute()}")

    # Cancella HTML se richiesto e parsing riuscito
    if delete_html_after and new_sentences_count >= 0:  # >= 0 per cancellare anche se nessuna nuova
        print(f"\n🗑️  Cancellazione file HTML...")
        deleted_count = 0
        for html_file in html_files:
            try:
                html_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"   ✗ Errore cancellazione {html_file.name}: {e}")
        print(f"   ✓ {deleted_count}/{len(html_files)} file HTML cancellati")

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


def parse_all_html_to_json_by_year(html_dir, output_dir="metadata", delete_html_after=False):
    """
    Parsa tutti gli HTML e genera JSON separati per ogni anno.
    Strategia efficiente: UN solo download HTML, TUTTI i JSON generati!
    """
    html_path = Path(html_dir)
    if not html_path.exists():
        print(f"✗ Directory non trovata: {html_dir}")
        return

    html_files = sorted(html_path.glob('*.html'))
    if not html_files:
        print(f"✗ Nessun file HTML trovato in {html_dir}")
        return

    print(f"🚀 Parsing HTML → JSON per Anno (strategia efficiente)")
    print(f"📁 Input:  {html_path.absolute()}")
    print(f"📄 File HTML: {len(html_files)}")
    print(f"💾 Output: {output_dir}/metadata_cassazione_YYYY.json\n")

    # Raggruppa sentenze per anno
    sentences_by_year = {}
    total_parsed = 0

    for html_file in html_files:
        print(f"📖 {html_file.name}...", end=" ")
        sentences = parse_html_file(html_file)

        for sent in sentences:
            year = sent.get('anno', 'unknown')
            if year not in sentences_by_year:
                sentences_by_year[year] = {}

            # Usa ID come chiave per evitare duplicati
            sentences_by_year[year][sent['id']] = sent
            total_parsed += 1

        print(f"✓ {len(sentences)} sentenze")

    print(f"\n📊 Totale sentenze parsate: {total_parsed}")
    print(f"📅 Anni trovati: {sorted(sentences_by_year.keys())}\n")

    # Genera un JSON per ogni anno
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for year in sorted(sentences_by_year.keys()):
        # Converti dict a list e ordina per ID decrescente
        year_sentences = list(sentences_by_year[year].values())
        year_sentences.sort(key=lambda x: x['id'], reverse=True)

        output_json = output_path / f"metadata_cassazione_{year}.json"

        output_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'anno': year,
                'total_sentences': len(year_sentences),
                'source': 'italgiure.giustizia.it',
                'filters': 'CIVILE - QUINTA SEZIONE'
            },
            'sentences': year_sentences
        }

        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"   ✅ {year}: {len(year_sentences):4d} sentenze → {output_json.name}")

    # Cancella HTML se richiesto
    if delete_html_after:
        print(f"\n🗑️  Cancellazione file HTML...")
        deleted_count = 0
        for html_file in html_files:
            try:
                html_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"   ✗ Errore: {html_file.name}: {e}")
        print(f"   ✓ {deleted_count}/{len(html_files)} file cancellati")

    print(f"\n✅ Completato! Generati {len(sentences_by_year)} JSON divisi per anno")


def main():
    parser = argparse.ArgumentParser(
        description="STEP 2: Parsa HTML e aggiorna JSON dei metadata (incrementale)"
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
        default=None,
        help="File JSON di output (default: metadata/metadata_cassazione_{year}.json se --year, altrimenti metadata/metadata_cassazione.json)"
    )
    parser.add_argument(
        "--year",
        type=str,
        default=None,
        help="Anno specifico per generare metadata_cassazione_{year}.json"
    )
    parser.add_argument(
        "--all-years",
        action="store_true",
        help="Genera JSON separati per TUTTI gli anni (strategia efficiente)"
    )
    parser.add_argument(
        "--delete-html",
        action="store_true",
        help="Cancella i file HTML dopo parsing riuscito"
    )

    args = parser.parse_args()

    # STRATEGIA EFFICIENTE: genera tutti i JSON per anno
    if args.all_years:
        parse_all_html_to_json_by_year(args.html_dir, output_dir="metadata", delete_html_after=args.delete_html)
        return

    # Strategia singolo anno (mantenuta per compatibilità)
    if args.output:
        output_json = args.output
    elif args.year:
        output_json = f"metadata/metadata_cassazione_{args.year}.json"
    else:
        output_json = "metadata/metadata_cassazione.json"

    parse_all_html_files(args.html_dir, output_json, delete_html_after=args.delete_html, filter_year=args.year)


if __name__ == "__main__":
    main()
