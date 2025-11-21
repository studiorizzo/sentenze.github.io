# 📚 Scripts per Download e Processing Sentenze

Questi script ti permettono di scaricare ed elaborare tutte le sentenze della Cassazione.

## 🎯 Workflow Completo

```
HTML (5563 file) → DOWNLOAD PDF (55K sentenze) → PROCESS (TXT + Markdown)
```

---

## 📥 Script 1: Download PDF

**File:** `download_all_pdfs.py`

**Cosa fa:**
- Legge tutti i file HTML dalla cartella `html/`
- Estrae gli URL dei PDF (uno per ogni sentenza)
- Scarica i PDF usando Playwright (browser automatico)
- Salva i PDF nella cartella `pdf/`
- Mantiene un log dei download (`download_log.json`)

### Requisiti

```bash
pip install playwright beautifulsoup4
python -m playwright install chromium
```

### Uso Base

```bash
# Scarica TUTTI i PDF (55.627 sentenze)
python download_all_pdfs.py

# Test con solo 10 PDF
python download_all_pdfs.py --max 10

# Con pausa di 2 secondi tra download (per non stressare il server)
python download_all_pdfs.py --delay 2.0
```

### Opzioni

- `--html-dir`: Directory con file HTML (default: `html`)
- `--pdf-dir`: Directory output PDF (default: `pdf`)
- `--max N`: Scarica solo primi N PDF (per test)
- `--delay SEC`: Secondi di pausa tra download (default: 1.0)

### Ripresa Automatica

Lo script tiene traccia di cosa ha già scaricato in `download_log.json`. Se interrompi e rilanci lo script, riparte da dove si era fermato saltando i PDF già scaricati.

### Performance Stimata

- **Velocità**: ~2-3 secondi per PDF (con delay 1.0)
- **Tempo totale**: ~40-50 ore per 55K sentenze
- **Spazio disco**: ~1.5 GB

---

## 🔄 Script 2: Processing PDF

**File:** `process_all_pdfs.py`

**Cosa fa:**
- Legge tutti i PDF dalla cartella `pdf/`
- Estrae il testo completo con layout corretto
- Genera 2 file per ogni sentenza:
  - `txt/ID.txt` - Testo pulito
  - `markdown/ID.md` - Markdown formattato per AI
- Mantiene un log del processing (`processing_log.json`)

### Requisiti

```bash
pip install pymupdf beautifulsoup4
```

### Uso Base

```bash
# Processa TUTTI i PDF
python process_all_pdfs.py

# Test con solo 10 PDF
python process_all_pdfs.py --max 10
```

### Opzioni

- `--html-dir`: Directory con file HTML (default: `html`)
- `--pdf-dir`: Directory con PDF (default: `pdf`)
- `--txt-dir`: Directory output TXT (default: `txt`)
- `--md-dir`: Directory output Markdown (default: `markdown`)
- `--max N`: Processa solo primi N (per test)

### Performance Stimata

- **Velocità**: ~0.5 secondi per PDF
- **Tempo totale**: ~8-10 ore per 55K sentenze
- **Spazio disco output**: ~2.5 GB (TXT + Markdown)

---

## 📋 Workflow Completo Passo-Passo

### Passo 1: Preparazione

```bash
# Crea struttura directory
mkdir -p html pdf txt markdown

# Metti i tuoi file HTML nella cartella html/
# (i 5563 file che scarichi dal sito)
```

### Passo 2: Test Download (IMPORTANTE!)

```bash
# Prima testa con 10 PDF
python download_all_pdfs.py --max 10

# Verifica che funzioni:
ls -lh pdf/  # Dovresti vedere 10 PDF
```

### Passo 3: Download Completo

```bash
# Scarica tutti i PDF (può richiedere ~40-50 ore)
# Puoi interrompere e riprendere quando vuoi
python download_all_pdfs.py --delay 1.5

# Monitora progresso:
tail -f download_log.json
```

### Passo 4: Test Processing

```bash
# Testa il processing su 10 PDF
python process_all_pdfs.py --max 10

# Verifica output:
ls txt/        # File .txt
ls markdown/   # File .md
```

### Passo 5: Processing Completo

```bash
# Processa tutti i PDF (~8-10 ore)
python process_all_pdfs.py

# Monitora progresso:
tail -f processing_log.json
```

---

## 🔍 Esempio Output

### Input
```
html/pagina 1 di 5563.html
```

### Dopo Download
```
pdf/snciv@s50@a2025@n30039@tO.clean.pdf  (24 KB)
```

### Dopo Processing
```
txt/snciv2025530039O.txt       (23.453 caratteri)
markdown/snciv2025530039O.md   (23.564 caratteri)
```

---

## ⚠️ Note Importanti

### Download Script

1. **Esegui sul TUO computer** (non in questo ambiente)
2. **Playwright richiede browser**: installalo con `python -m playwright install chromium`
3. **Può richiedere GIORNI**: usa `--delay` per evitare ban dal server
4. **È interrompibile**: puoi fermare e riprendere
5. **Controlla download_log.json** per vedere progressi e errori

### Processing Script

1. **Può girare ovunque** (anche in questo ambiente)
2. **Molto più veloce** del download (~8-10 ore vs 40-50 ore)
3. **Può girare in parallelo al download** (processa man mano che scarichi)
4. **È interrompibile**: salta file già processati

### Spazio Disco Necessario

- PDF: ~1.5 GB
- TXT: ~1.3 GB
- Markdown: ~1.3 GB
- **Totale: ~4 GB**

---

## 🐛 Troubleshooting

### "503 Service Unavailable"

Il server ti sta bloccando. Soluzioni:
- Aumenta `--delay` (es. 2.0 o 3.0 secondi)
- Esegui in orari notturni
- Riprova dopo qualche ora

### "Browser not installed"

```bash
python -m playwright install chromium
```

### "Module not found"

```bash
pip install playwright beautifulsoup4 pymupdf
```

### Download lento

- **Normale**: 2-3 sec/PDF è già veloce
- Il server limita i download per prevenire abusi
- Non aumentare velocità per evitare ban

---

## 📊 Log Files

### download_log.json
```json
{
  "downloaded": ["snciv2025530039O", ...],
  "failed": ["snciv2025530038O"],
  "skipped": ["snciv2025530037O"]
}
```

### processing_log.json
```json
{
  "processed": ["snciv2025530039O", ...],
  "failed": [{"id": "...", "reason": "..."}],
  "skipped": ["snciv2025530037O"]
}
```

---

## 🎯 Quick Start (TL;DR)

```bash
# 1. Installa dipendenze
pip install playwright beautifulsoup4 pymupdf
python -m playwright install chromium

# 2. Test (10 sentenze)
python download_all_pdfs.py --max 10
python process_all_pdfs.py --max 10

# 3. Full run (55K sentenze - richiede giorni)
python download_all_pdfs.py --delay 1.5 &
# Quando finisce (o in parallelo):
python process_all_pdfs.py
```

---

## 📞 Supporto

Se gli script non funzionano:
1. Verifica i requisiti installati
2. Controlla i log files (`.json`)
3. Prova prima con `--max 1` per testare
4. Verifica spazio disco disponibile
