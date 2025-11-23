#!/usr/bin/env python3
"""
STEP 4: Extract TXT from PDFs
Scarica PDF, estrae TXT usando final_pdf_extractor, cancella PDF
"""

import os
import json
import time
import argparse
import requests
import urllib3
from pathlib import Path
from datetime import datetime

# Importa l'estrattore esistente
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))
from final_pdf_extractor import FinalPDFExtractor

# Disable SSL warnings
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


def get_existing_txt_files(txt_dir):
    """Ritorna set di ID sentenze già estratte in TXT"""
    txt_path = Path(txt_dir)
    if not txt_path.exists():
        return set()

    txt_files = txt_path.glob('*.txt')
    # Estrai ID dal nome file (es: snciv2025530039O.txt → snciv2025530039O)
    return {f.stem for f in txt_files}


def download_pdf_temp(url, temp_path, timeout=30):
    """Scarica PDF temporaneamente"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout, stream=True, verify=False)

        if response.status_code == 200:
            # Verifica che sia un PDF
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower():
                return False

            # Salva temporaneamente
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            return False

    except Exception as e:
        print(f"      Errore download: {e}")
        return False


def extract_txt_from_pdf(sentence_id, pdf_url, txt_dir, temp_pdf_dir, delete_pdf=True):
    """
    Scarica PDF, estrae TXT, cancella PDF

    Args:
        sentence_id: ID univoco sentenza
        pdf_url: URL del PDF
        txt_dir: Directory output TXT
        temp_pdf_dir: Directory temporanea per PDF
        delete_pdf: Se True, cancella PDF dopo estrazione

    Returns:
        True se successo, False altrimenti
    """
    txt_path = Path(txt_dir)
    temp_pdf_path = Path(temp_pdf_dir)
    txt_path.mkdir(parents=True, exist_ok=True)
    temp_pdf_path.mkdir(parents=True, exist_ok=True)

    # Percorsi file
    txt_file = txt_path / f"{sentence_id}.txt"
    temp_pdf_file = temp_pdf_path / f"{sentence_id}.pdf"

    # Verifica se TXT esiste già
    if txt_file.exists():
        print(f"   ⏭️  {sentence_id} - TXT già esistente")
        return True

    try:
        # 1. Scarica PDF temporaneamente
        print(f"   📥 {sentence_id} - Download PDF...", end=" ")
        if not download_pdf_temp(pdf_url, temp_pdf_file):
            print("✗ Errore download")
            return False
        print("✓")

        # 2. Estrai TXT usando FinalPDFExtractor
        print(f"   📝 {sentence_id} - Estrazione TXT...", end=" ")
        extractor = FinalPDFExtractor(str(temp_pdf_file))
        txt_content = extractor.extract_structured_text()
        extractor.close()

        # 3. Salva TXT
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        print(f"✓ ({len(txt_content):,} caratteri)")

        # 4. Cancella PDF se richiesto
        if delete_pdf and temp_pdf_file.exists():
            temp_pdf_file.unlink()

        return True

    except Exception as e:
        print(f"\n   ✗ Errore estrazione {sentence_id}: {e}")
        # Pulizia in caso di errore
        if temp_pdf_file.exists():
            temp_pdf_file.unlink()
        return False


def extract_all_txt(json_path, txt_dir="txt", temp_pdf_dir="temp_pdf", max_extractions=0, delay=1.5):
    """
    Processa tutte le sentenze dal JSON ed estrae TXT

    Args:
        json_path: Percorso JSON metadata
        txt_dir: Directory output TXT
        temp_pdf_dir: Directory temporanea PDF
        max_extractions: Numero massimo estrazioni (0 = tutte)
        delay: Pausa tra download (secondi)
    """
    print(f"🚀 Estrazione TXT da PDF")
    print(f"📄 JSON: {json_path}")
    print(f"📁 Output TXT: {txt_dir}")
    print(f"🗑️  PDF temporanei in: {temp_pdf_dir} (cancellati dopo estrazione)\n")

    # Carica metadata
    sentences = load_metadata(json_path)
    if not sentences:
        print("✗ Nessuna sentenza trovata nel JSON")
        return

    # Trova TXT già esistenti
    existing_txt = get_existing_txt_files(txt_dir)

    # Filtra solo sentenze senza TXT
    to_extract = [s for s in sentences if s['id'] not in existing_txt]

    print(f"📊 Sentenze totali: {len(sentences)}")
    print(f"✅ TXT già esistenti: {len(existing_txt)}")
    print(f"📥 Da estrarre: {len(to_extract)}")

    if max_extractions > 0:
        to_extract = to_extract[:max_extractions]
        print(f"🎯 Limite: {max_extractions} estrazioni\n")

    if not to_extract:
        print("\n✅ Tutti i TXT già presenti!")
        return

    # Statistiche
    extracted = 0
    failed = 0
    start_time = time.time()

    # Processa sentenze
    for i, sentence in enumerate(to_extract, 1):
        sentence_id = sentence['id']
        pdf_url = sentence['pdf_url']

        print(f"[{i}/{len(to_extract)}] {sentence_id}")

        if extract_txt_from_pdf(sentence_id, pdf_url, txt_dir, temp_pdf_dir, delete_pdf=True):
            extracted += 1
        else:
            failed += 1

        # Pausa tra download
        if i < len(to_extract):
            time.sleep(delay)

    # Report finale
    elapsed = time.time() - start_time
    print(f"\n✅ Estrazione completata!")
    print(f"📥 Estratti: {extracted}")
    print(f"✗ Falliti: {failed}")
    print(f"⏱️  Tempo: {elapsed:.1f}s")
    print(f"📁 Directory TXT: {Path(txt_dir).absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description="STEP 4: Estrae TXT da PDF delle sentenze"
    )
    parser.add_argument(
        "--json",
        type=str,
        required=True,
        help="File JSON metadata (es: metadata/metadata_cassazione_2020.json)"
    )
    parser.add_argument(
        "--txt-dir",
        type=str,
        default="txt",
        help="Directory output TXT (default: txt)"
    )
    parser.add_argument(
        "--temp-pdf-dir",
        type=str,
        default="temp_pdf",
        help="Directory temporanea PDF (default: temp_pdf)"
    )
    parser.add_argument(
        "--max",
        type=int,
        default=0,
        help="Numero massimo estrazioni (0 = tutte, default: 0)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Pausa tra download in secondi (default: 1.5)"
    )

    args = parser.parse_args()

    extract_all_txt(
        json_path=args.json,
        txt_dir=args.txt_dir,
        temp_pdf_dir=args.temp_pdf_dir,
        max_extractions=args.max,
        delay=args.delay
    )


if __name__ == "__main__":
    main()
