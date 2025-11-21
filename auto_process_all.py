#!/usr/bin/env python3
"""
PROCESSORE AUTOMATICO COMPLETO
Pipeline completa: HTML → Metadata → TXT → LLM Entities → XML → Chunks → Embeddings → Markdown
"""

import sys
sys.path.insert(0, 'scripts')

from pathlib import Path
import json
import os

# Import step processors
from html_metadata_extractor import process_all_html, extract_sentenze_from_html
from final_pdf_extractor import process_single_pdf
from llm_entity_extractor import process_sentenza_llm
from akoma_ntoso_generator import process_sentenza_akoma_ntoso
from chunking_processor import process_sentenza_chunking
from embeddings_generator import process_sentenza_embeddings
from markdown_generator import process_sentenza_markdown


def main():
    print("="*80)
    print("PROCESSORE AUTOMATICO COMPLETO - Pipeline 7 Steps")
    print("="*80)
    print()

    # Determina backend LLM per estrazione entità
    backend = os.getenv('LLM_BACKEND', 'gemini')
    has_api_key = bool(os.getenv('GOOGLE_API_KEY') or os.getenv('ANTHROPIC_API_KEY') or backend == 'ollama')

    print(f"🤖 Metodo estrazione entità: LLM")
    print(f"   Backend: {backend}")

    if not has_api_key:
        print()
        print("⚠️  ATTENZIONE: Nessuna API key configurata!")
        print("   Per usare l'estrazione automatica, configura:")
        print("     - Gemini:  export GOOGLE_API_KEY='...'")
        print("     - Claude:  export ANTHROPIC_API_KEY='sk-ant-...'")
        print("     - Ollama:  export LLM_BACKEND='ollama' (locale)")
        print()
        print("   Puoi comunque estrarre entità manualmente con Claude.ai")
        print("   usando il prompt in PROGRESS.md")
        print()
    print()

    # Directory
    html_dir = Path('data/html')
    pdf_dir = Path('data/pdf')
    metadata_dir = Path('metadata')
    txt_dir = Path('txt')
    entities_dir = Path('entities')
    akoma_dir = Path('akoma_ntoso')
    chunks_dir = Path('chunks')
    embeddings_dir = Path('embeddings')
    markdown_dir = Path('markdown_ai')

    # Crea directory output
    for dir_path in [metadata_dir, txt_dir, entities_dir, akoma_dir,
                      chunks_dir, embeddings_dir, markdown_dir]:
        dir_path.mkdir(exist_ok=True)

    # STEP 0: Estrai metadata da HTML
    print("📋 STEP 0: Estrazione Metadata da HTML")
    print("-"*80)

    metadata_stats = process_all_html(html_dir, metadata_dir)
    print(f"✅ {metadata_stats['total_sentenze']} metadata estratti\n")

    # Carica metadata
    metadata_file = metadata_dir / "_all_sentenze.json"
    with open(metadata_file, 'r', encoding='utf-8') as f:
        all_sentenze = json.load(f)

    # Trova PDFs disponibili
    pdf_files = {p.stem.replace('_20251113_', '').replace('.clean', ''): p
                 for p in pdf_dir.glob('*.pdf')}

    print(f"📂 {len(all_sentenze)} sentenze con metadata")
    print(f"📂 {len(pdf_files)} PDFs disponibili")
    print()

    # Contatori
    processed = 0
    skipped = 0
    errors = 0
    no_pdf = 0

    # PROCESSA ogni sentenza
    print("="*80)
    print("PROCESSING PIPELINE")
    print("="*80)
    print()

    for sentenza_meta in all_sentenze:
        sentenza_id = sentenza_meta['id']
        print(f"📄 {sentenza_id}")

        # Controlla se già processata
        markdown_path = markdown_dir / f"{sentenza_id}.md"
        if markdown_path.exists():
            print(f"   ⏭️  Già processata (skip)")
            skipped += 1
            continue

        # Cerca PDF
        pdf_filename_key = sentenza_meta.get('pdf_filename', '').replace('.clean.pdf', '')
        matching_pdf = None

        for pdf_key, pdf_path in pdf_files.items():
            if pdf_filename_key in pdf_key or sentenza_id.lower() in pdf_key.lower():
                matching_pdf = pdf_path
                break

        if not matching_pdf:
            print(f"   ⚠️  PDF non disponibile")
            no_pdf += 1
            continue

        # PIPELINE COMPLETA
        try:
            # Step 1: PDF → TXT
            print(f"   → Step 1: PDF extraction...")
            txt_result = process_single_pdf(str(matching_pdf), sentenza_id, str(Path.cwd()))
            txt_path = Path(txt_result['txt_file'])

            # Step 2: TXT → Entities (LLM)
            print(f"   → Step 2: LLM entity extraction...")
            entity_result = process_sentenza_llm(txt_path, sentenza_id, entities_dir, backend=backend)
            entities_path = Path(entity_result['output_file'])

            # Step 3: TXT + Entities → Akoma Ntoso XML
            print(f"   → Step 3: Akoma Ntoso XML...")
            xml_result = process_sentenza_akoma_ntoso(txt_path, entities_path, sentenza_id, akoma_dir)

            # Step 4: TXT → Chunks
            print(f"   → Step 4: Chunking...")
            chunks_result = process_sentenza_chunking(txt_path, sentenza_id, chunks_dir, use_both=True)
            chunks_path = Path(chunks_result['output_file'])

            # Step 5: Chunks → Embeddings
            print(f"   → Step 5: Embeddings...")
            embeddings_result = process_sentenza_embeddings(chunks_path, sentenza_id, embeddings_dir, use_both=False)

            # Step 7: TXT + Entities + Chunks → Markdown AI
            print(f"   → Step 7: Markdown AI...")
            markdown_result = process_sentenza_markdown(txt_path, entities_path, chunks_path, sentenza_id, markdown_dir)

            print(f"   ✅ Completata ({txt_result['txt_length']:,} char)")
            processed += 1

        except Exception as e:
            errors += 1
            print(f"   ❌ ERRORE: {e}")

        print()

    # RIEPILOGO FINALE
    print("="*80)
    print("RIEPILOGO FINALE")
    print("="*80)
    print(f"Sentenze totali:       {len(all_sentenze)}")
    print(f"  ✅ Processate:       {processed}")
    print(f"  ⏭️  Già processate:  {skipped}")
    print(f"  ⚠️  Senza PDF:        {no_pdf}")
    print(f"  ❌ Errori:           {errors}")
    print("="*80)

    if processed > 0:
        print("\n✅ PROCESSO COMPLETATO!")
        print(f"   Metadata:    metadata/")
        print(f"   TXT:         txt/")
        print(f"   Entities:    entities/")
        print(f"   XML:         akoma_ntoso/")
        print(f"   Chunks:      chunks/")
        print(f"   Embeddings:  embeddings/")
        print(f"   Markdown:    markdown_ai/")


if __name__ == '__main__':
    main()
