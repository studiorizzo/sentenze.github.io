# Sentenze Cassazione - Database Processing

## 🎯 Obiettivo

Processare le sentenze della Corte di Cassazione italiana con pipeline automatica:
- Estrazione testo da PDF
- Estrazione entità con LLM (Gemini API)
- Chunking semantico
- Embeddings per semantic search
- Output in formati strutturati

**Sistema file-based** (no database) per semplicità e portabilità.

---

## ✅ Stato Attuale

### Configurazione
- ✅ Repository GitHub configurato
- ✅ API Gemini configurata e funzionante (`gemini-2.5-flash-lite`)
- ✅ GitHub Secrets attivi (chiave API sicura)
- ✅ Limiti Gemini: 1000 richieste/giorno (gratuito)

### Dati Disponibili
- **Metadata**: ~500 sentenze indicizzate in `metadata/_all_sentenze.json`
- **PDF**: Disponibili in locale (link fonte: Cassazione)
- **TXT estratti**: 1 sentenza test processata

### Script Funzionanti
1. **`scripts/html_metadata_extractor.py`** - Estrae metadata da HTML
2. **`scripts/final_pdf_extractor.py`** - Estrae testo pulito da PDF (PyMuPDF)
3. **`scripts/llm_entity_extractor.py`** - Estrae entità con Gemini API
4. **`scripts/chunking_processor.py`** - Chunking semantico + fixed-size
5. **`scripts/embeddings_generator.py`** - Genera embeddings (sentence-transformers)
6. **`scripts/markdown_generator.py`** - Genera markdown AI-optimized
7. **`auto_process_all.py`** - Pipeline completa automatica

---

## 📂 Struttura Repository

### Input
```
data/
├── html/          # HTML con metadata sentenze (fonte: Cassazione)
├── pdf/           # PDF sentenze (da caricare)
```

### Output
```
metadata/          # Indice generale sentenze (solo _all_sentenze.json)
txt/               # Testo estratto pulito
entities/          # Entità estratte da LLM (vuoto - da processare)
chunks/            # Chunks semantici per RAG
embeddings/        # Vettori embeddings (vuoto - da processare)
markdown_ai/       # Markdown con YAML frontmatter
```

### Scripts
```
scripts/           # Processori individuali (PDF, LLM, chunking, ecc.)
auto_process_all.py    # Pipeline automatica completa
test_gemini_api.py     # Test API Gemini
```

---

## 🔧 Pipeline Implementata

**Input:** PDF sentenza → **Output:** 6 formati strutturati

1. **PDF → TXT** (PyMuPDF)
   - Estrazione pulita con gestione layout Cassazione
   - Rimozione watermark, header formattato
   - Output: `txt/{id}.txt`

2. **TXT → Entità** (Gemini API)
   - Estrazione: presidente, relatore, parti, avvocati, norme, precedenti
   - Output: `entities/{id}_entities.json`

3. **TXT → Chunks** (Semantic + Fixed)
   - Chunking semantico: metadata, fatti, motivi, dispositivo
   - Chunking fixed-size: 512 token con overlap
   - Output: `chunks/{id}_chunks.json`

4. **Chunks → Embeddings** (sentence-transformers)
   - Modello: `paraphrase-multilingual-mpnet-base-v2`
   - 768 dimensioni
   - Output: `embeddings/{id}_embeddings.npz`

5. **TXT + Entità → Markdown AI**
   - YAML frontmatter con metadata strutturati
   - Sezioni formattate per AI
   - Output: `markdown_ai/{id}.md`

---

## 🚀 Come Processare le Sentenze

### Esecuzione Locale

```bash
# 1. Configura API key
export GOOGLE_API_KEY='tua-chiave-api'

# 2. Processa tutte le sentenze
python3 auto_process_all.py
```

### Esecuzione su GitHub Actions

Il workflow automatico processa sentenze usando il secret `SENTENZE` configurato.

**Limiti attuali:**
- 1000 sentenze/giorno (rate limit Gemini)
- ~500 sentenze totali → processabili in 1 giorno

---

## 📊 Metriche

**Sentenze disponibili:** ~500
**Sentenze processate:** 1 (test)
**Da processare:** ~499

**Formati output per sentenza:**
- TXT (estrazione pulita)
- Entities (JSON)
- Chunks (JSON)
- Embeddings (NumPy)
- Markdown AI (YAML + MD)

**Spazio stimato:** ~150KB per sentenza → ~75MB totali

---

## 📝 Prossimi Passi

1. **Test pipeline su campione** (5-10 sentenze)
2. **Validazione qualità output** (entità, chunks)
3. **Processing batch completo** (~500 sentenze)
4. **Ottimizzazione chunking** (separazione motivi ricorrente/corte)
5. **Sistema di monitoraggio** (progressi, errori)

---

## 🔗 Link Utili

- **Repository:** https://github.com/studiorizzo/sentenze.github.io
- **Branch sviluppo:** `claude/parse-rulings-database-015Go7YALbJMcYAB5hV8CJjP`
- **Gemini API:** https://aistudio.google.com/
- **Rate limits:** 1K req/day, 15 req/min, 250K tokens/min

---

**Ultimo aggiornamento:** 2025-11-22
**Status:** ✅ Pipeline pronta, API configurata, test funzionanti
