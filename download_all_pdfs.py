#!/usr/bin/env python3
"""
SCRIPT 1: PDF DOWNLOADER
Da eseguire SUL TUO COMPUTER (non in questo ambiente)

Scarica tutti i PDF delle sentenze dai file HTML usando Playwright.

Requisiti:
    pip install playwright beautifulsoup4
    python -m playwright install chromium

Usage:
    python download_all_pdfs.py
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from pathlib import Path
import json
import time
import re


class PDFDownloader:
    """Scarica PDF delle sentenze usando Playwright"""

    def __init__(self, html_dir='html', pdf_dir='pdf', log_file='download_log.json'):
        self.html_dir = Path(html_dir)
        self.pdf_dir = Path(pdf_dir)
        self.log_file = Path(log_file)

        self.pdf_dir.mkdir(exist_ok=True)

        # Carica log esistente
        self.log = self._load_log()

    def _load_log(self):
        """Carica log dei download precedenti"""
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'downloaded': [],
            'failed': [],
            'skipped': []
        }

    def _save_log(self):
        """Salva log"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)

    def parse_html_for_sentenze(self, html_file):
        """Estrae info sentenze da un file HTML"""

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

            # PDF URL
            pdf_elem = card.find('img', class_='pdf')
            if pdf_elem and pdf_elem.get('data-arg'):
                pdf_path = pdf_elem['data-arg']
                pdf_path = pdf_path.replace('%3F', '?').replace('%3D', '=').replace('%26', '&').replace('%2F', '/')
                sentenza['pdf_url'] = f"https://www.italgiure.giustizia.it{pdf_path}"

                # Nome file PDF
                match = re.search(r'(sn(?:civ|pen)@[^/]+\.pdf)', pdf_path)
                if match:
                    sentenza['pdf_filename'] = match.group(1)

            if sentenza.get('id') and sentenza.get('pdf_url'):
                sentenze.append(sentenza)

        return sentenze

    def download_pdf(self, sentenza, browser):
        """Scarica un singolo PDF"""

        sentenza_id = sentenza['id']
        pdf_url = sentenza['pdf_url']
        pdf_filename = sentenza.get('pdf_filename', f"{sentenza_id}.pdf")
        pdf_path = self.pdf_dir / pdf_filename

        # Skip se già scaricato
        if pdf_path.exists():
            print(f"  ⏭️  Già esistente: {pdf_filename}")
            self.log['skipped'].append(sentenza_id)
            return True

        # Skip se già tentato e fallito
        if sentenza_id in self.log['failed']:
            print(f"  ⏭️  Saltato (fallito in precedenza): {sentenza_id}")
            return False

        try:
            print(f"  📥 Download: {sentenza_id}")

            context = browser.new_context(
                accept_downloads=True,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()

            # Intercetta download
            with page.expect_download(timeout=30000) as download_info:
                page.goto(pdf_url, wait_until='domcontentloaded', timeout=30000)
                download = download_info.value

            # Salva file
            download.save_as(pdf_path)

            file_size = pdf_path.stat().st_size
            print(f"  ✅ Scaricato: {file_size:,} bytes")

            context.close()

            self.log['downloaded'].append(sentenza_id)
            return True

        except Exception as e:
            print(f"  ❌ Errore: {e}")
            self.log['failed'].append(sentenza_id)
            return False

    def download_all(self, max_files=None, delay=1):
        """Scarica tutti i PDF dagli HTML"""

        print("="*80)
        print("DOWNLOAD PDF SENTENZE")
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

        print(f"\n📊 Totale sentenze da scaricare: {len(all_sentenze)}")

        if max_files:
            all_sentenze = all_sentenze[:max_files]
            print(f"⚠️  Limitato a prime {max_files} sentenze per test")

        # Avvia Playwright
        print("\n🌐 Avvio browser...")
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            print("📥 Inizio download...\n")

            downloaded = 0
            failed = 0
            skipped = 0

            for i, sentenza in enumerate(all_sentenze, 1):
                print(f"[{i}/{len(all_sentenze)}] {sentenza['id']}")

                success = self.download_pdf(sentenza, browser)

                if success:
                    if sentenza['id'] in self.log.get('downloaded', []):
                        downloaded += 1
                    else:
                        skipped += 1
                else:
                    failed += 1

                # Salva log ogni 10 download
                if i % 10 == 0:
                    self._save_log()

                # Pausa tra download
                if delay > 0 and i < len(all_sentenze):
                    time.sleep(delay)

            browser.close()

        # Salva log finale
        self._save_log()

        # Report finale
        print("\n" + "="*80)
        print("📊 REPORT FINALE")
        print("="*80)
        print(f"✅ Scaricati: {downloaded}")
        print(f"⏭️  Saltati (già esistenti): {skipped}")
        print(f"❌ Falliti: {failed}")
        print(f"📁 Directory PDF: {self.pdf_dir.absolute()}")
        print(f"📋 Log salvato: {self.log_file.absolute()}")
        print("="*80)


def main():
    """Esegui download"""

    import argparse

    parser = argparse.ArgumentParser(description='Scarica PDF sentenze')
    parser.add_argument('--html-dir', default='html', help='Directory con file HTML')
    parser.add_argument('--pdf-dir', default='pdf', help='Directory output PDF')
    parser.add_argument('--max', type=int, help='Numero massimo PDF da scaricare (per test)')
    parser.add_argument('--delay', type=float, default=1.0, help='Secondi di pausa tra download')

    args = parser.parse_args()

    downloader = PDFDownloader(
        html_dir=args.html_dir,
        pdf_dir=args.pdf_dir
    )

    downloader.download_all(
        max_files=args.max,
        delay=args.delay
    )


if __name__ == '__main__':
    main()
