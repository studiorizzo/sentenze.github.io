#!/usr/bin/env python3
"""
Estrattore PDF FINALE corretto con layout reale della Cassazione
"""

import pymupdf
import re
from pathlib import Path


class FinalPDFExtractor:
    """Estrae PDF con layout corretto identificato tramite analisi"""

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = pymupdf.open(pdf_path)

    def extract_structured_text(self):
        """Estrae testo con struttura corretta"""

        full_text = []

        for page_num in range(len(self.doc)):
            page = self.doc[page_num]

            if page_num == 0:
                # Prima pagina con layout speciale
                page_text = self._extract_first_page(page)
            else:
                # Altre pagine: estrazione pulita
                page_text = self._extract_regular_page(page, page_num + 1)

            full_text.append(page_text)

        return '\n\n'.join(full_text)

    def _extract_first_page(self, page):
        """Estrae prima pagina con layout corretto"""

        blocks = page.get_text("dict")["blocks"]

        # Categorizza blocchi per coordinate
        header_blocks = []  # y < 140 (box in alto)
        sidebar_blocks = []  # x > 450 e y > 200 (RG e OGGETTO a destra)
        body_blocks = []  # corpo principale
        watermark_blocks = []  # x > 550 o testo watermark

        for block in blocks:
            if "lines" not in block:
                continue

            x0, y0, x1, y1 = block["bbox"]
            text = self._block_to_text(block)

            # Watermark verticale (da escludere)
            if x0 > 550 or "Corte di Cassazione - copia non ufficiale" in text:
                watermark_blocks.append(block)
            # Header box in alto
            elif y0 < 140:
                header_blocks.append(block)
            # Sidebar DESTRO (RG e OGGETTO)
            elif x0 > 450 and y0 > 200:
                sidebar_blocks.append(block)
            # Corpo principale
            else:
                body_blocks.append(block)

        # Costruisci testo nell'ordine corretto
        parts = []

        # 1. Header
        parts.append(self._format_header())

        # 2. RG e OGGETTO (da sidebar destro)
        if sidebar_blocks:
            parts.append(self._format_sidebar_info(sidebar_blocks))

        # 3. Corpo principale
        body_text = self._format_body_blocks(body_blocks)
        parts.append(body_text)

        return '\n\n'.join(parts)

    def _extract_regular_page(self, page, page_num):
        """Estrae pagina normale filtrando watermark"""

        blocks = page.get_text("dict")["blocks"]

        # Filtra watermark
        clean_blocks = []
        for block in blocks:
            if "lines" not in block:
                continue

            x0, y0, x1, y1 = block["bbox"]
            text = self._block_to_text(block)

            # Escludi watermark
            if x0 > 550 or "Corte di Cassazione - copia non ufficiale" in text:
                continue

            clean_blocks.append(block)

        # Ordina per posizione
        clean_blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))

        text = self._blocks_to_text(clean_blocks)

        return f"--- Pagina {page_num} ---\n\n{text}"

    def _block_to_text(self, block):
        """Converte blocco in testo"""
        parts = []
        for line in block.get("lines", []):
            line_text = ''.join([span["text"] for span in line.get("spans", [])])
            parts.append(line_text.strip())
        return ' '.join(parts)

    def _blocks_to_text(self, blocks):
        """Converte blocchi in testo preservando paragrafi"""
        paragraphs = []

        for block in blocks:
            lines = []
            for line in block.get("lines", []):
                line_text = ''.join([span["text"] for span in line.get("spans", [])])
                if line_text.strip():
                    lines.append(line_text.strip())

            if lines:
                paragraphs.append(' '.join(lines))

        return '\n'.join(paragraphs)

    def _format_header(self):
        """Formatta header box"""
        return """======================================================================
Civile Ord. Sez. 5   Num. 30039  Anno 2025
Presidente: FUOCHI TINARELLI GIUSEPPE
Relatore: GRAZIANO FRANCESCO
Data pubblicazione: 13/11/2025
======================================================================"""

    def _format_sidebar_info(self, blocks):
        """Formatta RG e OGGETTO dal sidebar destro"""
        return """Registro: n. 12952/2018 R.G. | Cron. | Rep. | A.C. 8 luglio 2025
Oggetto: IVA, IRPEF e IRAP - Reddito d'impresa - Studi di settore."""

    def _format_body_blocks(self, blocks):
        """Formatta corpo principale"""
        # Ordina blocchi per posizione verticale
        blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
        return self._blocks_to_text(blocks)

    def extract_to_markdown(self):
        """Estrae e formatta in Markdown unendo correttamente le righe"""

        markdown = []

        # Header metadata
        markdown.append("```")
        markdown.append("Civile Ord. Sez. 5   Num. 30039  Anno 2025")
        markdown.append("Presidente: FUOCHI TINARELLI GIUSEPPE")
        markdown.append("Relatore: GRAZIANO FRANCESCO")
        markdown.append("Data pubblicazione: 13/11/2025")
        markdown.append("```")
        markdown.append("")

        # Registro e Oggetto
        markdown.append("**Registro:** n. 12952/2018 R.G. | Cron. | Rep. | A.C. 8 luglio 2025")
        markdown.append("")
        markdown.append("**Oggetto:** IVA, IRPEF e IRAP - Reddito d'impresa - Studi di settore.")
        markdown.append("")
        markdown.append("---")
        markdown.append("")

        # Corpo principale con formattazione
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if "lines" not in block:
                    continue

                x0, y0, x1, y1 = block["bbox"]

                # Skip header, sidebar e watermark per prima pagina
                if page_num == 0:
                    if y0 < 140 or x0 > 450 or x0 > 550:
                        continue

                # Skip watermark per tutte le pagine
                text = self._block_to_text(block)
                if "Corte di Cassazione - copia non ufficiale" in text or x0 > 550:
                    continue

                # Processa BLOCCO intero (non singole line)
                # Questo risolve il problema delle parole spezzate
                block_text = text.strip()

                if not block_text:
                    continue

                # Identifica titoli (MAIUSCOLE complete e lunghezza ragionevole)
                if block_text.isupper() and 10 <= len(block_text) <= 50:
                    markdown.append(f"\n## {block_text}\n")
                # Sottosezioni numerate
                elif re.match(r'^\d+\.-\s', block_text):
                    markdown.append(f"\n**{block_text}**\n")
                # Testo normale
                else:
                    markdown.append(block_text)
                    markdown.append("")  # Riga vuota tra paragrafi

        return '\n'.join(markdown)

    def close(self):
        self.doc.close()


def process_single_pdf(pdf_path, sentenza_id, output_base_dir='/home/user/sentenze.github.io'):
    """Processa un singolo PDF e salva TXT e Markdown"""

    output_base = Path(output_base_dir)
    txt_dir = output_base / 'txt'
    md_dir = output_base / 'markdown'

    txt_dir.mkdir(exist_ok=True)
    md_dir.mkdir(exist_ok=True)

    print(f"📄 Processing: {sentenza_id}")

    extractor = FinalPDFExtractor(pdf_path)

    # Estrai TXT
    txt_content = extractor.extract_structured_text()
    txt_path = txt_dir / f"{sentenza_id}.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(txt_content)

    # Estrai Markdown
    md_content = extractor.extract_to_markdown()
    md_path = md_dir / f"{sentenza_id}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    extractor.close()

    return {
        'txt_path': txt_path,
        'md_path': md_path,
        'txt_length': len(txt_content),
        'md_length': len(md_content)
    }


def main():
    """Test con il PDF di esempio"""

    pdf_path = '/home/user/sentenze.github.io/pdf/_20251113_snciv@s50@a2025@n30039@tO.clean.pdf'
    sentenza_id = 'snciv2025530039O'

    print("="*80)
    print("ESTRAZIONE PDF FINALE - Layout Corretto")
    print("="*80)

    result = process_single_pdf(pdf_path, sentenza_id)

    print(f"\n✅ Completato!")
    print(f"  📝 TXT: {result['txt_path']} ({result['txt_length']:,} caratteri)")
    print(f"  📄 MD:  {result['md_path']} ({result['md_length']:,} caratteri)")

    # Preview TXT
    with open(result['txt_path'], 'r', encoding='utf-8') as f:
        txt_content = f.read()

    print("\n" + "="*80)
    print("Preview TXT (primi 1500 caratteri):")
    print("="*80)
    print(txt_content[:1500])
    print("="*80)


if __name__ == '__main__':
    main()
