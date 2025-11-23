#!/usr/bin/env python3
"""
STEP 3: Download PDFs
Legge metadata/metadata_cassazione.json e scarica i PDF delle nuove sentenze
"""

import os
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime
import urllib3

# Disable SSL warnings (necessario per italgiure.giustizia.it in GitHub Actions)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_metadata(json_path):
    """Carica il JSON dei metadata"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('sentences', [])
    except Exception as e:
        print(f"✗ Errore caricamento JSON: {e}")
        return []


def get_existing_pdfs(pdf_dir):
    """Ottiene la lista degli ID delle sentenze già scaricate"""
    pdf_path = Path(pdf_dir)
    if not pdf_path.exists():
        return set()

    # Estrae gli ID dai nomi dei file PDF
    # Formato file: snciv2025530039O.pdf o _20251113_snciv@s50@a2025@n30039@tO.clean.pdf
    existing_ids = set()

    for pdf_file in pdf_path.glob('*.pdf'):
        filename = pdf_file.stem

        # Prova a estrarre l'ID in vari formati
        # Formato 1: snciv2025530039O
        if filename.startswith('snciv') or filename.startswith('snpen'):
            existing_ids.add(filename)

        # Formato 2: _20251113_snciv@s50@a2025@n30039@tO.clean
        if '@' in filename:
            # Estrai la parte dopo l'ultima /
            parts = filename.split('@')
            if len(parts) >= 4:
                # snciv@s50@a2025@n30039@tO → snciv2025530039O
                try:
                    db = parts[0].split('_')[-1]  # snciv
                    year = parts[2][1:]  # 2025
                    num = parts[3][1:].split('@')[0]  # 30039
                    tipo = parts[4][1:].split('.')[0]  # O
                    sentence_id = f"{db}{year}{num}{tipo}"
                    existing_ids.add(sentence_id)
                except:
                    pass

    return existing_ids


def download_pdf(url, output_path, max_retries=3, timeout=30):
    """
    Scarica un PDF con retry automatico

    Args:
        url: URL del PDF
        output_path: Path dove salvare il PDF
        max_retries: Numero massimo di retry
        timeout: Timeout in secondi

    Returns:
        True se download riuscito, False altrimenti
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for attempt in range(max_retries):
        try:
            # Disable SSL verification for italgiure.giustizia.it (GitHub Actions environment)
            response = requests.get(url, headers=headers, timeout=timeout, stream=True, verify=False)

            if response.status_code == 200:
                # Verifica che sia effettivamente un PDF
                content_type = response.headers.get('Content-Type', '')
                if 'pdf' not in content_type.lower() and 'application/octet-stream' not in content_type.lower():
                    print(f"⚠️  Content-Type non valido: {content_type}")
                    return False

                # Salva il PDF
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                # Verifica dimensione file
                if output_path.stat().st_size < 1000:  # < 1KB probabilmente errore
                    print(f"⚠️  File troppo piccolo")
                    output_path.unlink()
                    return False

                return True

            elif response.status_code == 404:
                print(f"✗ Not Found (404)")
                return False
            elif response.status_code == 403:
                print(f"✗ Forbidden (403) - possibile rate limiting")
                time.sleep(5)
                continue
            else:
                print(f"✗ HTTP {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            print(f"⏱️  Timeout (tentativo {attempt + 1}/{max_retries})")
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"✗ Errore: {e}")
            return False

    return False


def download_new_pdfs(json_path, pdf_dir, max_downloads=None, delay=1.5):
    """
    Scarica i PDF delle sentenze nuove

    Args:
        json_path: Percorso del JSON metadata
        pdf_dir: Directory dove salvare i PDF
        max_downloads: Numero massimo di PDF da scaricare (None = tutti)
        delay: Pausa in secondi tra un download e l'altro
    """
    # Carica metadata
    sentences = load_metadata(json_path)
    if not sentences:
        print("✗ Nessuna sentenza trovata nel JSON")
        return

    # Ottieni PDF già esistenti
    existing_ids = get_existing_pdfs(pdf_dir)

    # Filtra le sentenze da scaricare
    to_download = [s for s in sentences if s['id'] not in existing_ids and s.get('pdf_url')]

    if not to_download:
        print("✅ Tutti i PDF sono già stati scaricati!")
        return

    print(f"🚀 Download PDFs")
    print(f"📊 Sentenze totali: {len(sentences)}")
    print(f"✅ Già scaricate: {len(existing_ids)}")
    print(f"📥 Da scaricare: {len(to_download)}")

    if max_downloads:
        to_download = to_download[:max_downloads]
        print(f"🎯 Limite: {max_downloads} download\n")

    # Crea directory PDF se non esiste
    pdf_path = Path(pdf_dir)
    pdf_path.mkdir(parents=True, exist_ok=True)

    # Scarica i PDF
    downloaded = 0
    failed = 0

    for i, sentence in enumerate(to_download, 1):
        sentence_id = sentence['id']
        pdf_url = sentence['pdf_url']

        print(f"[{i}/{len(to_download)}] {sentence_id}... ", end="", flush=True)

        # Nome file: stesso ID della sentenza
        output_file = pdf_path / f"{sentence_id}.pdf"

        if download_pdf(pdf_url, output_file):
            downloaded += 1
            print(f"✓")
        else:
            failed += 1
            print()

        # Pausa tra i download
        if i < len(to_download):
            time.sleep(delay)

    print(f"\n✅ Download completato!")
    print(f"📥 Scaricati: {downloaded}")
    print(f"✗ Falliti: {failed}")
    print(f"📁 Directory: {pdf_path.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description="STEP 3: Scarica PDF delle nuove sentenze"
    )
    parser.add_argument(
        "--json",
        type=str,
        default="metadata/metadata_cassazione.json",
        help="File JSON metadata (default: metadata/metadata_cassazione.json)"
    )
    parser.add_argument(
        "--pdf-dir",
        type=str,
        default="data/pdf",
        help="Directory PDF (default: data/pdf)"
    )
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        help="Numero massimo di PDF da scaricare (default: tutti)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Pausa in secondi tra i download (default: 1.5)"
    )

    args = parser.parse_args()

    download_new_pdfs(
        json_path=args.json,
        pdf_dir=args.pdf_dir,
        max_downloads=args.max,
        delay=args.delay
    )


if __name__ == "__main__":
    main()
