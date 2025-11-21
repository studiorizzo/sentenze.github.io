#!/usr/bin/env python3
"""
Test con Playwright: può scaricare PDF dal sito della Cassazione?
"""

from playwright.sync_api import sync_playwright
import time
import os
from pathlib import Path

def test_playwright_download():
    """Test download PDF con Playwright"""

    print("="*80)
    print("TEST PLAYWRIGHT - Download PDF")
    print("="*80)

    # URL del PDF
    pdf_url = "https://www.italgiure.giustizia.it/xway/application/nif/clean/hc.dll?verbo=attach&db=snciv&id=./20251113/snciv@s50@a2025@n30039@tO.clean.pdf"

    # Directory download
    download_dir = Path("/home/user/sentenze.github.io/test_playwright_downloads")
    download_dir.mkdir(exist_ok=True)

    print(f"\n📁 Download directory: {download_dir}")
    print(f"🔗 PDF URL: {pdf_url}")

    try:
        with sync_playwright() as p:
            print("\n🌐 Avvio browser Chromium...")

            # Lancia browser
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            # Crea context con download abilitato
            context = browser.new_context(
                accept_downloads=True,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            page = context.new_page()

            print("📥 Navigazione verso PDF...")

            # Intercetta download
            download_info = None

            with page.expect_download() as download:
                page.goto(pdf_url, wait_until='networkidle', timeout=30000)
                download_info = download.value

            if download_info:
                # Salva il file
                file_path = download_dir / f"sentenza_30039_test.pdf"
                download_info.save_as(file_path)

                file_size = file_path.stat().st_size
                print(f"✅ Download completato!")
                print(f"📄 File: {file_path}")
                print(f"📊 Dimensione: {file_size:,} bytes ({file_size/1024:.1f} KB)")

                browser.close()

                print("\n" + "="*80)
                print("🎉 SUCCESSO! Playwright può scaricare i PDF!")
                print("="*80)
                return True

            else:
                print("❌ Nessun download intercettato")
                browser.close()
                return False

    except Exception as e:
        print(f"❌ Errore: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_playwright_download()

    if success:
        print("\n✅ PLAYWRIGHT FUNZIONA → Posso implementare download automatico per tutte le 55K sentenze")
    else:
        print("\n❌ PLAYWRIGHT NON funziona → Serve approccio diverso")
