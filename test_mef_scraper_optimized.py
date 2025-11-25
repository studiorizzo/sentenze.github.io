#!/usr/bin/env python3
"""
Script di test per verificare l'ottimizzazione dello scraper MEF.
Esegue una singola ricerca di test per verificare che l'estrazione XML funzioni correttamente.
"""

import sys
sys.path.insert(0, 'scraper/scripts')

from mef_scrape_by_combinations import setup_driver, search_combination

def test_single_search():
    """Test con una singola ricerca"""
    print("🧪 TEST SCRAPER MEF OTTIMIZZATO")
    print("="*60)
    print("Testing single search with:")
    print("  - Anno: 2014")
    print("  - Ente: Corte di Cassazione")
    print("  - Materia: D040 (Accertamento imposte)")
    print("  - Classificazione: 0100 (Attività istruttoria)")
    print("  - Massimate: False")
    print()

    driver = None
    try:
        print("🔧 Setup browser...")
        driver = setup_driver(headless=False)  # Mostra browser per debug

        print("🔍 Esecuzione ricerca...")
        result = search_combination(
            driver=driver,
            materia_code="D040",
            classificazione_code="0100",
            anno="2014",
            ente="Corte di Cassazione",
            solo_massimate=False
        )

        print("\n" + "="*60)
        print("📊 RISULTATI TEST")
        print("="*60)

        num_risultati = result.get('num_risultati', -1)
        sentenze = result.get('sentenze', [])
        metadata = result.get('metadata', {})
        error = result.get('error')

        if error:
            print(f"❌ ERRORE: {error}")
            return False

        print(f"✅ Numero risultati: {num_risultati}")
        print(f"✅ Sentenze estratte: {len(sentenze)}")
        print(f"✅ Metadata: {metadata}")

        if len(sentenze) > 0:
            print(f"\n📄 Esempio prima sentenza:")
            first = sentenze[0]
            print(f"   ID: {first.get('id', 'N/A')}")
            print(f"   Estremi: {first.get('estremi', 'N/A')[:100]}...")
            print(f"   URL: {first.get('url', 'N/A')}")
            print(f"   Titoli: {len(first.get('titoli', []))}")

        # Verifica coerenza
        if num_risultati > 0 and len(sentenze) == num_risultati:
            print(f"\n✅ TEST PASSED: Estratti tutti i {num_risultati} risultati correttamente!")
            return True
        elif num_risultati == 0 and len(sentenze) == 0:
            print(f"\n✅ TEST PASSED: Nessun risultato trovato (OK)")
            return True
        else:
            print(f"\n⚠️  WARNING: Discrepanza tra num_risultati ({num_risultati}) e sentenze estratte ({len(sentenze)})")
            return False

    except Exception as e:
        print(f"\n❌ ERRORE TEST: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            print("\n🔧 Chiusura browser...")
            driver.quit()


if __name__ == "__main__":
    success = test_single_search()
    sys.exit(0 if success else 1)
