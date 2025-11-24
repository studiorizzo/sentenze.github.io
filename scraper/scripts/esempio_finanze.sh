#!/bin/bash
# ESEMPI DI UTILIZZO - SCRAPER MEF FINANZE

echo "🎯 ESEMPI DI UTILIZZO - SCRAPER SENTENZE MEF"
echo "============================================="
echo ""

# Esempio 1: Sentenze Cassazione anno 2022
echo "📌 Esempio 1: Tutte le sentenze Cassazione del 2022"
echo "python3 scraper/scripts/finanze_download_html.py \\"
echo "  --ente \"Corte di Cassazione\" \\"
echo "  --data-da \"01/01/2022\" \\"
echo "  --data-a \"31/12/2022\""
echo ""

# Esempio 2: Sentenze massimate 2023
echo "📌 Esempio 2: Solo sentenze massimate del 2023"
echo "python3 scraper/scripts/finanze_download_html.py \\"
echo "  --ente \"Corte di Cassazione\" \\"
echo "  --data-da \"01/01/2023\" \\"
echo "  --data-a \"31/12/2023\" \\"
echo "  --massimate"
echo ""

# Esempio 3: Ricerca per parole chiave
echo "📌 Esempio 3: Ricerca per parole chiave 'IVA'"
echo "python3 scraper/scripts/finanze_download_html.py \\"
echo "  --ente \"Corte di Cassazione\" \\"
echo "  --parole \"IVA\" \\"
echo "  --data-da \"01/01/2024\" \\"
echo "  --data-a \"31/12/2024\""
echo ""

# Esempio 4: Sentenza specifica per numero
echo "📌 Esempio 4: Sentenza specifica per numero e anno"
echo "python3 scraper/scripts/finanze_download_html.py \\"
echo "  --ente \"Corte di Cassazione\" \\"
echo "  --numero \"38131\" \\"
echo "  --anno \"2022\""
echo ""

# Esempio 5: Modalità visibile (per debug)
echo "📌 Esempio 5: Modalità visibile del browser (debug)"
echo "python3 scraper/scripts/finanze_download_html.py \\"
echo "  --ente \"Corte di Cassazione\" \\"
echo "  --data-da \"01/01/2022\" \\"
echo "  --data-a \"31/01/2022\" \\"
echo "  --no-headless"
echo ""

echo "💡 Per eseguire un esempio, copia e incolla il comando!"
echo ""
echo "📚 Altri enti disponibili:"
echo "   - Corte di Cassazione"
echo "   - Commissione Tributaria Centrale"
echo "   - Commissione Tributaria Provinciale"
echo "   - Commissione Tributaria Regionale"
echo "   (verifica i nomi esatti sul sito)"
