# 📚 Sentenze Cassazione - Database & Extraction Pipeline

Sistema completo per scaricare, estrarre e processare le sentenze della Corte Suprema di Cassazione italiana.

## 🎯 Panoramica

Questo progetto fornisce una pipeline automatizzata per:
- Scaricare PDF di sentenze dal sito italgiure.giustizia.it (55.627+ sentenze)
- Estrarre testo strutturato con layout corretto
- Generare file TXT e Markdown ottimizzati per applicazioni AI
- (Opzionale) Creare database SQLite per ricerche avanzate

## 📁 Struttura del Repository

```
sentenze.github.io/
├── scripts/                    # 🔧 Script principali
│   ├── download_all_pdfs.py   # Download automatico PDF
│   ├── process_all_pdfs.py    # Estrazione TXT + Markdown
│   └── final_pdf_extractor.py # Motore di estrazione
│
├── database/                   # 💾 Script database (opzionali)
│   ├── database_schema.sql    # Schema SQLite/PostgreSQL
│   ├── create_database.py     # Creazione e popolamento
│   └── query_example.py       # Esempi di query
│
├── tests/                      # 🧪 Test e sviluppo
│   └── ...                     # Script di test vari
│
├── docs/                       # 📖 Documentazione
│   ├── README_SCRIPTS.md      # Guida completa script
│   └── README_DATABASE.md     # Guida database
│
└── data/                       # 📊 Dati (non in git)
    ├── html/                   # File HTML scaricati (5563 pagine)
    ├── pdf/                    # PDF sentenze (~1.5 GB)
    ├── txt/                    # Testo estratto (~1.3 GB)
    └── markdown/               # Markdown per AI (~1.3 GB)
```

## 🚀 Quick Start

### 1. Installazione

```bash
# Clona il repository
git clone https://github.com/studiorizzo/sentenze.github.io
cd sentenze.github.io

# Installa dipendenze
pip install playwright beautifulsoup4 pymupdf

# Installa browser per Playwright
python -m playwright install chromium
```

### 2. Preparazione Dati

```bash
# Crea struttura cartelle
mkdir -p data/{html,pdf,txt,markdown}

# Metti i tuoi file HTML in data/html/
# (scaricali manualmente dal sito italgiure.giustizia.it)
```

### 3. Test Rapido (10 sentenze)

```bash
# Scarica 10 PDF
python scripts/download_all_pdfs.py --max 10 --html-dir data/html --pdf-dir data/pdf

# Processa i 10 PDF
python scripts/process_all_pdfs.py --max 10 --html-dir data/html --pdf-dir data/pdf --txt-dir data/txt --md-dir data/markdown

# Verifica output
ls data/pdf/       # 10 PDF
ls data/txt/       # 10 file .txt
ls data/markdown/  # 10 file .md
```

### 4. Processing Completo (55K sentenze)

```bash
# Download completo (~40-50 ore)
python scripts/download_all_pdfs.py --delay 1.5 --html-dir data/html --pdf-dir data/pdf

# Processing completo (~8-10 ore)
python scripts/process_all_pdfs.py --html-dir data/html --pdf-dir data/pdf --txt-dir data/txt --md-dir data/markdown
```

## 📖 Documentazione Completa

- **[Guida Script](docs/README_SCRIPTS.md)** - Istruzioni dettagliate per download e processing
- **[Guida Database](docs/README_DATABASE.md)** - Setup database opzionale per ricerche avanzate

## ✨ Caratteristiche

### Estrazione Avanzata
- ✅ Layout preservato (header, metadata, corpo testo)
- ✅ Rimozione watermark automatica
- ✅ Identificazione sezioni (FATTI DI CAUSA, RAGIONI DELLA DECISIONE, etc.)
- ✅ Testo continuo senza parole spezzate
- ✅ Metadata strutturati (RG, OGGETTO, giudici, date)

### Output Ottimizzato per AI
- **TXT**: Testo pulito con struttura chiara
- **Markdown**: Formattazione semantica
  - `##` per titoli principali
  - `**bold**` per sottosezioni numerate
  - Code blocks per metadata

### Robustezza
- 🔄 Ripresa automatica da interruzioni
- 📊 Log dettagliati (JSON)
- ⏭️ Skip automatico file già processati
- ⚡ Performance ottimizzate (PyMuPDF)

## 📊 Statistiche Dataset

- **Sentenze totali**: 55.627+
- **Archivi**: CIVILE (55.627), PENALE (22.786)
- **Sezioni**: Prima, Seconda, Terza, Quinta, Sesta, Lavoro, Unite
- **Anni**: 2020-2025
- **Spazio richiesto**: ~4 GB totale

## ⏱️ Tempi Stimati

| Operazione | Tempo | Note |
|------------|-------|------|
| Download HTML manuale | ~2-3 ore | 5563 pagine web |
| Download PDF (script) | 40-50 ore | Con delay 1.5s |
| Processing PDF | 8-10 ore | Estrazione TXT+MD |
| **Totale** | **~3 giorni** | Automatizzato |

## 🛠️ Requisiti Sistema

- **Python**: 3.8+
- **RAM**: 2 GB minimo
- **Disco**: 5 GB liberi
- **Internet**: Per download PDF
- **OS**: Linux, macOS, Windows

## 🔍 Esempio Output

### Input (HTML)
```html
<span data-role="content" data-arg="id">snciv2025530039O</span>
```

### Output TXT (data/txt/snciv2025530039O.txt)
```
======================================================================
Civile Ord. Sez. 5   Num. 30039  Anno 2025
Presidente: FUOCHI TINARELLI GIUSEPPE
Relatore: GRAZIANO FRANCESCO
Data pubblicazione: 13/11/2025
======================================================================

Registro: n. 12952/2018 R.G. | Cron. | Rep. | A.C. 8 luglio 2025
Oggetto: IVA, IRPEF e IRAP - Reddito d'impresa - Studi di settore.

ORDINANZA
sul ricorso (iscritto al n. 12952/2018 R.G.) proposto da:
GJYZELI ARDIAN (Codice Fiscale: GJY RDN 71B27 Z100S), ...
```

### Output Markdown (data/markdown/snciv2025530039O.md)
```markdown
\`\`\`
Civile Ord. Sez. 5   Num. 30039  Anno 2025
Presidente: FUOCHI TINARELLI GIUSEPPE
...
\`\`\`

**Registro:** n. 12952/2018 R.G. | Cron. | Rep. | A.C. 8 luglio 2025

## FATTI DI CAUSA

**1.- In punto di fatto e limitando l'esposizione...**
```

## 🐛 Troubleshooting

### Download fallisce con 503
Il server limita i download. Soluzioni:
- Aumenta `--delay` (es. 2.0 o 3.0)
- Esegui in orari notturni
- Riprendi dopo qualche ora

### Browser not found
```bash
python -m playwright install chromium
```

### Permission denied
Verifica permessi sulle cartelle data/

## 🤝 Contributi

Contributi benvenuti! Per bug, feature request o miglioramenti, apri una issue.

## 📄 Licenza

Questo progetto è per scopi di ricerca ed educativi. I dati delle sentenze sono di dominio pubblico (italgiure.giustizia.it).

## 🔗 Links Utili

- [Italgiure - Sentenze Cassazione](https://www.italgiure.giustizia.it/sncass/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [Playwright Python](https://playwright.dev/python/)

---

**Sviluppato per ricerca legale e applicazioni AI**
