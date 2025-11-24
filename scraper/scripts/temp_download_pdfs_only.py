#!/usr/bin/env python3
"""
TEMP: Download PDFs only (for manual TXT extraction with vision)
Scarica i PDF dal JSON e li salva in data/pdf/ (senza estrarre TXT)
"""

import os
import json
import time
import argparse
import requests
import urllib3
from pathlib import Path

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def download_pdfs_from_json(json_path, pdf_dir="data/pdf", max_pdfs=0, delay=2.0):
    """Scarica tutti i PDF elencati nel JSON"""

    print(f"🚀 Download PDFs da JSON")
    print(f"📄 JSON: {json_path}")
    print(f"📁 Output: {pdf_dir}\n")

    # Carica JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        sentences = data.get('sentences', [])

    if not sentences:
        print("✗ Nessuna sentenza nel JSON")
        return

    # Crea directory
    pdf_path = Path(pdf_dir)
    pdf_path.mkdir(parents=True, exist_ok=True)

    # Limita se necessario
    to_download = sentences[:max_pdfs] if max_pdfs > 0 else sentences

    print(f"📊 Sentenze totali: {len(sentences)}")
    print(f"📥 Da scaricare: {len(to_download)}\n")

    downloaded = 0
    failed = 0

    for i, sentence in enumerate(to_download, 1):
        sentence_id = sentence['id']
        pdf_url = sentence['pdf_url']

        # Nome file PDF
        pdf_file = pdf_path / f"{sentence_id}.pdf"

        # Skip se esiste già
        if pdf_file.exists():
            print(f"[{i}/{len(to_download)}] {sentence_id} - già presente")
            continue

        print(f"[{i}/{len(to_download)}] {sentence_id}...", end=" ")

        try:
            # Download PDF
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(pdf_url, headers=headers, timeout=30, stream=True, verify=False)

            if response.status_code == 200:
                with open(pdf_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("✓")
                downloaded += 1
            else:
                print(f"✗ HTTP {response.status_code}")
                failed += 1

        except Exception as e:
            print(f"✗ Errore: {e}")
            failed += 1

        # Delay tra download
        if i < len(to_download):
            time.sleep(delay)

    print(f"\n✅ Download completato!")
    print(f"📥 Scaricati: {downloaded}")
    print(f"✗ Falliti: {failed}")
    print(f"📁 Directory: {pdf_path.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description="TEMP: Scarica solo PDF dal JSON (per estrazione manuale vision)"
    )
    parser.add_argument(
        "--json",
        type=str,
        required=True,
        help="File JSON metadata"
    )
    parser.add_argument(
        "--pdf-dir",
        type=str,
        default="data/pdf",
        help="Directory output PDF (default: data/pdf)"
    )
    parser.add_argument(
        "--max",
        type=int,
        default=0,
        help="Numero massimo PDF (0 = tutti, default: 0)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Pausa tra download in secondi (default: 2.0)"
    )

    args = parser.parse_args()

    download_pdfs_from_json(
        json_path=args.json,
        pdf_dir=args.pdf_dir,
        max_pdfs=args.max,
        delay=args.delay
    )


if __name__ == "__main__":
    main()
