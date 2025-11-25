# 🏛️ Sistema Scraping Sentenze MEF - Completo

Sistema completo per scraping, estrazione e analisi sentenze dal sito **def.finanze.it** (Ministero Economia e Finanze).

## 🎯 Obiettivo

Creare un sistema parallelo a quello di Cassazione per:
1. Scrapare sentenze rilevanti da MEF (con massime)
2. Estrarre testo completo + massime + intitolazioni
3. **Estrarre entities** (link a normative e precedenti) già taggati dal sito
4. Estrarre tab "Documenti citati"
5. Generare metadata JSON compatibili con Cassazione
6. Salvare TXT formattati

## 📊 Output Generati

```
metadata/
├── metadata_mef_2022.json              # Metadata compatibili con Cassazione
└── metadata_mef_2022_entities.json     # Entities aggregate

txt/mef/
├── mef202253813S.txt                   # Testo sentenza 38131/2022
├── mef202253830S.txt
└── ...

scraper/data/mef/
└── sentenze_lista_2022.json            # Lista intermedia (step 1)
```

## 🔄 Workflow Completo

### **Esecuzione via GitHub Actions** (Automatica)

1. Vai su **Actions** → **MEF Sentenze Scraper**
2. Click **Run workflow**
3. Parametri:
   - **Anno**: `2022`
   - **Solo massimate**: `true`
   - **Ente**: `Corte di Cassazione`
   - **Download dettagli**: `true`
4. Il workflow fa tutto automaticamente e committa i risultati

### **Esecuzione manuale** (Locale - per test)

```bash
# STEP 1: Scraping lista sentenze
python3 scraper/scripts/mef_1_scrape_sentenze.py \
  --anno 2022 \
  --ente "Corte di Cassazione" \
  --massimate \
  --output scraper/data/mef

# STEP 2: Download dettagli completi
python3 scraper/scripts/mef_2_download_dettagli.py \
  --input scraper/data/mef/sentenze_lista_2022.json \
  --output-json metadata/metadata_mef_2022.json \
  --output-txt txt/mef \
  --delay 2

# STEP 3: Estrazione entities aggregate (opzionale)
python3 scraper/scripts/mef_3_extract_entities.py \
  --input metadata/metadata_mef_2022.json \
  --output metadata/metadata_mef_2022_entities.json
```

## 📋 Struttura Metadata JSON

Compatibile con `metadata_cassazione_YYYY.json`:

```json
{
  "metadata": {
    "generated_at": "2024-11-24T15:30:00",
    "anno": "2022",
    "total_sentences": 139,
    "fonte": "MEF - def.finanze.it",
    "filters": {
      "anno": "2022",
      "ente": "Corte di Cassazione",
      "solo_massimate": true
    }
  },
  "sentences": [
    {
      "id": "mef2022538131S",
      "id_mef_guid": "{84B3CC19-CC89-46BE-B7FB-79EA80772CA2}",
      "url": "https://def.finanze.it/DocTribFrontend/getGiurisprudenzaDetail.do?id={...}",
      "fonte": "MEF - Ministero Economia e Finanze",
      "autorita": "Corte di Cassazione",
      "sezione": "5",
      "tipo_provvedimento": "Sentenza",
      "numero": "38131",
      "anno": "2022",
      "data_pubblicazione": "30/12/2022",
      "estremi": "Sentenza del 30/12/2022 n. 38131 - Corte di Cassazione - Sezione/Collegio 5",
      "intitolazione": "Cartella di pagamento - Accise - Imposta di fabbricazione...",
      "has_massima": true,
      "massima": "La Direttiva n. 92/12 ha inteso fissare...",
      "entities_count": 45,
      "entities_testo": [
        {
          "type": "normativa",
          "urn": "urn:doctrib::DLG:1995;504_art7",
          "text": "D.Lgs. n. 504 del 1995, art. 7",
          "parsed": {
            "type": "normativa",
            "kind": "DLG",
            "year": 1995,
            "number": 504,
            "article": 7
          }
        },
        {
          "type": "giurisprudenza",
          "urn": "urn:doctrib:CCO:SEN:2020;142",
          "text": "Corte cost. n.142/2020",
          "parsed": {
            "type": "giurisprudenza",
            "court": "CCO",
            "kind": "SEN",
            "year": 2020,
            "number": 142
          }
        }
      ],
      "entities_massima": [...],
      "documenti_citati_count": 12,
      "metadata": {
        "sentenza_sicot": false,
        "flag_stato": 0,
        "allegato": false
      }
    }
  ]
}
```

## 🔗 Entities Estratte

### **Cosa sono le entities**

Le entities sono **riferimenti normativi e giurisprudenziali già linkati** nel testo HTML del sito MEF.

Esempio nel testo:
```html
<a href="decodeurn?urn=urn:doctrib::DLG:1995;504_art7">D.Lgs. n. 504 del 1995, art. 7</a>
```

Lo scraper estrae automaticamente:
- **URN**: `urn:doctrib::DLG:1995;504_art7`
- **Testo visualizzato**: `D.Lgs. n. 504 del 1995, art. 7`
- **Parse strutturato**: `{kind: 'DLG', year: 1995, number: 504, article: 7}`

### **Tipi di entities**

1. **Normativa**: Leggi, decreti, regolamenti
   - DLG (Decreto Legislativo)
   - DPR (Decreto Presidente Repubblica)
   - L (Legge)
   - DL (Decreto Legge)
   - ecc.

2. **Giurisprudenza**: Precedenti sentenze
   - CCO (Corte Costituzionale)
   - CASS (Cassazione)
   - CTR (Commissione Tributaria Regionale)
   - ecc.

### **Tab "Documenti citati"**

Oltre ai link nel testo, il sito ha un tab dedicato "Documenti citati" con:
- Lista strutturata di tutti i documenti referenziati
- Normative citate
- Precedenti giurisprudenziali citati

Lo scraper estrae anche questi!

## 📊 Statistiche Entities (Step 3)

Lo script 3 genera statistiche aggregate:

```json
{
  "statistics": {
    "total_entities": 6234,
    "total_unique_normative": 145,
    "total_unique_giurisprudenza": 89,
    "sentences_with_entities": 137,
    "avg_entities_per_sentence": 45.3
  },
  "normative": {
    "top_20": [
      {
        "key": "DLG_1995_504_art7",
        "count": 89,
        "parsed": {...},
        "sentences_count": 45
      }
    ]
  },
  "giurisprudenza": {
    "top_20": [...]
  }
}
```

## 🎯 Vantaggi MEF vs Cassazione

| Aspetto | Cassazione | MEF |
|---------|-----------|-----|
| **Testo** | PDF → OCR | HTML già pronto ✅ |
| **Massime** | Da estrarre | Separate ✅ |
| **Entities** | Da estrarre con LLM | **Già linkate** ✅✅✅ |
| **Qualità** | Possibili errori OCR | Perfetto ✅ |
| **Velocità** | Lenta (PDF) | Velocissima (HTML) ✅ |
| **Link normativi** | No | **Sì con URN** ✅✅✅ |

## 🔥 Caratteristiche Uniche MEF

### 1. **Entities già pronte**
Non serve LLM per estrarre riferimenti normativi! Il sito li ha già linkati.

### 2. **URN strutturati**
Ogni riferimento ha un URN univoco parsabile:
```
urn:doctrib::DLG:1995;504_art7
         ↓      ↓    ↓    ↓   ↓
      doctrib  tipo anno num art
```

### 3. **Massime curate**
Le sentenze massimate hanno massime curate da Ce.R.D.E.F.

### 4. **Testo HTML pulito**
Niente problemi di OCR, formattazione perfetta.

## 🔄 Integrazione con Cassazione

### **Workflow di integrazione** (futuro)

```python
# 1. Carica metadata Cassazione
cassazione = json.load(open('metadata/metadata_cassazione_2022.json'))

# 2. Carica metadata MEF
mef = json.load(open('metadata/metadata_mef_2022.json'))

# 3. Match sentenze (stesso numero/anno)
for sent_mef in mef['sentences']:
    numero = sent_mef['numero']
    anno = sent_mef['anno']

    # Trova in Cassazione
    sent_cass = find_in_cassazione(numero, anno)

    if sent_cass:
        # 4. Arricchisci Cassazione con dati MEF
        sent_cass['has_massima_mef'] = sent_mef['has_massima']
        sent_cass['massima_mef'] = sent_mef['massima']
        sent_cass['entities_mef'] = sent_mef['entities_testo']
        sent_cass['url_mef'] = sent_mef['url']

        # 5. Confronta testi (censure?)
        if sent_mef['testo'] != sent_cass['testo']:
            sent_cass['testo_differisce'] = True
```

### **Casi d'uso integrazione**

1. **Arricchimento massime**: Sentenze Cassazione senza massima → prendi da MEF
2. **Entities automatiche**: Usa entities MEF invece di LLM
3. **Verifica censure**: Confronta testo MEF vs Cassazione
4. **Doppia fonte**: Validazione incrociata

## 🚀 Performance

| Step | Tempo | Output |
|------|-------|--------|
| Step 1 (lista) | ~2 min | 139 sentenze |
| Step 2 (dettagli) | ~10 min | 139 TXT + entities |
| Step 3 (aggregate) | ~5 sec | Statistiche |
| **TOTALE** | **~12 min** | **Sistema completo** |

## 📝 Note Importanti

### **Censure nel testo**
Il testo MEF può contenere **censure** rispetto a quello di Cassazione (dati sensibili, nomi, ecc.).

### **Non tutte le sentenze**
MEF contiene solo sentenze "rilevanti" selezionate, non tutte quelle della Cassazione.

### **Massime curate**
Solo alcune sentenze hanno massime (quelle con flag `has_massima: true`).

### **Affidabilità entities**
Le entities linkate sono **affidabili al 100%** perché create manualmente dal sito.

## 🔧 Troubleshooting

### Errore 403
Il sito blocca? Lo scraper usa Selenium con headers realistici, dovrebbe funzionare sempre.

### XML non trovato
La variabile JavaScript `xmlDettaglio` non esiste? Controlla che il sito non abbia cambiato struttura.

### Entities vuote
Se non ci sono link nel testo, è normale. Non tutte le sentenze hanno lo stesso livello di linking.

## 📚 Prossimi Step

1. ✅ Sistema scraping completo
2. ✅ Estrazione entities
3. ⏳ Integrazione con metadata Cassazione
4. ⏳ Dashboard visualizzazione entities
5. ⏳ Analisi grafo citazioni

## 🤝 Contributi

Sistema creato per `sentenze.github.io` - Raccolta e analisi sentenze tributarie.
