# 🔄 MEF Scraper per Combinazioni Materia+Classificazione

Script ottimizzato per eseguire ricerche sistematiche su **tutte le combinazioni Materia+Classificazione** del sito MEF (def.finanze.it).

## 🎯 Problema Risolto

Il sito MEF permette di filtrare le sentenze per:
- **Materia** (es. "Accertamento imposte", "IVA", "IRES", ecc.)
- **Classificazione** (es. "Attività istruttoria", "Ambito di applicazione", ecc.)

Esistono **1016 combinazioni** possibili Materia+Classificazione, e vogliamo raccogliere tutte le sentenze per ciascuna.

### ⚡ Ottimizzazione Implementata

Lo script esegue la ricerca in **DUE FASI** per evitare ricerche inutili:

1. **FASE 1** (`massime=false`): Testa tutte le 1016 combinazioni
   - Tiene traccia delle combinazioni che danno **0 risultati**

2. **FASE 2** (`massime=true`): Ripete SOLO per le combinazioni che hanno dato almeno 1 risultato
   - **Salta** le combinazioni con 0 risultati (perché daranno ancora 0 risultati)

**Risparmio**: Se il 30% delle combinazioni dà 0 risultati, risparmiamo ~300 ricerche inutili!

## 📋 Struttura Combinazioni

Il file `pattern/mef/mef_by_classificazioni.json` contiene:

```json
{
  "classificazioni": [
    {
      "codiceClassificazione": "0010",
      "descrizioneVC": "Documenti non classificati",
      "materie": [
        {
          "codice": "Z270",
          "descrizione": "NC Accertamento imposte"
        },
        {
          "codice": "Z310",
          "descrizione": "NC Accise armonizzate - Alcole"
        },
        ...
      ]
    },
    ...
  ]
}
```

Ogni combinazione è: `Materia (codice) + Classificazione (codice)`

## 🚀 Utilizzo

### Esecuzione Base

```bash
python3 scraper/scripts/mef_scrape_by_combinations.py \
  --anno 2022 \
  --ente "Corte di Cassazione"
```

### Parametri Disponibili

```bash
--combinations FILE      # File JSON combinazioni (default: pattern/mef/mef_by_classificazioni.json)
--anno YYYY              # Anno da cercare (OBBLIGATORIO)
--ente "NOME"            # Autorità emanante (default: "Corte di Cassazione")
--output DIR             # Directory output (default: scraper/data/mef_combinations)
--max-pages N            # Limita a N pagine per ricerca (default: illimitato)
--no-headless            # Mostra browser durante esecuzione
```

### Esempi

**1. Ricerca completa anno 2022**
```bash
python3 scraper/scripts/mef_scrape_by_combinations.py --anno 2022
```

**2. Ricerca con limite pagine (per test veloce)**
```bash
python3 scraper/scripts/mef_scrape_by_combinations.py \
  --anno 2022 \
  --max-pages 1
```

**3. Ricerca per altro ente**
```bash
python3 scraper/scripts/mef_scrape_by_combinations.py \
  --anno 2022 \
  --ente "Commissione Tributaria Centrale"
```

**4. Debug con browser visibile**
```bash
python3 scraper/scripts/mef_scrape_by_combinations.py \
  --anno 2022 \
  --no-headless
```

## 📊 Output Generati

Lo script genera 2 file principali nella directory `scraper/data/mef_combinations/`:

### 1. `zero_results_{anno}_{timestamp}.json`

Contiene le combinazioni che hanno dato 0 risultati nella FASE 1:

```json
[
  {
    "materia_code": "Z270",
    "materia_desc": "NC Accertamento imposte",
    "classificazione_code": "0010",
    "classificazione_desc": "Documenti non classificati"
  },
  ...
]
```

**Utilità**: Queste combinazioni vengono **saltate** nella FASE 2.

### 2. `results_{anno}_{timestamp}.json`

Contiene tutti i risultati delle due fasi:

```json
{
  "timestamp": "20241125_120000",
  "anno": "2022",
  "ente": "Corte di Cassazione",
  "total_combinations": 1016,
  "phases": [
    {
      "phase": 1,
      "massime": false,
      "duration_seconds": 3600,
      "total_tested": 1016,
      "zero_results_count": 305,
      "results": [
        {
          "combination": {
            "materia_code": "Z270",
            "materia_desc": "NC Accertamento imposte",
            "classificazione_code": "0010",
            "classificazione_desc": "Documenti non classificati"
          },
          "num_risultati": 0,
          "sentenze": [],
          "metadata": {}
        },
        {
          "combination": {...},
          "num_risultati": 15,
          "sentenze": [
            {
              "id": "{GUID}",
              "url": "https://def.finanze.it/...",
              "estremi": "Sentenza del 30/12/2022 n. 38131...",
              "titoli": ["Accertamento - IVA - ..."]
            },
            ...
          ],
          "metadata": {
            "contatore_giurisprudenza": "15",
            "ultima_pagina": "1",
            ...
          }
        },
        ...
      ]
    },
    {
      "phase": 2,
      "massime": true,
      "duration_seconds": 2100,
      "total_tested": 711,
      "skipped_zero_results": 305,
      "results": [...]
    }
  ]
}
```

## 📈 Statistiche e Progresso

Durante l'esecuzione, lo script mostra:

```
🚀 MEF SCRAPER - Ricerca per Combinazioni Materia+Classificazione
================================================================================
📁 Output: /home/user/scraper/data/mef_combinations
📅 Anno: 2022
🏛️  Ente: Corte di Cassazione
🕐 Timestamp: 20241125_120000

📋 Caricamento combinazioni...
✓ Caricate 1016 combinazioni

================================================================================
🔍 FASE 1: Ricerca con massime=false
================================================================================

[1/1016] Materia: NC Accertamento imposte
          Classificazione: Documenti non classificati
          ⊘ 0 risultati (verrà saltata in fase 2)

[2/1016] Materia: NC Accise armonizzate - Alcole
          Classificazione: Documenti non classificati
          ✓ 15 risultati trovati

...

💾 Salvataggio intermedio (processate 50/1016)...

...

✅ FASE 1 completata in 60.5 minuti
📊 Combinazioni con 0 risultati: 305/1016
📊 Combinazioni con risultati: 711
💾 File zero results: scraper/data/mef_combinations/zero_results_2022_20241125_120000.json

================================================================================
🔍 FASE 2: Ricerca con massime=true (solo combinazioni con risultati)
================================================================================
📋 Combinazioni da testare in fase 2: 711

[1/711] Materia: NC Accise armonizzate - Alcole
        Classificazione: Documenti non classificati
        ✓ 8 risultati (massimate) trovati

...

✅ FASE 2 completata in 35.2 minuti
📊 Combinazioni testate: 711

================================================================================
💾 Salvataggio risultati finali...
✓ File risultati: scraper/data/mef_combinations/results_2022_20241125_120000.json

================================================================================
📊 STATISTICHE FINALI
================================================================================
⏱️  Tempo totale: 95.7 minuti
📋 Combinazioni totali: 1016
⊘  Combinazioni con 0 risultati (saltate in fase 2): 305
✓  Combinazioni con risultati: 711
⚡ Ricerche risparmiate: 305 (30.0%)

📄 Sentenze trovate fase 1 (massime=false): 8542
📄 Sentenze trovate fase 2 (massime=true): 3215
```

## ⚙️ Come Funziona

### 1. Caricamento Combinazioni

Lo script legge `pattern/mef/mef_by_classificazioni.json` e crea una lista di tutte le 1016 combinazioni.

### 2. FASE 1: Ricerca Base

Per ogni combinazione:
1. Apre il form di ricerca avanzata MEF
2. Compila i filtri:
   - Data: 01/01/{anno} - 31/12/{anno}
   - Ente: "Corte di Cassazione"
   - **Materia**: seleziona il codice (es. "Z270")
   - **Classificazione**: seleziona il codice (es. "0010")
   - **Massime**: NO (checkbox deselezionata)
3. Invia la ricerca
4. Estrae risultati da tutte le pagine (click su "Avanti")
5. Se 0 risultati → aggiunge a lista `zero_results`

### 3. Salvataggio Intermedio

Ogni 50 combinazioni, salva il file `zero_results.json` per non perdere progresso.

### 4. FASE 2: Solo Massimate

Per ogni combinazione che HA DATO RISULTATI in fase 1:
1. Ripete la ricerca con **Massime: SÌ** (checkbox selezionata)
2. Estrae risultati massimati

**Combinazioni con 0 risultati vengono SALTATE** → risparmio tempo!

### 5. Output Finale

Salva `results.json` con:
- Tutte le combinazioni testate
- Numero risultati per ciascuna
- Sentenze trovate (ID, URL, estremi, titoli)
- Metadata (totale pagine, ecc.)
- Statistiche per fase

## 🔧 Gestione Interruzioni

Se lo script viene interrotto (Ctrl+C o errore):
- I file intermedi vengono salvati
- È possibile riprendere manualmente modificando lo script per:
  1. Caricare `zero_results.json` esistente
  2. Filtrare combinazioni già elaborate

## 📝 Note Importanti

### Tempi di Esecuzione

Con 1016 combinazioni e ~2 secondi per ricerca:
- **FASE 1**: ~34 minuti (1016 ricerche)
- **FASE 2**: ~24 minuti (se 30% sono zero → 711 ricerche)
- **TOTALE**: ~58 minuti

Tempi reali dipendono da:
- Velocità sito MEF
- Numero pagine per combinazione
- Latenza rete

### Limite Rate

Il sito MEF potrebbe limitare richieste troppo frequenti. Lo script include:
- Pausa di 1 secondo tra ricerche
- Pausa di 2 secondi tra pagine
- User-Agent realistico

### Paginazione

Per ogni combinazione con risultati, lo script:
1. Estrae XML dalla prima pagina
2. Controlla se ci sono altre pagine (`ultima_pagina`)
3. Clicca su link "Avanti" (classe CSS `.avanti`)
4. Ripete fino all'ultima pagina

## 🔗 Integrazione con Step Successivi

L'output di questo script può essere usato per:

1. **Step 2**: Download dettagli completi
   ```bash
   # Per ogni sentenza trovata, scaricare testo completo + massime
   python3 scraper/scripts/mef_2_download_dettagli.py ...
   ```

2. **Step 3**: Estrazione entities
   ```bash
   python3 scraper/scripts/mef_3_extract_entities.py ...
   ```

## 🎯 Vantaggi dell'Approccio

| Aspetto | Senza Ottimizzazione | Con Ottimizzazione |
|---------|---------------------|-------------------|
| **Ricerche totali** | 1016 + 1016 = 2032 | 1016 + 711 = 1727 |
| **Tempo risparmiato** | - | ~15% (305 ricerche) |
| **Efficienza** | Molte ricerche inutili | Solo ricerche utili |

## 🐛 Troubleshooting

### Errore "Elemento non trovato"

Se Selenium non trova elementi del form:
1. Controlla che il sito non abbia cambiato struttura
2. Aumenta i timeout (modifica `WebDriverWait`)
3. Usa `--no-headless` per debug visivo

### Nessun risultato trovato

Possibili cause:
- Combinazione effettivamente senza sentenze per quell'anno
- Errore nella selezione materia/classificazione
- Codici non validi nel JSON

### Script lento

Per velocizzare:
- Usa `--max-pages 1` per test
- Riduci pause (modifica `time.sleep()`)
- Esegui su server con buona connessione

## 📚 Riferimenti

- Script base: `mef_1_scrape_sentenze.py`
- Combinazioni: `pattern/mef/mef_by_classificazioni.json`
- Workflow: `.github/workflows/scrape-mef-sentenze.yml`
- Documentazione: `README_MEF_SYSTEM.md`
