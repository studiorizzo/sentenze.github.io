# Database Sentenze della Cassazione

## 📊 Risultati dei Test

### ✅ Cosa Funziona

1. **Estrazione metadati da HTML** - Funziona perfettamente
   - Estrae tutti i dati: ID, numero, anno, sezione, date, giudici, ECLI
   - Ricostruisce correttamente gli URL dei PDF
   - Identifica univocamente ogni sentenza

2. **Estrazione testo da PDF** - Testato con successo
   - Estrae testo completo (24.088 caratteri dal PDF di test)
   - Converte in Markdown per applicazioni AI
   - Gestisce PDF multi-pagina (12 pagine nel test)

3. **Database SQLite** - Creato e testato
   - Schema completo con indici per performance
   - 10 sentenze inserite con successo
   - Query veloci e statistiche funzionanti

### ⚠️ Limitazione Trovata

**Download automatico PDF**: Il server italgiure.giustizia.it restituisce errore 503 (Service Unavailable) per i download automatici. Probabilmente richiede:
- Cookie di sessione validi
- Token CSRF
- Protezioni anti-bot

## 🗄️ Schema Database

### Opzioni Database

#### **SQLite** (✅ Consigliato per iniziare)
- **Pro**: Nessun server, file singolo, semplice, veloce
- **Contro**: Non adatto per accesso concorrente massivo
- **Ideale per**: 55.000 sentenze, applicazioni AI locali

#### **PostgreSQL** (per produzione futura)
- **Pro**: Full-text search avanzato, scalabile, concorrenza
- **Contro**: Richiede server separato
- **Ideale per**: Applicazione web pubblica, ricerche complesse

### Tabelle Principali

#### `sentenze`
Tabella principale con tutti i dati:
```sql
- id (TEXT PRIMARY KEY)           -- snciv2025530039O
- numero, anno, ecli              -- Identificatori
- archivio, sezione               -- CIVILE/PENALE, PRIMA/SECONDA/etc
- tipo_provvedimento              -- Ordinanza/Sentenza/Decreto
- data_deposito, data_udienza     -- Date
- presidente, relatore            -- Giudici
- pdf_url, pdf_filename           -- Link e identificatore PDF
- testo_completo                  -- Testo estratto dal PDF
- testo_markdown                  -- Formato Markdown per AI
- testo_length, pdf_num_pages     -- Statistiche
```

#### `processing_log`
Log di tutte le operazioni (download, estrazione, errori)

#### `batch_metadata`
Tracking delle pagine HTML elaborate (1-5563)

### Indici
- Per anno, sezione, archivio
- Per numero/anno (ricerche veloci)
- Per ECLI (standard europeo)

## 🚀 Workflow Proposto

### Opzione A: Semi-Automatica (Consigliata)

1. **Tu scarichi i PDF manualmente** con il browser
   - Salvi nella cartella `pdf/`
   - Naming: `snciv@s50@a2025@n30039@tO.clean.pdf`

2. **Io processo tutto automaticamente**:
   ```bash
   python3 process_all.py
   ```
   - Legge tutti gli HTML dalla cartella `html/`
   - Estrae metadati
   - Trova i PDF corrispondenti in `pdf/`
   - Estrae il testo completo
   - Popola il database

3. **Risultato**: Database completo pronto per AI

### Opzione B: Completamente Automatica (Richiede sviluppo)

Uso **Selenium/Playwright** per:
- Simulare browser reale
- Gestire cookie/sessioni
- Scaricare automaticamente tutti i PDF

**Tempo sviluppo**: ~2-3 ore
**Vantaggi**: Completamente hands-off
**Svantaggi**: Più fragile (dipende dal sito)

## 📈 Capacità e Performance

### Dati Stimati (55.627 sentenze totali)

Basandomi sul PDF di test (24KB, 12 pagine, 24.000 caratteri):

- **Dimensione PDF totali**: ~1.3 GB
- **Dimensione testo estratto**: ~1.3 GB
- **Dimensione database**: ~2-3 GB
- **Tempo estrazione** (con PDF già scaricati): ~2-3 ore
- **Tempo download manuale**: Dipende da te 😊

### Database Performance

Con SQLite e 55.627 sentenze:
- Query per ID: <1ms
- Query per anno/sezione: ~10-50ms
- Full-text search: ~100-500ms (con FTS5)
- Statistiche aggregate: ~50-200ms

## 🔧 Script Disponibili

### `parse_html_test.py`
Estrae metadati da un file HTML

### `parse_pdf_test.py`
Estrae testo da un PDF (plain text e Markdown)

### `test_full_pipeline.py`
Test completo: HTML → Download PDF → Estrazione

### `create_database.py`
Crea database e popola con i dati

### `database_schema.sql`
Schema completo del database

### `query_example.py`
Esempi di query e statistiche

## 🎯 Prossimi Passi

### Per te:
1. Decidere approccio (A o B)
2. Se A: continuare a scaricare PDF manualmente
3. Caricarmi i file HTML (5563 pagine)

### Per me:
1. Creare `process_all.py` - Script master che:
   - Processa tutti gli HTML
   - Abbina i PDF
   - Estrae tutto il testo
   - Popola il database
   - Genera report di progresso

2. (Opzionale) Implementare download automatico con Selenium

## 💡 Per Applicazioni AI

### Formato Ottimale
Il testo in **Markdown** è ideale per:
- LLM (GPT, Claude, etc.)
- RAG (Retrieval Augmented Generation)
- Embedding per semantic search

### Esempio di uso con AI:
```python
# Recupera sentenza dal DB
sentenza = db.get_sentenza('snciv2025530039O')

# Usa il testo markdown per AI
prompt = f"""
Analizza questa sentenza:

{sentenza['testo_markdown']}

Estrai: tema principale, articoli citati, decisione
"""

response = ai_model.generate(prompt)
```

## ❓ Domande?

- Preferisci SQLite o PostgreSQL?
- Opzione A (semi-auto) o B (full-auto)?
- Hai già scaricato altri HTML oltre al primo?
- Vuoi che proceda con lo script master?
