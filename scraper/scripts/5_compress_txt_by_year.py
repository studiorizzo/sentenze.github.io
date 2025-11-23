#!/usr/bin/env python3
"""
STEP 5: Compress TXT files by year
Comprime tutti i file TXT di un anno in un archivio .tar.gz
"""

import os
import json
import tarfile
import argparse
from pathlib import Path
from datetime import datetime


def load_sentences_for_year(year, metadata_dir="metadata"):
    """Carica tutte le sentenze di un anno specifico dal JSON"""
    json_path = Path(metadata_dir) / f"metadata_cassazione_{year}.json"

    if not json_path.exists():
        print(f"✗ JSON non trovato: {json_path}")
        return []

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            sentences = data.get('sentences', [])
            return [s['id'] for s in sentences]
    except Exception as e:
        print(f"✗ Errore caricamento JSON: {e}")
        return []


def compress_txt_files(year, txt_dir="txt", output_dir="txt_compressed", metadata_dir="metadata", delete_after=False):
    """
    Comprime tutti i TXT di un anno in un archivio .tar.gz

    Args:
        year: Anno da comprimere
        txt_dir: Directory contenente i file TXT
        output_dir: Directory output archivi compressi
        metadata_dir: Directory metadata JSON
        delete_after: Se True, cancella i TXT dopo compressione
    """
    print(f"🗜️  Compressione TXT Anno {year}")
    print(f"📁 Input: {txt_dir}")
    print(f"📦 Output: {output_dir}\n")

    # Carica ID sentenze per l'anno
    sentence_ids = load_sentences_for_year(year, metadata_dir)

    if not sentence_ids:
        print(f"✗ Nessuna sentenza trovata per anno {year}")
        return

    print(f"📊 Sentenze anno {year}: {len(sentence_ids)}")

    # Trova file TXT esistenti per questo anno
    txt_path = Path(txt_dir)
    if not txt_path.exists():
        print(f"✗ Directory TXT non trovata: {txt_dir}")
        return

    txt_files = []
    missing = 0

    for sentence_id in sentence_ids:
        txt_file = txt_path / f"{sentence_id}.txt"
        if txt_file.exists():
            txt_files.append(txt_file)
        else:
            missing += 1

    print(f"✓ File TXT trovati: {len(txt_files)}")
    if missing > 0:
        print(f"⚠️  File TXT mancanti: {missing}")

    if not txt_files:
        print("\n✗ Nessun file TXT da comprimere")
        return

    # Crea directory output
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Nome archivio
    archive_name = f"{year}_sentenze_civile_quinta.tar.gz"
    archive_path = output_path / archive_name

    print(f"\n📦 Creazione archivio: {archive_name}")

    # Crea archivio tar.gz
    try:
        with tarfile.open(archive_path, 'w:gz') as tar:
            for i, txt_file in enumerate(txt_files, 1):
                # Aggiungi file all'archivio con percorso relativo
                arcname = txt_file.name  # Solo il nome file, senza path
                tar.add(txt_file, arcname=arcname)

                if i % 100 == 0 or i == len(txt_files):
                    print(f"   [{i}/{len(txt_files)}] file aggiunti...")

        # Statistiche
        archive_size = archive_path.stat().st_size
        total_txt_size = sum(f.stat().st_size for f in txt_files)
        compression_ratio = (1 - archive_size / total_txt_size) * 100

        print(f"\n✅ Compressione completata!")
        print(f"📦 Archivio: {archive_path}")
        print(f"📊 File compressi: {len(txt_files)}")
        print(f"💾 Dimensione originale: {total_txt_size / 1024 / 1024:.2f} MB")
        print(f"📉 Dimensione compressa: {archive_size / 1024 / 1024:.2f} MB")
        print(f"🎯 Compressione: {compression_ratio:.1f}%")

        # Cancella TXT se richiesto
        if delete_after:
            print(f"\n🗑️  Cancellazione file TXT originali...")
            deleted = 0
            for txt_file in txt_files:
                try:
                    txt_file.unlink()
                    deleted += 1
                except Exception as e:
                    print(f"   ✗ Errore cancellazione {txt_file.name}: {e}")
            print(f"   ✓ {deleted}/{len(txt_files)} file cancellati")

    except Exception as e:
        print(f"✗ Errore durante compressione: {e}")
        import traceback
        traceback.print_exc()


def decompress_archive(archive_path, output_dir="txt"):
    """
    Decomprime un archivio .tar.gz nella directory specificata

    Args:
        archive_path: Percorso archivio .tar.gz
        output_dir: Directory output
    """
    archive = Path(archive_path)
    if not archive.exists():
        print(f"✗ Archivio non trovato: {archive_path}")
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"📦 Decompressione: {archive.name}")
    print(f"📁 Output: {output_dir}\n")

    try:
        with tarfile.open(archive, 'r:gz') as tar:
            members = tar.getmembers()
            print(f"📊 File nell'archivio: {len(members)}")

            for i, member in enumerate(members, 1):
                tar.extract(member, path=output_dir)
                if i % 100 == 0 or i == len(members):
                    print(f"   [{i}/{len(members)}] file estratti...")

        print(f"\n✅ Decompressione completata!")
        print(f"📁 File estratti in: {output_path.absolute()}")

    except Exception as e:
        print(f"✗ Errore decompressione: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="STEP 5: Comprime/decomprime TXT per anno"
    )
    subparsers = parser.add_subparsers(dest='command', help='Comando da eseguire')

    # Comando compress
    compress_parser = subparsers.add_parser('compress', help='Comprimi TXT di un anno')
    compress_parser.add_argument(
        "--year",
        type=str,
        required=True,
        help="Anno da comprimere (es: 2020)"
    )
    compress_parser.add_argument(
        "--txt-dir",
        type=str,
        default="txt",
        help="Directory TXT input (default: txt)"
    )
    compress_parser.add_argument(
        "--output-dir",
        type=str,
        default="txt_compressed",
        help="Directory output archivi (default: txt_compressed)"
    )
    compress_parser.add_argument(
        "--metadata-dir",
        type=str,
        default="metadata",
        help="Directory metadata JSON (default: metadata)"
    )
    compress_parser.add_argument(
        "--delete-after",
        action="store_true",
        help="Cancella TXT originali dopo compressione"
    )

    # Comando decompress
    decompress_parser = subparsers.add_parser('decompress', help='Decomprimi archivio TXT')
    decompress_parser.add_argument(
        "--archive",
        type=str,
        required=True,
        help="Percorso archivio .tar.gz"
    )
    decompress_parser.add_argument(
        "--output-dir",
        type=str,
        default="txt",
        help="Directory output (default: txt)"
    )

    args = parser.parse_args()

    if args.command == 'compress':
        compress_txt_files(
            year=args.year,
            txt_dir=args.txt_dir,
            output_dir=args.output_dir,
            metadata_dir=args.metadata_dir,
            delete_after=args.delete_after
        )
    elif args.command == 'decompress':
        decompress_archive(
            archive_path=args.archive,
            output_dir=args.output_dir
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
