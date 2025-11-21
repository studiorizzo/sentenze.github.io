#!/usr/bin/env python3
"""
SCRIPT 2: PDF PROCESSOR
Da eseguire SUL TUO COMPUTER o in questo ambiente

Processa tutti i PDF scaricati ed estrae TXT e Markdown.
Usa il final_pdf_extractor.py che abbiamo già sviluppato.

Requisiti:
    pip install pymupdf beautifulsoup4

Usage:
    python process_all_pdfs.py
    python process_all_pdfs.py --max 10  # processa solo primi 10 per test
"""

from pathlib import Path
import json
from final_pdf_extractor import FinalPDFExtractor, process_single_pdf
from bs4 import BeautifulSoup
import re
import time


class PDFProcessor:
    """Processa tutti i PDF e genera TXT e Markdown"""

    def __init__(self, html_dir='html', pdf_dir='pdf', txt_dir='txt', md_dir='markdown'):
        self.html_dir = Path(html_dir)
        self.pdf_dir = Path(pdf_dir)
        self.txt_dir = Path(txt_dir)
        self.md_dir = Path(md_dir)

        self.txt_dir.mkdir(exist_ok=True)
        self.md_dir.mkdir(exist_ok=True)

        self.log_file = Path('processing_log.json')
        self.log = self._load_log()

    def _load_log(self):
        """Carica log processing"""
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'processed': [],
            'failed': [],
            'skipped': []
        }

    def _save_log(self):
        """Salva log"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)

    def parse_html_for_sentenze(self, html_file):
        """Estrae mapping ID -> PDF filename"""

        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.find_all('div', class_='card')

        sentenze = []
        for card in cards:
            sentenza = {}

            # ID
            id_elem = card.find('span', {'data-role': 'content', 'data-arg': 'id'})
            if id_elem:
                sentenza['id'] = id_elem.text.strip()

            # PDF filename
            pdf_elem = card.find('img', class_='pdf')
            if pdf_elem and pdf_elem.get('data-arg'):
                pdf_path = pdf_elem['data-arg']
                match = re.search(r'(sn(?:civ|pen)@[^/]+\.pdf)', pdf_path)
                if match:
                    sentenza['pdf_filename'] = match.group(1)

            # Numero e anno (per riferimento)
            num_elem = card.find('span', {'data-role': 'content', 'data-arg': 'numcard'})
            if num_elem:
                sentenza['numero'] = num_elem.text.strip()

            anno_elem = card.find('span', {'data-role': 'content', 'data-arg': 'anno'})
            if anno_elem:
                sentenza['anno'] = anno_elem.text.strip()

            if sentenza.get('id') and sentenza.get('pdf_filename'):
                sentenze.append(sentenza)

        return sentenze

    def process_single(self, sentenza):
        """Processa un singolo PDF"""

        sentenza_id = sentenza['id']
        pdf_filename = sentenza['pdf_filename']
        pdf_path = self.pdf_dir / pdf_filename

        # Check se già processato
        txt_path = self.txt_dir / f"{sentenza_id}.txt"
        md_path = self.md_dir / f"{sentenza_id}.md"

        if txt_path.exists() and md_path.exists():
            print(f"  ⏭️  Già processato")
            self.log['skipped'].append(sentenza_id)
            return True

        # Check se PDF esiste
        if not pdf_path.exists():
            print(f"  ❌ PDF non trovato: {pdf_filename}")
            self.log['failed'].append({
                'id': sentenza_id,
                'reason': 'PDF not found'
            })
            return False

        try:
            # Usa il final_pdf_extractor
            result = process_single_pdf(
                pdf_path=str(pdf_path),
                sentenza_id=sentenza_id,
                output_base_dir='.'
            )

            print(f"  ✅ TXT: {result['txt_length']:,} chars | MD: {result['md_length']:,} chars")

            self.log['processed'].append(sentenza_id)
            return True

        except Exception as e:
            print(f"  ❌ Errore: {e}")
            self.log['failed'].append({
                'id': sentenza_id,
                'reason': str(e)
            })
            return False

    def process_all(self, max_files=None):
        """Processa tutti i PDF"""

        print("="*80)
        print("PROCESSING PDF → TXT + MARKDOWN")
        print("="*80)

        # Trova tutti gli HTML
        html_files = sorted(self.html_dir.glob('*.html'))

        if not html_files:
            print(f"❌ Nessun file HTML trovato in {self.html_dir}")
            return

        print(f"\n📁 Trovati {len(html_files)} file HTML")

        # Estrai tutte le sentenze
        all_sentenze = []
        for html_file in html_files:
            sentenze = self.parse_html_for_sentenze(html_file)
            all_sentenze.extend(sentenze)
            print(f"  {html_file.name}: {len(sentenze)} sentenze")

        print(f"\n📊 Totale sentenze: {len(all_sentenze)}")

        if max_files:
            all_sentenze = all_sentenze[:max_files]
            print(f"⚠️  Limitato a prime {max_files} per test")

        # Conta PDF disponibili
        available_pdfs = sum(1 for s in all_sentenze if (self.pdf_dir / s['pdf_filename']).exists())
        print(f"📄 PDF disponibili: {available_pdfs}/{len(all_sentenze)}")

        print("\n🔄 Inizio processing...\n")

        processed = 0
        failed = 0
        skipped = 0

        start_time = time.time()

        for i, sentenza in enumerate(all_sentenze, 1):
            print(f"[{i}/{len(all_sentenze)}] {sentenza['id']} ({sentenza.get('numero')}/{sentenza.get('anno')})")

            success = self.process_single(sentenza)

            if success:
                if sentenza['id'] in self.log.get('processed', []):
                    processed += 1
                else:
                    skipped += 1
            else:
                failed += 1

            # Salva log ogni 10
            if i % 10 == 0:
                self._save_log()

                # Stima tempo rimanente
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                remaining = (len(all_sentenze) - i) * avg_time
                print(f"  ⏱️  Tempo stimato rimanente: {remaining/60:.1f} minuti")

        # Salva log finale
        self._save_log()

        elapsed_total = time.time() - start_time

        # Report finale
        print("\n" + "="*80)
        print("📊 REPORT FINALE")
        print("="*80)
        print(f"✅ Processati: {processed}")
        print(f"⏭️  Saltati (già esistenti): {skipped}")
        print(f"❌ Falliti: {failed}")
        print(f"⏱️  Tempo totale: {elapsed_total/60:.1f} minuti")
        print(f"⚡ Media: {elapsed_total/len(all_sentenze):.2f} sec/sentenza")
        print(f"\n📁 Directory output:")
        print(f"  TXT: {self.txt_dir.absolute()}")
        print(f"  MD:  {self.md_dir.absolute()}")
        print(f"📋 Log: {self.log_file.absolute()}")
        print("="*80)


def main():
    """Esegui processing"""

    import argparse

    parser = argparse.ArgumentParser(description='Processa PDF sentenze')
    parser.add_argument('--html-dir', default='html', help='Directory con file HTML')
    parser.add_argument('--pdf-dir', default='pdf', help='Directory con PDF')
    parser.add_argument('--txt-dir', default='txt', help='Directory output TXT')
    parser.add_argument('--md-dir', default='markdown', help='Directory output Markdown')
    parser.add_argument('--max', type=int, help='Numero massimo da processare (per test)')

    args = parser.parse_args()

    processor = PDFProcessor(
        html_dir=args.html_dir,
        pdf_dir=args.pdf_dir,
        txt_dir=args.txt_dir,
        md_dir=args.md_dir
    )

    processor.process_all(max_files=args.max)


if __name__ == '__main__':
    main()
