# 🔍 Scraper Sentenze CIVILE - QUINTA SEZIONE

Sistema automatizzato per scaricare e gestire le sentenze della Cassazione (CIVILE - QUINTA SEZIONE) dal sito italgiure.giustizia.it.

## 📋 Panoramica

Questo scraper è progettato per identificare **automaticamente le nuove sentenze** pubblicate settimanalmente, evitando il problema della paginazione dinamica (dove le nuove sentenze modificano i numeri di pagina).

### Il Problema

Il sito della Cassazione aggiunge nuove sentenze settimanalmente. Se oggi la pagina 1 contiene le sentenze più recenti, tra una settimana queste potrebbero essere alla pagina 50. **Non possiamo salvare "pagina 1, pagina 2..." perché i riferimenti cambiano!**

### La Soluzione

1. **Download HTML** → Scarica le prime 10-50 pagine (sentenze più recenti)
2. **Parsing Metadata** → Estrae gli ID univoci di ogni sentenza (es. `snciv2025530039O`)
3. **Download PDF** → Confronta con quelli già scaricati e scarica solo i nuovi
4. **Integrazione** → I PDF vengono poi processati dalla pipeline esistente

## 🚀 Quick Start

### Esecuzione locale completa (3 step)

```bash
# STEP 1: Scarica le prime 10 pagine HTML
python3 scraper/scripts/1_download_html.py --pages 10

# STEP 2: Parsa HTML e genera JSON metadata
python3 scraper/scripts/2_parse_html_to_json.py

# STEP 3: Scarica PDF delle nuove sentenze
python3 scraper/scripts/3_download_pdfs.py --max 5
```

### Esecuzione automatica via GitHub Actions

1. Vai su **Actions** nel repository
2. Seleziona "Weekly Scraper - CIVILE QUINTA"
3. Clicca "Run workflow"
4. (Opzionale) Modifica i parametri
5. Clicca "Run workflow"

Il workflow esegue automaticamente tutti e 3 gli step e committa i risultati!

## 📁 Struttura del Progetto

```
scraper/
├── scripts/
│   ├── 1_download_html.py      # Scarica pagine HTML
│   ├── 2_parse_html_to_json.py # Estrae metadata → JSON
│   └── 3_download_pdfs.py      # Scarica PDF nuovi
├── data/
│   └── html/                   # Pagine HTML scaricate
├── docs/
│   └── USAGE.md               # Guida dettagliata
└── README.md                  # Questo file

metadata/
└── metadata_cassazione.json   # Metadata di tutte le sentenze

data/pdf/
└── *.pdf                      # PDF delle sentenze
```

## 🔧 Script Dettagliati

### 1. Download HTML (`1_download_html.py`)

Scarica le prime N pagine di risultati dal sito della Cassazione.

**Uso:**
```bash
# Scarica 10 pagine (default)
python3 scraper/scripts/1_download_html.py

# Scarica 50 pagine
python3 scraper/scripts/1_download_html.py --pages 50

# Mostra il browser (debug)
python3 scraper/scripts/1_download_html.py --no-headless
```

**Output:** File HTML in `scraper/data/html/`
**Formato:** `page_0001_20251123_143022.html`

**Tempo:** ~2-3 secondi per pagina (10 pagine = ~30 sec)

---

### 2. Parse HTML → JSON (`2_parse_html_to_json.py`)

Estrae i metadata da tutti i file HTML e crea `metadata/metadata_cassazione.json`.

**Uso:**
```bash
# Parsing standard
python3 scraper/scripts/2_parse_html_to_json.py

# Specifica directory custom
python3 scraper/scripts/2_parse_html_to_json.py \
  --html-dir scraper/data/html \
  --output metadata/metadata_cassazione.json
```

**Output:** `metadata/metadata_cassazione.json`

**Struttura JSON:**
```json
{
  "metadata": {
    "generated_at": "2025-11-23T14:30:00",
    "total_sentences": 100,
    "html_files_processed": 10,
    "source": "italgiure.giustizia.it",
    "filters": "CIVILE - QUINTA SEZIONE"
  },
  "sentences": [
    {
      "id": "snciv2025530039O",
      "sezione": "QUINTA",
      "archivio": "CIVILE",
      "tipo_provvedimento": "Ordinanza",
      "numero": "30039",
      "data_pubblicazione": "13/11/2025",
      "ecli": "ECLI:IT:CASS:2025:30039CIV",
      "anno": "2025",
      "data_udienza": "08/07/2025",
      "presidente": "FUOCHI TINARELLI GIUSEPPE",
      "relatore": "GRAZIANO FRANCESCO",
      "pdf_url": "https://www.italgiure.giustizia.it/xway/application/nif/clean/hc.dll?verbo=attach&db=snciv&id=./20251113/snciv@s50@a2025@n30039@tO.clean.pdf"
    }
  ]
}
```

**Tempo:** ~1 secondo per file HTML (10 file = ~10 sec)

---

### 3. Download PDF (`3_download_pdfs.py`)

Legge `metadata_cassazione.json`, confronta con i PDF già esistenti in `data/pdf/`, e scarica solo i nuovi.

**Uso:**
```bash
# Scarica TUTTI i PDF nuovi
python3 scraper/scripts/3_download_pdfs.py

# Scarica solo i primi 10 (per testare)
python3 scraper/scripts/3_download_pdfs.py --max 10

# Aumenta il delay tra download (evita rate limiting)
python3 scraper/scripts/3_download_pdfs.py --delay 3.0

# Percorsi custom
python3 scraper/scripts/3_download_pdfs.py \
  --json metadata/metadata_cassazione.json \
  --pdf-dir data/pdf
```

**Output:** File PDF in `data/pdf/` con formato: `snciv2025530039O.pdf`

**Tempo:** ~2-4 secondi per PDF (dipende dalla dimensione)

**Gestione errori:**
- ✅ Retry automatico (max 3 tentativi)
- ✅ Timeout (30 secondi)
- ✅ Rate limiting detection (pausa 5 sec se 403)
- ✅ Verifica Content-Type e dimensione file

---

## ⚙️ GitHub Actions

### Workflow disponibili

#### `scrape-sentenze-weekly.yml` - Scraping settimanale automatico

**Schedulazione:** Ogni lunedì alle 2:00 AM UTC (3:00 AM CET)

**Cosa fa:**
1. Scarica le prime 20 pagine HTML
2. Parsa HTML → JSON
3. Scarica PDF nuovi (max 50)
4. Committa e pusha automaticamente

**Esecuzione manuale:**
1. Actions → "Weekly Scraper - CIVILE QUINTA"
2. Run workflow
3. Parametri opzionali:
   - `pages`: Numero pagine HTML (default: 20)
   - `max_pdfs`: Numero max PDF (default: 50)

---

## 📊 Workflow Tipico Settimanale

```bash
# Lunedì mattina (automatico via GitHub Actions)
# oppure manualmente:

# 1. Scarica le prime 20 pagine (le più recenti)
python3 scraper/scripts/1_download_html.py --pages 20

# 2. Estrai metadata
python3 scraper/scripts/2_parse_html_to_json.py

# 3. Scarica solo le nuove sentenze (es. ~50-100 nuove a settimana)
python3 scraper/scripts/3_download_pdfs.py

# 4. I PDF vengono poi processati dalla pipeline esistente
python3 scripts/final_pdf_extractor.py  # (pipeline esistente)
```

## 🔍 Identificazione Sentenze Nuove

Il sistema traccia le sentenze già elaborate usando l'**ID univoco** della sentenza (es. `snciv2025530039O`).

### Come funziona:

1. Lo script 3 legge tutti i PDF già presenti in `data/pdf/`
2. Estrae gli ID dai nomi dei file (supporta vari formati)
3. Confronta con le sentenze in `metadata_cassazione.json`
4. Scarica solo quelle **non ancora presenti**

### Formati supportati per i file PDF esistenti:

- `snciv2025530039O.pdf` (formato pulito)
- `_20251113_snciv@s50@a2025@n30039@tO.clean.pdf` (formato originale del sito)

Entrambi vengono riconosciuti come la stessa sentenza!

---

## 🛠️ Requisiti

### Localmente

```bash
# Python 3.8+
pip install selenium beautifulsoup4 requests

# Chrome/Chromium (per Selenium)
# Ubuntu/Debian
sudo apt-get install google-chrome-stable

# macOS
brew install --cask google-chrome
```

### GitHub Actions

✅ Tutto configurato automaticamente (Chrome, Python, dipendenze)

---

## 📈 Statistiche Attese

- **Sentenze totali CIVILE - QUINTA**: ~55.000+
- **Nuove sentenze/settimana**: ~50-150
- **Tempo download HTML** (20 pagine): ~60 secondi
- **Tempo parsing**: ~20 secondi
- **Tempo download PDF** (100 sentenze): ~5-10 minuti

---

## 🐛 Troubleshooting

### "chromedriver not found"
```bash
# Assicurati che Chrome sia installato
google-chrome --version

# Selenium scarica automaticamente il driver giusto
```

### "Timeout durante download HTML"
Il sito potrebbe essere lento. Prova:
- Aumentare il numero di pagine gradualmente
- Eseguire in orari notturni
- Usare `--no-headless` per vedere cosa succede

### "Download PDF falliti (403)"
Rate limiting del server. Soluzioni:
- Aumenta `--delay` (es. `--delay 3.0`)
- Riduci `--max` (scarica in batch)
- Attendi qualche ora e riprova

### "File JSON non contiene sentenze"
Verifica che gli HTML siano stati scaricati correttamente:
```bash
ls -lh scraper/data/html/
```

Se i file sono vuoti o troppo piccoli, il sito potrebbe aver cambiato struttura.

---

## 🔄 Integrazione con Pipeline Esistente

Dopo aver scaricato i PDF, puoi processarli con gli script esistenti:

```bash
# 1. Scarica nuove sentenze (scraper)
python3 scraper/scripts/3_download_pdfs.py

# 2. Processa i PDF (pipeline esistente)
python3 scripts/final_pdf_extractor.py \
  --pdf-dir data/pdf \
  --txt-dir data/txt \
  --md-dir data/markdown

# 3. Genera altri formati (opzionale)
python3 scripts/markdown_generator.py
python3 scripts/chunking_processor.py
# ecc...
```

---

## 📝 Note Importanti

1. **Non sovrascrivere `_all_sentenze.json`**: Il file `metadata_cassazione.json` è separato e dedicato solo alle sentenze CIVILE - QUINTA SEZIONE.

2. **Pulizia HTML**: I file HTML in `scraper/data/html/` possono essere eliminati dopo il parsing (il JSON contiene tutti i metadata necessari).

3. **Duplicati**: Lo script 2 gestisce automaticamente i duplicati se scarichi la stessa pagina più volte (es. pagina 1 in date diverse).

4. **Rate Limiting**: Il sito della Cassazione può limitare i download. Usa delay appropriati (1.5-3 secondi).

---

## 🎯 Prossimi Step

Dopo aver testato lo scraper:

1. ✅ Verifica che i PDF vengano scaricati correttamente
2. ✅ Testa la GitHub Action manualmente
3. ✅ Abilita lo scheduling settimanale
4. ✅ Integra con la pipeline esistente di processing
5. ✅ (Opzionale) Aggiungi notifiche via email/Slack

---

## 📧 Supporto

Per problemi o domande:
- Apri una Issue su GitHub
- Controlla i log della GitHub Action in `Actions` → `Weekly Scraper`

---

**Sviluppato per automatizzare il download delle sentenze CIVILE - QUINTA SEZIONE**
