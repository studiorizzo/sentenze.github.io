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

## 🔄 STEP IN CORSO

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
