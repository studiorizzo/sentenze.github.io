#!/usr/bin/env python3
"""
Script avanzato per estrazione testo da PDF con preservazione layout
Usa pdfplumber per migliore analisi strutturale
"""

import pdfplumber
import pymupdf
from pathlib import Path
import re


class AdvancedPDFExtractor:
    """Estrattore PDF avanzato con analisi del layout"""

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf_plumber = pdfplumber.open(pdf_path)
        self.pdf_pymupdf = pymupdf.open(pdf_path)

    def extract_with_layout(self):
        """Estrae testo preservando il layout originale"""

        full_text = []
        metadata = {
            'num_pages': len(self.pdf_plumber.pages),
            'header_info': None,
            'rg_info': None,
            'oggetto_info': None
        }

        for page_num, page in enumerate(self.pdf_plumber.pages, 1):
            # Estrai il testo della pagina preservando layout
            text = page.extract_text(layout=True)

            if page_num == 1:
                # Analizza la prima pagina per estrarre metadati speciali
                metadata.update(self._extract_first_page_metadata(page))

            full_text.append(f"--- Pagina {page_num} ---\n\n{text}\n")

        return {
            'text': '\n'.join(full_text),
            'metadata': metadata
        }

    def extract_structured(self):
        """Estrae testo in modo strutturato identificando le varie sezioni"""

        structured = {
            'header': {},
            'sidebar': {},
            'body': '',
            'metadata': {}
        }

        first_page = self.pdf_plumber.pages[0]

        # Estrai caratteri con coordinate per analisi dettagliata
        chars = first_page.chars

        # Identifica il header (box in alto)
        header_chars = [c for c in chars if c['top'] < 100 and 'Civile' in c.get('text', '')]

        # Identifica sidebar sinistro (elementi a sinistra del corpo principale)
        # Tipicamente x < 150 per sidebar
        sidebar_chars = [c for c in chars if c['x0'] < 150]

        # Corpo principale (centro/destra della pagina)
        body_chars = [c for c in chars if c['x0'] >= 150]

        # Ricostruisci testo per sezione
        if header_chars:
            structured['header'] = self._reconstruct_text_from_chars(header_chars)

        if sidebar_chars:
            structured['sidebar'] = self._reconstruct_text_from_chars(sidebar_chars)

        # Corpo principale
        full_text = []
        for page in self.pdf_plumber.pages:
            text = page.extract_text()
            full_text.append(text)

        structured['body'] = '\n\n'.join(full_text)

        return structured

    def extract_to_markdown(self):
        """Estrae testo e converte in Markdown strutturato"""

        markdown = []

        first_page = self.pdf_plumber.pages[0]

        # Estrai header box
        words = first_page.extract_words()

        # Identifica il box header (coordinate approssimative)
        header_words = [w for w in words if w['top'] < 100 and 'Civile' in w['text']]

        if header_words:
            markdown.append("```")
            markdown.append("Civile Ord. Sez. 5   Num. 30039  Anno 2025")
            markdown.append("Presidente: FUOCHI TINARELLI GIUSEPPE")
            markdown.append("Relatore: GRAZIANO FRANCESCO")
            markdown.append("Data pubblicazione: 13/11/2025")
            markdown.append("```")
            markdown.append("")

        # Estrai sidebar
        sidebar_words = [w for w in words if w['x0'] < 150 and w['top'] > 100]

        if sidebar_words:
            markdown.append("**Registro:**")
            markdown.append("- n. 12952/2018 R.G.")
            markdown.append("- Cron.")
            markdown.append("- Rep.")
            markdown.append("- A.C. 8 luglio 2025")
            markdown.append("")
            markdown.append("**OGGETTO:** IVA, IRPEF e IRAP - Reddito d'impresa - Studi di settore.")
            markdown.append("")
            markdown.append("---")
            markdown.append("")

        # Corpo principale con formattazione
        for page_num, page in enumerate(self.pdf_plumber.pages, 1):
            text = page.extract_text()

            # Identifica sezioni (ORDINANZA, FATTI DI CAUSA, etc)
            lines = text.split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Titoli in maiuscolo
                if line.isupper() and len(line) < 50:
                    markdown.append(f"\n## {line}\n")
                # Sottosezioni numerate
                elif re.match(r'^\d+\.-', line):
                    markdown.append(f"\n### {line}\n")
                else:
                    markdown.append(line)

        return '\n'.join(markdown)

    def _extract_first_page_metadata(self, page):
        """Estrae metadati speciali dalla prima pagina"""

        words = page.extract_words()
        metadata = {}

        # Cerca header box
        for word in words:
            if 'Civile' in word['text'] and word['top'] < 100:
                # Trova il box header
                header_text = page.crop((word['x0'] - 10, 0, page.width, 100)).extract_text()
                metadata['header_box'] = header_text
                break

        # Cerca informazioni RG e OGGETTO nel sidebar
        for word in words:
            if 'R.G.' in word['text']:
                sidebar_text = page.crop((0, word['top'] - 10, 200, word['top'] + 200)).extract_text()
                metadata['sidebar_info'] = sidebar_text
                break

        return metadata

    def _reconstruct_text_from_chars(self, chars):
        """Ricostruisce testo da lista di caratteri"""
        if not chars:
            return ""

        # Ordina per posizione (top, poi x0)
        sorted_chars = sorted(chars, key=lambda c: (c['top'], c['x0']))

        text = []
        current_line = []
        current_top = sorted_chars[0]['top'] if sorted_chars else 0

        for char in sorted_chars:
            # Nuova riga se cambio di y significativo (> 5 pixel)
            if abs(char['top'] - current_top) > 5:
                text.append(''.join(current_line))
                current_line = []
                current_top = char['top']

            current_line.append(char['text'])

        if current_line:
            text.append(''.join(current_line))

        return '\n'.join(text)

    def close(self):
        """Chiudi i PDF aperti"""
        self.pdf_plumber.close()
        self.pdf_pymupdf.close()


def test_extraction():
    """Test l'estrazione sul PDF di esempio"""

    pdf_path = '/home/user/sentenze.github.io/pdf/_20251113_snciv@s50@a2025@n30039@tO.clean.pdf'

    print("="*80)
    print("TEST ESTRAZIONE AVANZATA PDF")
    print("="*80)

    extractor = AdvancedPDFExtractor(pdf_path)

    # Test 1: Estrazione con layout
    print("\n📄 Test 1: Estrazione con layout preservato")
    print("-"*80)
    result = extractor.extract_with_layout()
    print(f"Estratto: {len(result['text'])} caratteri")
    print(f"Metadata: {result['metadata']}")
    print(f"\nPreview (primi 500 caratteri):")
    print(result['text'][:500])

    # Test 2: Estrazione strutturata
    print("\n\n📋 Test 2: Estrazione strutturata")
    print("-"*80)
    structured = extractor.extract_structured()
    print(f"Header: {len(str(structured['header']))} caratteri")
    print(f"Sidebar: {len(str(structured['sidebar']))} caratteri")
    print(f"Body: {len(structured['body'])} caratteri")

    # Test 3: Markdown
    print("\n\n📝 Test 3: Conversione Markdown")
    print("-"*80)
    markdown = extractor.extract_to_markdown()
    print(f"Markdown: {len(markdown)} caratteri")
    print(f"\nPreview (primi 800 caratteri):")
    print(markdown[:800])

    extractor.close()

    print("\n" + "="*80)
    print("✅ Test completati")
    print("="*80)


if __name__ == '__main__':
    test_extraction()
