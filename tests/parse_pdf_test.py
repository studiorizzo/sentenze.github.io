#!/usr/bin/env python3
"""
Script per estrarre testo dai PDF delle sentenze
"""

import pymupdf  # PyMuPDF
import json


def extract_text_from_pdf(pdf_path):
    """Estrae il testo completo da un PDF"""

    try:
        doc = pymupdf.open(pdf_path)

        # Informazioni sul PDF
        info = {
            'num_pages': len(doc),
            'metadata': doc.metadata,
        }

        # Estrai il testo da tutte le pagine
        full_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            full_text += text + "\n\n"

        doc.close()

        return {
            'success': True,
            'info': info,
            'text': full_text.strip(),
            'text_length': len(full_text.strip()),
            'preview': full_text.strip()[:1000] + "..." if len(full_text) > 1000 else full_text.strip()
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def extract_text_to_markdown(pdf_path):
    """Estrae il testo dal PDF e lo formatta in Markdown"""

    try:
        doc = pymupdf.open(pdf_path)

        markdown_text = ""

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Estrai i blocchi di testo con formattazione
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        for span in line["spans"]:
                            text = span["text"]
                            # Controlla se è grassetto o titolo in base alla dimensione font
                            if span["size"] > 12:  # Probabile titolo
                                line_text += f"**{text}** "
                            else:
                                line_text += text + " "

                        markdown_text += line_text.strip() + "\n\n"

        doc.close()

        return {
            'success': True,
            'markdown': markdown_text.strip(),
            'length': len(markdown_text.strip())
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == '__main__':
    # Test con il PDF della sentenza 30039
    pdf_file = '/home/user/sentenze.github.io/pdf/_20251113_snciv@s50@a2025@n30039@tO.clean.pdf'

    print("📄 Test estrazione testo da PDF...")
    print("=" * 60)

    # Test 1: Estrazione semplice
    result = extract_text_from_pdf(pdf_file)

    if result['success']:
        print(f"✅ Estrazione riuscita!")
        print(f"📊 Numero pagine: {result['info']['num_pages']}")
        print(f"📝 Lunghezza testo: {result['text_length']:,} caratteri")
        print(f"\n📖 Preview (primi 1000 caratteri):")
        print("-" * 60)
        print(result['preview'])
        print("-" * 60)

        # Salva il testo completo
        with open('/home/user/sentenze.github.io/sentenza_30039_text.txt', 'w', encoding='utf-8') as f:
            f.write(result['text'])
        print(f"\n💾 Testo completo salvato in: sentenza_30039_text.txt")

    else:
        print(f"❌ Errore: {result['error']}")

    # Test 2: Estrazione con formattazione Markdown
    print("\n" + "=" * 60)
    print("📝 Test estrazione con formattazione Markdown...")

    md_result = extract_text_to_markdown(pdf_file)

    if md_result['success']:
        print(f"✅ Conversione Markdown riuscita!")
        print(f"📝 Lunghezza: {md_result['length']:,} caratteri")

        # Salva in formato Markdown
        with open('/home/user/sentenze.github.io/sentenza_30039.md', 'w', encoding='utf-8') as f:
            f.write(md_result['markdown'])
        print(f"💾 Markdown salvato in: sentenza_30039.md")

        # Mostra preview
        print(f"\n📖 Preview Markdown (primi 800 caratteri):")
        print("-" * 60)
        print(md_result['markdown'][:800] + "...")
        print("-" * 60)
    else:
        print(f"❌ Errore: {md_result['error']}")
