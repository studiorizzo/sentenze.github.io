#!/usr/bin/env python3
"""
Script COMPLETAMENTE AUTOMATICO
Processa tutti gli HTML e i PDF disponibili su GitHub
"""

import sys
sys.path.insert(0, 'scripts')

from pathlib import Path
from bs4 import BeautifulSoup
from final_pdf_extractor import process_single_pdf
import json

def extract_sentenze_from_html(html_path):
    """Estrae metadata e link PDF dall'HTML"""

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    cards = soup.find_all('div', class_='card')

    sentenze = []
    for card in cards:
        # Estrai ID
        id_elem = card.find('span', {'data-role': 'content', 'data-arg': 'id'})
        if not id_elem:
            continue

        sentenza_id = id_elem.text.strip()

        # Estrai PDF URL
        pdf_elem = card.find('img', class_='pdf')
        if not pdf_elem or 'data-arg' not in pdf_elem.attrs:
            continue

        pdf_path = pdf_elem['data-arg']
        # Estrai il nome file dal path
        # Es: /xway/.../snciv@s50@a2025@n30039@tO.clean.pdf
        pdf_filename = pdf_path.split('/')[-1].replace('.clean.pdf', '')

        sentenze.append({
            'id': sentenza_id,
            'pdf_filename': pdf_filename,
        })

    return sentenze

def main():
    print("="*80)
    print("PROCESSORE AUTOMATICO COMPLETO")
    print("="*80)
    print()

    # Directory
    html_dir = Path('data/html')
    pdf_dir = Path('data/pdf')
    txt_dir = Path('txt')
    md_dir = Path('markdown')

    txt_dir.mkdir(exist_ok=True)
    md_dir.mkdir(exist_ok=True)

    # Trova tutti gli HTML
    html_files = sorted(html_dir.glob('*.html'))
    print(f"📂 Trovati {len(html_files)} file HTML")

    # Trova tutti i PDF disponibili
    pdf_files = {p.stem: p for p in pdf_dir.glob('*.pdf')}
    print(f"📂 Trovati {len(pdf_files)} file PDF disponibili")
    print()

    # Contatori
    total_sentenze = 0
    processed = 0
    skipped = 0
    errors = 0

    # Processa ogni HTML
    for html_file in html_files:
        print(f"📄 Processando HTML: {html_file.name}")

        sentenze = extract_sentenze_from_html(html_file)
        total_sentenze += len(sentenze)

        print(f"   → {len(sentenze)} sentenze trovate")

        # Processa ogni sentenza
        for sentenza in sentenze:
            sentenza_id = sentenza['id']

            # Controlla se già processata
            txt_path = txt_dir / f"{sentenza_id}.txt"
            md_path = md_dir / f"{sentenza_id}.md"

            if txt_path.exists() and md_path.exists():
                print(f"   ⏭️  {sentenza_id} - già processata")
                skipped += 1
                continue

            # Cerca il PDF
            # Il nome del PDF potrebbe essere diverso, cerchiamo per pattern
            matching_pdfs = [
                pdf_path for pdf_name, pdf_path in pdf_files.items()
                if sentenza_id.lower() in pdf_name.lower() or
                   sentenza['pdf_filename'] in pdf_name
            ]

            if not matching_pdfs:
                print(f"   ⚠️  {sentenza_id} - PDF non disponibile")
                skipped += 1
                continue

            pdf_path = matching_pdfs[0]

            # Processa
            try:
                result = process_single_pdf(str(pdf_path), sentenza_id, str(Path.cwd()))
                processed += 1
                print(f"   ✅ {sentenza_id} - OK ({result['txt_length']:,} char)")
            except Exception as e:
                errors += 1
                print(f"   ❌ {sentenza_id} - ERRORE: {e}")

        print()

    # Riepilogo
    print("="*80)
    print("RIEPILOGO")
    print("="*80)
    print(f"Totale sentenze trovate: {total_sentenze}")
    print(f"  ✅ Processate:         {processed}")
    print(f"  ⏭️  Già processate:     {skipped}")
    print(f"  ❌ Errori:             {errors}")
    print("="*80)

    if processed > 0:
        print("\n✅ PROCESSO COMPLETATO!")
        print(f"   TXT salvati in: {txt_dir}/")
        print(f"   Markdown salvati in: {md_dir}/")

if __name__ == '__main__':
    main()
