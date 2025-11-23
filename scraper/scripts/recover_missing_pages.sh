#!/bin/bash
# Script per recuperare pagine mancanti 3688-4064

echo "🔄 Recupero Pagine Mancanti: 3688-4064"
echo "========================================"
echo ""

# Directory di lavoro
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "📍 Directory progetto: $PROJECT_ROOT"
echo ""

# STEP 1: Scarica le pagine mancanti
echo "📥 STEP 1: Download pagine 3688-4064..."
echo "----------------------------------------"
python3 scraper/scripts/1_download_html_range.py \
    --start 3688 \
    --end 4064 \
    --output scraper/data/html

echo ""
echo "✓ Download completato!"
echo ""

# STEP 2: Parsa gli HTML e aggiorna il JSON (modalità incrementale)
echo "📖 STEP 2: Parsing HTML → JSON (incrementale)..."
echo "------------------------------------------------"
python3 scraper/scripts/2_parse_html_to_json.py \
    --input scraper/data/html \
    --output metadata/metadata_cassazione_2025.json

echo ""
echo "✅ Recupero completato!"
echo ""
echo "📊 Verifica risultati:"
echo "  - File HTML: scraper/data/html/"
echo "  - JSON aggiornato: metadata/metadata_cassazione_2025.json"
echo ""
