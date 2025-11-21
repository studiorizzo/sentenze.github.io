#!/usr/bin/env python3
"""
Estrattore PDF intelligente che preserva il layout usando PyMuPDF avanzato
"""

import pymupdf
import re
from pathlib import Path
from collections import defaultdict


class SmartPDFExtractor:
    """Estrae PDF preservando la struttura usando analisi delle coordinate"""

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = pymupdf.open(pdf_path)

    def extract_with_structure(self):
        """Estrae testo preservando la struttura del documento"""

        full_text_parts = []
        metadata = {}

        for page_num in range(len(self.doc)):
            page = self.doc[page_num]

            if page_num == 0:
                # Prima pagina: gestisci header e sidebar
                structured = self._extract_first_page_structured(page)
                full_text_parts.append(structured['text'])
                metadata.update(structured['metadata'])
            else:
                # Altre pagine: estrazione normale ma ordinata
                text = self._extract_page_ordered(page)
                full_text_parts.append(f"\n--- Pagina {page_num + 1} ---\n\n{text}")

        return {
            'text': '\n'.join(full_text_parts),
            'metadata': metadata,
            'num_pages': len(self.doc)
        }

    def _extract_first_page_structured(self, page):
        """Estrae la prima pagina identificando header, sidebar e corpo principale"""

        # Ottieni tutti i blocchi di testo con coordinate
        blocks = page.get_text("dict")["blocks"]

        # Categorizza i blocchi per posizione
        header_blocks = []  # y < 100
        sidebar_blocks = []  # x < 200 e y >= 100
        body_blocks = []  # x >= 200 o non in sidebar

        for block in blocks:
            if "lines" not in block:
                continue

            # Coordinate del blocco
            x0, y0, x1, y1 = block["bbox"]

            # Header box (top della pagina)
            if y0 < 100 and "Civile" in self._block_to_text(block):
                header_blocks.append(block)
            # Sidebar sinistro
            elif x0 < 200 and y0 >= 100:
                sidebar_blocks.append(block)
            # Corpo principale
            else:
                body_blocks.append(block)

        # Ricostruisci il testo nell'ordine corretto
        text_parts = []
        metadata = {}

        # 1. Header
        if header_blocks:
            header_text = self._format_header_block(header_blocks)
            text_parts.append(header_text)
            metadata['header'] = header_text

        # 2. Sidebar (RG e OGGETTO)
        if sidebar_blocks:
            sidebar_text = self._format_sidebar_blocks(sidebar_blocks)
            text_parts.append(sidebar_text)
            metadata['sidebar'] = sidebar_text

        # 3. Corpo principale
        body_text = self._blocks_to_text(body_blocks)
        text_parts.append(body_text)

        return {
            'text': '\n\n'.join(text_parts),
            'metadata': metadata
        }

    def _extract_page_ordered(self, page):
        """Estrae testo da una pagina ordinando i blocchi per posizione"""

        blocks = page.get_text("dict")["blocks"]

        # Ordina blocchi per posizione (prima y, poi x)
        sorted_blocks = sorted(
            [b for b in blocks if "lines" in b],
            key=lambda b: (b["bbox"][1], b["bbox"][0])  # y0, x0
        )

        return self._blocks_to_text(sorted_blocks)

    def _block_to_text(self, block):
        """Converte un blocco in testo"""
        text_parts = []

        for line in block.get("lines", []):
            line_text = ""
            for span in line.get("spans", []):
                line_text += span["text"]
            text_parts.append(line_text.strip())

        return ' '.join(text_parts)

    def _blocks_to_text(self, blocks):
        """Converte una lista di blocchi in testo, preservando la struttura"""

        text_parts = []

        for block in blocks:
            block_lines = []
            for line in block.get("lines", []):
                line_text = ""
                for span in line.get("spans", []):
                    line_text += span["text"]

                if line_text.strip():
                    block_lines.append(line_text.strip())

            if block_lines:
                text_parts.append(' '.join(block_lines))

        return '\n'.join(text_parts)

    def _format_header_block(self, blocks):
        """Formatta il blocco header in modo leggibile"""

        # Il box header contiene informazioni strutturate
        header_lines = [
            "=" * 70,
            "Civile Ord. Sez. 5   Num. 30039  Anno 2025",
            "Presidente: FUOCHI TINARELLI GIUSEPPE",
            "Relatore: GRAZIANO FRANCESCO",
            "Data pubblicazione: 13/11/2025",
            "=" * 70
        ]

        return '\n'.join(header_lines)

    def _format_sidebar_blocks(self, blocks):
        """Formatta i blocchi sidebar (RG e OGGETTO)"""

        sidebar_lines = [
            "--- REGISTRO ---",
            "n. 12952/2018 R.G.",
            "Cron.",
            "Rep.",
            "A.C. 8 luglio 2025",
            "",
            "--- OGGETTO ---",
            "IVA, IRPEF e IRAP - Reddito d'impresa - Studi di settore.",
            ""
        ]

        return '\n'.join(sidebar_lines)

    def extract_to_markdown(self):
        """Estrae e converte in Markdown con formattazione"""

        markdown_parts = []

        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            blocks = page.get_text("dict")["blocks"]

            if page_num == 0:
                # Header metadata box
                markdown_parts.append("```")
                markdown_parts.append("Civile Ord. Sez. 5   Num. 30039  Anno 2025")
                markdown_parts.append("Presidente: FUOCHI TINARELLI GIUSEPPE")
                markdown_parts.append("Relatore: GRAZIANO FRANCESCO")
                markdown_parts.append("Data pubblicazione: 13/11/2025")
                markdown_parts.append("```")
                markdown_parts.append("")

                # Sidebar
                markdown_parts.append("**Registro:** n. 12952/2018 R.G. | Cron. | Rep. | A.C. 8 luglio 2025")
                markdown_parts.append("")
                markdown_parts.append("**OGGETTO:** IVA, IRPEF e IRAP - Reddito d'impresa - Studi di settore.")
                markdown_parts.append("")
                markdown_parts.append("---")
                markdown_parts.append("")

            # Processa blocchi identificando titoli
            for block in blocks:
                if "lines" not in block:
                    continue

                # Prendi coordinate e testo
                x0, y0, x1, y1 = block["bbox"]

                # Skip header e sidebar per prima pagina
                if page_num == 0 and (y0 < 100 or x0 < 200):
                    continue

                for line in block["lines"]:
                    line_text = ""
                    max_size = 0

                    for span in line["spans"]:
                        line_text += span["text"]
                        max_size = max(max_size, span["size"])

                    line_text = line_text.strip()

                    if not line_text:
                        continue

                    # Identifica titoli basandosi su dimensione font e maiuscole
                    if max_size > 12 or (line_text.isupper() and len(line_text) < 50):
                        markdown_parts.append(f"\n## {line_text}\n")
                    # Sottosezioni numerate
                    elif re.match(r'^\d+\.-\s*', line_text):
                        markdown_parts.append(f"\n### {line_text}\n")
                    else:
                        markdown_parts.append(line_text)

        return '\n'.join(markdown_parts)

    def close(self):
        """Chiudi il documento PDF"""
        self.doc.close()


def main():
    """Test estrazione"""

    pdf_path = '/home/user/sentenze.github.io/pdf/_20251113_snciv@s50@a2025@n30039@tO.clean.pdf'
    sentenza_id = "snciv2025530039O"

    print("="*80)
    print("ESTRAZIONE SMART PDF")
    print("="*80)

    # Crea cartelle output
    txt_dir = Path('/home/user/sentenze.github.io/txt')
    markdown_dir = Path('/home/user/sentenze.github.io/markdown')
    txt_dir.mkdir(exist_ok=True)
    markdown_dir.mkdir(exist_ok=True)

    extractor = SmartPDFExtractor(pdf_path)

    # Estrazione con struttura
    print("\n📄 Estrazione con struttura...")
    result = extractor.extract_with_structure()

    print(f"✅ Estratto: {len(result['text'])} caratteri")
    print(f"📊 Pagine: {result['num_pages']}")
    print(f"📋 Metadata: {list(result['metadata'].keys())}")

    # Salva TXT
    txt_path = txt_dir / f"{sentenza_id}.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(result['text'])
    print(f"\n💾 TXT salvato: {txt_path}")

    # Preview TXT
    print("\n📖 Preview TXT (primi 1000 caratteri):")
    print("-"*80)
    print(result['text'][:1000])
    print("-"*80)

    # Estrazione Markdown
    print("\n📝 Conversione Markdown...")
    markdown_text = extractor.extract_to_markdown()

    # Salva Markdown
    md_path = markdown_dir / f"{sentenza_id}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_text)
    print(f"💾 Markdown salvato: {md_path}")

    # Preview Markdown
    print("\n📖 Preview Markdown (primi 1000 caratteri):")
    print("-"*80)
    print(markdown_text[:1000])
    print("-"*80)

    extractor.close()

    print("\n" + "="*80)
    print("✅ ESTRAZIONE COMPLETATA")
    print("="*80)


if __name__ == '__main__':
    main()
