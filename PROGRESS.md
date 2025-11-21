# Sentenze Cassazione - Pipeline Processing

## 📋 OBIETTIVO PROGETTO

Processare **60.000 sentenze** della Corte di Cassazione italiana con pipeline completa Legal NLP:
- Estrazione testo strutturato da PDF
- Named Entity Recognition (dual-model)
- Akoma Ntoso XML standard OASIS
- Chunking semantico + embeddings
- Knowledge Graph
- Output AI-optimized

**Sistema FILE-BASED** (no database), interrompibile e riprendibile.

---

## ✅ STEP COMPLETATI

### Step 1: Estrazione PDF e Parsing HTML ✅

**Script creati:**
- `scripts/final_pdf_extractor.py` - Estrazione PDF con layout corretto
- `auto_process_all.py` - Processore automatico completo

**Output generati:**
- `txt/` - Testo estratto pulito
- `markdown/` - Markdown con formattazione semantica

**Scoperte tecniche:**
- Layout PDF: header (y<140), sidebar destra (x>450), watermark (x>550)
- Coordinate-based extraction con PyMuPDF
- Block-level processing per evitare word splitting

**Formato TXT:**
```
======================================================================
Civile Ord. Sez. 5   Num. 30039  Anno 2025
Presidente: FUOCHI TINARELLI GIUSEPPE
Relatore: GRAZIANO FRANCESCO
Data pubblicazione: 13/11/2025
======================================================================

Registro: n. 12952/2018 R.G. | Cron. | Rep. | A.C. 8 luglio 2025
Oggetto: IVA, IRPEF e IRAP - Reddito d'impresa - Studi di settore.
...
```

**File esempio:**
- Input: `data/pdf/_20251113_snciv@s50@a2025@n30039@tO.clean.pdf`
- Output TXT: `txt/snciv2025530039O.txt` (23,453 caratteri)
- Output MD: `markdown/snciv2025530039O.md` (23,564 caratteri)

---

### Step 2: Named Entity Recognition ✅

**Script creato:**
- `ner_processor.py` - Dual-model NER con confronto

**Modelli utilizzati:**
1. **fabiod20/italian-legal-ner** - Specifico Cassazione
   - Trained su 9000 sentenze 2016-2021
   - Categorie: `RCR` (Ricorrente), `CTR` (Controricorrente), `CNS` (Consigliere), `RIC` (Ricorso)

2. **DeepMount00/Italian_NER_XXL_v2** - Generico italiano
   - 52 categorie
   - Categorie usate: `COGNOME`, `NOME`, `DATA`, `RAGIONE_SOCIALE`, `AVV_NOTAIO`

**Aggregation Strategy:**
- Usato `aggregation_strategy="average"` per unire subword tokenization
- Risolto problema: "GJYZELI" → `["G", "##J", "##Y", "##ZE", "##LI"]` ✗
- Dopo fix: "GJYZELI ARDIAN" → `["GJYZELI ARDIAN"]` ✓

**Output JSON struttura:**
```json
{
  "fabiod20_results": [...],
  "deepmount_results": [...],
  "comparison": {
    "fabiod20_unique": [...],
    "deepmount_unique": [...],
    "both_found": [...],
    "conflicts": [...]
  },
  "merged_best": [...]
}
```

**Risultati reali (sentenza snciv2025530039O):**
- fabiod20: 6 entità
- DeepMount00: 22 entità
- Merged: 26 entità totali
- Conflitti: 2

**File esempio:**
- Output: `entities/snciv2025530039O_entities.json`

**Conflitti rilevati:**
1. "AGENZIA DELLE ENTRATE" - fabiod20:`CTR` vs DeepMount:`RAGIONE_SOCIALE`
2. "Francesco Graziano" - fabiod20:`CNS` vs DeepMount:`AVV_NOTAIO`

---

## ✅ PIPELINE COMPLETA IMPLEMENTATA

### Step 3: Akoma Ntoso XML ✅

**Script creato:**
- `akoma_ntoso_generator.py` - Generatore XML standard OASIS LegalDocML v3.0

**Livello implementato:** MEDIO (bilanciato)

**Elementi implementati:**
- ✅ Meta/Identification: FRBRWork base con URI `/akn/it/judgment/cassazione/ANNO/NUMERO`
- ✅ Publication: data + numero sentenza
- ✅ References: TLCPerson (giudici, parti), TLCOrganization (Cassazione, enti)
- ✅ Header completo: court, section, judges, parties, docket number
- ✅ JudgmentBody: introduction (fatti), motivation (ragioni), decision (P.Q.M.)
- ✅ Conclusions: signature, location, date

**Elementi SCARTATI (per implementazione futura):**

1. **FRBRExpression + FRBRManifestation** (Meta/Identification)
   - Expression: versione linguistica/temporale con data
   - Manifestation: formato fisico (.xml, .pdf)
   - Motivo: Complessità FRBR alta, utilità limitata per AI
   - Quando: Se necessario per interoperabilità europea

2. **Classification + Keywords** (Meta)
   - Keywords estratte: materia, topics, categorie
   - Motivo: Richiede topic extraction ML separato
   - Quando: **Step 7** (con embeddings per keywords automatiche)

3. **Lifecycle** (Meta - eventi processuali)
   - Eventi: generation (udienza), publication, efficacy
   - Motivo: Date non sempre chiare, rischio errori
   - Quando: Se necessario per timeline processuale

4. **TLCConcept - Norme citate** (References)
   - Articoli: `art. 360, comma 1, n. 5), c.p.c.`
   - Leggi/DPR: `d.P.R. n. 633/1972`
   - Motivo: Citation extraction complessa, alto rischio errori
   - Quando: **Step 6** (Knowledge Graph - citations)

5. **Precedenti citati con URI** (References)
   - Citazioni: `Cass. Sez. 5, n. 25182/2020`
   - URI: `/akn/it/judgment/cassazione/2020/25182`
   - Motivo: Pattern matching sofisticato, mapping a DB
   - Quando: **Step 6** (Knowledge Graph - precedenti)

6. **Background** (JudgmentBody)
   - Sezione: Svolgimento del processo
   - Motivo: Difficile distinguere da "Fatti", non sempre presente
   - Quando: Solo se euristica migliora

**Euristica sezioni implementata:**
- `FATTI DI CAUSA` → introduction
- `RAGIONI DELLA DECISIONE` / `MOTIVI DELLA DECISIONE` → motivation
- `P.Q.M.` → decision

**File esempio:**
- Output: `akoma_ntoso/snciv2025530039O_akoma_ntoso.xml` (3,592 bytes)
- Validazione: ✅ Valid XML (xmllint)

**Struttura XML generata:**
```xml
<akomaNtoso>
  <judgment>
    <meta>
      <identification>FRBRWork</identification>
      <publication/>
      <references>5 entità</references>
    </meta>
    <header>court, judges, parties, docket</header>
    <judgmentBody>intro, motivation, decision</judgmentBody>
    <conclusions>signature, location, date</conclusions>
  </judgment>
</akomaNtoso>
```

---

## 📊 STRUTTURA DATI

### Input (da caricare su GitHub)
```
data/
├── html/           # HTML con metadata sentenze
│   └── pagina 1 di 5563.html
├── pdf/            # PDF sentenze (carica qui i PDF)
│   └── _20251113_snciv@s50@a2025@n30039@tO.clean.pdf
```

### Output Generati
```
txt/                # Testo estratto pulito
├── {id}.txt

markdown/           # Markdown AI-optimized
├── {id}.md

entities/           # NER results
├── {id}_entities.json

akoma_ntoso/        # XML standard OASIS (in corso)
├── {id}_akoma_ntoso.xml
```

### Script Principali
```
scripts/
├── final_pdf_extractor.py    # Estrazione PDF
├── download_all_pdfs.py       # Download automatico (locale)
├── process_all_pdfs.py        # Batch processing

ner_processor.py               # NER dual-model
auto_process_all.py            # Pipeline completa automatica
```

---

## 🔧 DIPENDENZE INSTALLATE

```bash
# PDF Processing
pymupdf
beautifulsoup4

# NER Models
transformers==4.57.1
torch==2.9.1+cpu

# Future steps
# lxml (per Akoma Ntoso XML)
# sentence-transformers (per embeddings)
```

---

## 🚀 COME CONTINUARE IN NUOVA CHAT

### 1. Carica contesto
```
Sto continuando il progetto "Sentenze Cassazione - Pipeline Processing".
Leggi PROGRESS.md per il contesto completo.

Step completati: 1 (PDF extraction), 2 (NER dual-model)
Step corrente: 3 (Akoma Ntoso XML - versione pragmatica)
```

### 2. Verifica stato attuale
```bash
# Lista file generati
ls -lh txt/ markdown/ entities/

# Testa script esistenti
python3 auto_process_all.py
python3 ner_processor.py
```

### 3. Riprendi da dove hai lasciato
- Consulta sezione "STEP IN CORSO"
- Verifica "TODO" per prossime azioni
- Continua implementazione

---

## 📝 NOTE TECNICHE IMPORTANTI

### Limitazioni Ambiente Attuale
❌ **Download PDF automatico NON funziona** in questo ambiente:
- requests → 503 Service Unavailable
- Playwright → Event loop error
- Selenium → Tab crashed

✅ **Soluzione:** Caricare PDF manualmente in `data/pdf/`

### Best Practices Scoperte

**1. Testing Modelli AI**
- ⚠️ Claude.ai propone strutture basate su assumzioni (usa regex)
- ✅ Claude Code testa REALMENTE i modelli e vede output effettivo
- **Sempre verificare struttura JSON con modelli reali**

**2. Subword Tokenization**
- Problema: BERT-based models spezzano parole
- Soluzione: `aggregation_strategy="average"` o `"max"`

**3. JSON Serialization**
- Problema: numpy.float32 non serializzabile
- Soluzione: Convertire con `.item()` prima di `json.dump()`

**4. File-based vs Database**
- Pro: facile debugging, interrompibile, no infrastruttura
- Contro: 60K × 7 files = 420K files (gestione filesystem)
- Decisione: OK per sviluppo, considerare DB per produzione

---

## 🎯 ROADMAP COMPLETA

### ✅ Completati
- [x] Step 1: PDF Extraction + HTML Parsing
- [x] Step 2: NER dual-model

### 🔄 In Corso
- [ ] Step 3: Akoma Ntoso XML (pragmatico)

### 📋 Da Fare
- [ ] Step 4: Chunking semantico + fixed-size
- [ ] Step 5: Embeddings locali
- [ ] Step 6: Knowledge Graph (JSON + Cypher)
- [ ] Step 7: Markdown AI-optimized con YAML frontmatter
- [ ] Step 8: Batch processing 60K sentenze
- [ ] Step 9: Sistema resume/checkpoint
- [ ] Step 10: Logging e monitoring

---

## 📈 METRICHE

**Sentenze processate:** 1 / 60,000 (0.002%)
**Token utilizzati (sessione corrente):** ~78K / 200K (39%)
**Step completati:** 2 / 10 (20%)

---

## 🔍 DOMANDE APERTE

1. **Akoma Ntoso:** Quale livello completezza serve? (scelto: MEDIO)
2. **Embeddings:** Modello da usare? (da decidere)
3. **Chunking:** Strategia semantic (sentence-transformers?) + chunk size?
4. **Knowledge Graph:** Neo4j o solo JSON?
5. **Batch size:** Quante sentenze processare per batch?

---

**Ultimo aggiornamento:** 2025-11-21
**Branch Git:** `claude/parse-rulings-database-015Go7YALbJMcYAB5hV8CJjP`
**Commit corrente:** `5e3e4af` - Add NER processing with dual-model comparison

---

### Step 4: Chunking Semantico + Fixed-Size ✅

**Script creato:**
- `chunking_processor.py` - Dual chunking strategy

**Chunking semantico implementato:**
- ✅ Metadata/header (intestazione)
- ✅ Fatti di causa
- ✅ Motivi (auto-detection pattern `\d+\.-`)
- ✅ Dispositivo (P.Q.M.)

**Chunking fixed-size:**
- ✅ RecursiveCharacterTextSplitter (LangChain)
- ✅ 512 token chunks, 50 token overlap
- ✅ Separators: `\n\n`, `\n`, `. `, ` `

**Token counting:**
- ✅ tiktoken (gpt-3.5-turbo encoding) per conteggio accurato

**File esempio:**
- Output: `chunks/snciv2025530039O_chunks.json`
  - 14 semantic chunks (1 metadata, 1 fatti, 11 motivi, 1 dispositivo)
  - 31 fixed chunks (~512 token each)

**⚠️ PROBLEMATICA IDENTIFICATA:**
Pattern `\d+\.-` cattura TUTTI i numeri nella sezione motivazione, senza distinguere:
- Motivi del ricorrente ("Con il primo motivo...")
- Risposte del giudice ("La censura è infondata...")

Risultato: chunk `003_motivo_1` = motivo ricorrente, chunk `004_motivo_2` = risposta giudice (semanticamente scorretto).

**TODO:** Dopo caricamento campione sentenze, analizzare pattern per split ricorrente/corte.

---

### Step 5: Embeddings con sentence-transformers ✅

**Script creato:**
- `embeddings_generator.py` - Generatore embeddings per semantic search

**Modello utilizzato:**
- `paraphrase-multilingual-mpnet-base-v2`
- 768 dimensioni
- Multilingue ottimizzato per italiano
- Locale (no API calls)

**Implementazione:**
- ✅ Batch processing (batch_size=32)
- ✅ Progress bar
- ✅ Output .npz compresso (NumPy)
- ✅ Test similarity search incluso

**File esempio:**
- Output: `embeddings/snciv2025530039O_embeddings.npz` (41KB)
- 14 embeddings × 768 dimensioni
- Include: embeddings, chunk_ids, chunk_types, model_name

**Test similarity:**
- Query: `001_metadata` → Top match: `002_fatti` (0.441)
- Embeddings catturano correttamente semantica

---

### Step 6: Knowledge Graph ❌ SALTATO

**Motivazione:**
- Richiede citation extraction complessa (precedenti + norme)
- Pattern matching sofisticato necessario
- Meglio implementare DOPO risoluzione chunking e con campione più grande

**TODO futuro:**
- Estrazione citazioni giurisprudenziali (Cass. n. X/anno)
- Estrazione norme (art. X c.p.c., leggi, DPR)
- Graph JSON + Cypher per Neo4j
- Link tra sentenze correlate

---

### Step 7: Markdown AI-Optimized ✅

**Script creato:**
- `markdown_generator.py` - Generatore Markdown con YAML frontmatter

**Frontmatter YAML estratto:**
```yaml
numero: "30039"
anno: 2025
sezione: "5"
rg_numero: "12952/2018"
data_pubblicazione: "13/11/2025"
presidente: "FUOCHI TINARELLI GIUSEPPE"
relatore: "GRAZIANO FRANCESCO"
ricorrente: "GJYZELI ARDIAN"
controricorrente: "AGENZIA DELLE ENTRATE"
esito: "rigetto"
spese: "€ 5.900,00"
materie: [IVA, IRPEF, IRAP, tributario, studi_settore, accertamento, reverse_charge]
precedenti: [{numero: "8053", anno: 2014}, ...]
norme: ["art. 112 c.p.c.", "art. 348-ter c.p.c.", ...]
```

**Body Markdown:**
- ✅ Titolo con numero/anno
- ✅ Sezione 👥 Parti
- ✅ Sezione 📖 Fatti di Causa
- ✅ Sezione ⚖️ Motivi e Valutazioni (preview 500 char)
- ✅ Sezione 🎯 Dispositivo
- ✅ Sezione 🔗 Entità Estratte (NER)

**Auto-extraction implementata:**
- ✅ Esito: rigetto/accoglimento (pattern matching)
- ✅ Spese: estrazione importo €
- ✅ Materie: keywords da oggetto + testo
- ✅ Precedenti: pattern `Cass. n. X del ../../....`
- ✅ Norme: pattern `art. X c.p.c.`, `d.P.R. n. X/anno`

**File esempio:**
- Output: `markdown_ai/snciv2025530039O.md` (9KB)
- Parsabile da AI (YAML structured)
- Leggibile da umani (Markdown formattato)

---

## 🔥 PROBLEMATICHE DA RISOLVERE

### 1. **PRIORITÀ ALTA: Chunking Motivi - Split Ricorrente/Corte**

**Problema:**
Il pattern `\d+\.-` cattura tutti i numeri sequenziali nella sezione "RAGIONI DELLA DECISIONE", creando chunks che mescolano:
- Argomentazioni del ricorrente
- Valutazioni del giudice

**Esempio reale (sentenza snciv2025530039O):**
```
003_motivo_1: "Con il primo motivo, il ricorrente denuncia..." ✓ (RICORRENTE)
004_motivo_2: "La censura è infondata..." ✗ (GIUDICE - ma numerato come motivo_2!)
005_motivo_3: "Con il secondo motivo..." ✗ (RICORRENTE - ma numerato come motivo_3!)
```

**Impatto:**
- **Semanticamente scorretto** per AI/RAG
- Query tipo "argomenti ricorrente" vs "motivazione giudice" non distinguibili
- Embeddings mischiano concetti opposti

**Soluzione proposta:**
1. Analisi pattern su campione rappresentativo (N>50-100 sentenze)
2. Identificare frasi comuni:
   - Inizio motivo ricorrente: "Con il [ordinale] motivo", "Il ricorrente denuncia/deduce"
   - Inizio risposta giudice: "La censura è [in]fondata", "Il motivo è [in]fondato", "La doglianza"
3. Implementare split intelligente:
   ```python
   chunk_id = f'{idx:03d}_ricorrente_motivo_{num}'
   type = 'argomentazione_ricorrente'
   
   chunk_id = f'{idx:03d}_corte_valutazione_{num}'
   type = 'valutazione_corte'
   ```

**Stato:** In attesa caricamento campione sentenze per analisi pattern

---

### 2. **PRIORITÀ MEDIA: Citation Extraction (Knowledge Graph)**

**Problema:**
L'estrazione di precedenti e norme è pattern-based semplice, con rischio errori:
- Precedenti: regex base per "Cass. n. X/anno"
- Norme: regex base per "art. X c.p.c."

**Limitazioni:**
- Non cattura tutte le varianti (es: "Cassazione, sezione X, sentenza n. Y")
- Non estrae contesto della citazione (perché è citato?)
- Non crea link/grafo tra sentenze correlate

**Soluzione proposta:**
1. Pattern matching robusto con varianti multiple
2. Estrazione contesto (frase che contiene citazione)
3. Validazione: check se sentenza citata esiste nel DB
4. Generazione graph JSON (nodi: sentenze, archi: citazioni)
5. Export Cypher per Neo4j (opzionale)

**Stato:** Da implementare dopo risoluzione chunking

---

### 3. **PRIORITÀ BASSA: Akoma Ntoso - Elementi Opzionali**

**Elementi scartati ma potenzialmente utili:**
- **Lifecycle**: eventi processuali (generazione, pubblicazione, efficacia)
- **Classification**: keywords automatiche da embeddings/clustering
- **TLCConcept**: norme citate con URI standard

**Quando implementare:**
- Lifecycle: se serve timeline processuale
- Classification: dopo Step 6 (clustering per auto-tagging)
- TLCConcept: insieme a Knowledge Graph

---

### 4. **PRIORITÀ BASSA: Batch Processing e Scaling**

**Problema:**
Scripts attuali processano 1 sentenza alla volta. Per 60K sentenze servono:
- Batch processing parallelizzato
- Sistema resume/checkpoint (se interrotto, riprende da dove aveva lasciato)
- Logging progressi
- Error handling robusto

**Soluzione proposta:**
```python
# Pseudo-code
for batch in sentenze_batches(size=100):
    with multiprocessing.Pool(n_workers) as pool:
        pool.map(process_sentenza, batch)
    save_checkpoint(batch_id)
```

**Stato:** Da implementare per produzione

---

## 📊 STRUTTURA DATI FINALE

### Output Completo per Sentenza

Per ogni sentenza `{id}` (es: `snciv2025530039O`):

```
txt/{id}.txt                      # Testo estratto pulito (23KB)
markdown/{id}.md                  # Markdown originale (23KB)
entities/{id}_entities.json       # NER dual-model (26 entità)
akoma_ntoso/{id}_akoma_ntoso.xml  # XML standard OASIS (3.5KB)
chunks/{id}_chunks.json           # Semantic + fixed chunks (14+31)
embeddings/{id}_embeddings.npz    # Vettori 768-dim (41KB)
markdown_ai/{id}.md               # Markdown AI-optimized + YAML (9KB)
```

**Totale per sentenza:** ~150KB

**Per 60K sentenze:** ~9GB totali

---

## 🎯 PROSSIMI PASSI

### Immediati (questa sessione)
- ✅ Completata pipeline base (Step 1-5, 7)
- ⏸️ Step 6 (Knowledge Graph) posticipato

### Short-term (prossime sessioni)
1. **Caricamento campione sentenze** (N>50-100)
2. **Analisi pattern chunking** (ricorrente vs corte)
3. **Fix chunking processor** con pattern identificati
4. **Test su campione** per validazione
5. **Rigenera chunks + embeddings + markdown** con fix

### Medium-term
1. **Implementazione Knowledge Graph** (citations + graph)
2. **Batch processing script** per 60K sentenze
3. **Sistema checkpoint/resume**
4. **Monitoring e logging**

### Long-term
1. **Ottimizzazione Akoma Ntoso** (elementi opzionali)
2. **Classification automatica** (clustering per keywords)
3. **API/Web interface** per semantic search
4. **Database deployment** (PostgreSQL/Neo4j)

---

## 📈 METRICHE FINALI

**Sentenze processate:** 1 / 60,000 (0.002%)
**Token utilizzati:** ~110K / 200K (55%)
**Step completati:** 6 / 7 core steps (85.7%)
**Script creati:** 7 (tutti funzionanti)
**Output formats:** 7 per sentenza

**Tempo stimato processing 60K:**
- PDF extraction: ~10 sec/sentenza = ~7 giorni
- NER dual-model: ~3 sec/sentenza = ~2 giorni
- Embeddings: ~2 sec/sentenza = ~1.5 giorni
- Totale: ~10-15 giorni (con parallelizzazione: 2-3 giorni)

---

**Ultimo aggiornamento:** 2025-11-21 (Pipeline base completa)
**Branch Git:** `claude/parse-rulings-database-015Go7YALbJMcYAB5hV8CJjP`
**Commit corrente:** `240d828` - Add AI-optimized Markdown generator with YAML frontmatter (Step 7)
