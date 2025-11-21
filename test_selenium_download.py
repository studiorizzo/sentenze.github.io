#!/usr/bin/env python3
"""
Test rapido: Selenium può scaricare PDF dal sito della Cassazione?
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def test_selenium_download():
    """Test se Selenium riesce a scaricare un PDF"""

    print("="*80)
    print("TEST SELENIUM - Download PDF")
    print("="*80)

    # URL del PDF della sentenza 30039
    pdf_url = "https://www.italgiure.giustizia.it/xway/application/nif/clean/hc.dll?verbo=attach&db=snciv&id=./20251113/snciv@s50@a2025@n30039@tO.clean.pdf"

    # Directory download
    download_dir = "/home/user/sentenze.github.io/test_selenium_downloads"
    os.makedirs(download_dir, exist_ok=True)

    print(f"\n📁 Download directory: {download_dir}")
    print(f"🔗 PDF URL: {pdf_url}")

    # Configura Chrome in headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Nessuna finestra
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')

    # Configura download automatico
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # Non aprire PDF nel browser
    }
    chrome_options.add_experimental_option("prefs", prefs)

    try:
        print("\n🌐 Avvio Chrome headless...")
        driver = webdriver.Chrome(options=chrome_options)

        print("📥 Tentativo download PDF...")
        driver.get(pdf_url)

        # Aspetta che il download completi (max 30 secondi)
        print("⏳ Attendo completamento download...")
        timeout = 30
        start_time = time.time()

        while time.time() - start_time < timeout:
            files = os.listdir(download_dir)
            # Cerca file PDF (non .crdownload che è temporaneo)
            pdf_files = [f for f in files if f.endswith('.pdf')]

            if pdf_files:
                print(f"✅ Download completato: {pdf_files[0]}")
                file_path = os.path.join(download_dir, pdf_files[0])
                file_size = os.path.getsize(file_path)
                print(f"📊 Dimensione file: {file_size:,} bytes")

                driver.quit()

                print("\n" + "="*80)
                print("🎉 SUCCESSO! Selenium può scaricare i PDF!")
                print("="*80)
                return True

            time.sleep(1)

        print("❌ Timeout: nessun file scaricato in 30 secondi")
        driver.quit()
        return False

    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

if __name__ == '__main__':
    success = test_selenium_download()

    if success:
        print("\n✅ Selenium FUNZIONA → Possiamo implementare download automatico")
    else:
        print("\n❌ Selenium NON funziona → Serve soluzione alternativa")
