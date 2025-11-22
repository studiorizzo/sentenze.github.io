# Strategia di Categorizzazione Sentenze - LLM Guidato

## 🎯 Obiettivo

Categorizzare automaticamente le sentenze della Cassazione usando **Gemini API** con **tassonomie validate** (MEF, Giustizia Tributaria, Cassazione).

---

## 📊 Dati Disponibili

### Pattern Estratti

| Fonte | File | Termini | Descrizione |
|-------|------|---------|-------------|
| **MEF** | `mef/mef.json` | 561 | Materie + classificazioni fiscali |
| **MEF** | `mef/mef_autosuggest.json` | 4.672 | Termini autosuggest sito MEF |
| **Giustizia Tributaria** | `giustizia_trib/giustizia_tributaria.json` | 41 | Materie tribunali tributari |
| **Cassazione** | `cassazione/2_cassazione.txt` | 24.667 | Keywords autocomplete (TUTTI i domini) |

### Liste Filtrate (pronte all'uso)

| Lista | File | Termini | Uso |
|-------|------|---------|-----|
| ✅ **WHITELIST** | `whitelist_tributario_completa.txt` | **6.823** | Categorizzazione primaria (tributario certo) |
| ❌ **BLACKLIST** | `cassazione/blacklist_penale_civile.txt` | 1.320 | Esclusione (penale/civile certo) |
| ❓ **GRAYLIST** | `cassazione/graylist_ambigui.txt` | 21.410 | Context-dependent (pesare con LLM) |

---

## 🚀 Strategia Implementativa

### Approccio a 3 Livelli

```
┌─────────────────────────────────────────────────────────────┐
│                 SENTENZA TXT                                │
│         (es: snciv2025530039O.txt)                         │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│  LIVELLO 1: WHITELIST MATCHING                             │
│  → Cerca termini presenti in whitelist_tributario_completa │
│  → Match: materie principali (es: "IVA", "IRPEF", "studi   │
│    settore")                                                │
│  → Output: Lista materie tributarie CERTE                  │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│  LIVELLO 2: BLACKLIST FILTERING                            │
│  → Verifica presenza termini penale/civile                 │
│  → Se match: FLAG sentenza come "non tributaria"           │
│  → Output: Boolean (is_tributaria: true/false)             │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│  LIVELLO 3: GEMINI LLM ENRICHMENT                          │
│  → Prompt con whitelist + graylist (top 500 frequenti)     │
│  → LLM analizza CONTESTO e pesa termini ambigui            │
│  → Output: JSON strutturato con categorizzazione finale    │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
         OUTPUT JSON
```

---

## 📋 Prompt Template per Gemini

### Prompt Strutturato (Raccomandato)

```
Analizza questa sentenza della Cassazione e classificala ESCLUSIVAMENTE usando i termini delle liste fornite.

**SENTENZA:**
[testo sentenza completo]

**TASSONOMIE DISPONIBILI:**

1. MATERIE TRIBUTARIE (scegli max 3):
[lista materie da MEF + Giustizia Trib - primi 100]

2. CLASSIFICAZIONI DETTAGLIATE (scegli max 5):
[lista classificazioni da MEF - primi 200]

3. KEYWORDS CASSAZIONE (scegli max 10 presenti nel testo):
[lista da whitelist_tributario_completa - primi 500 più frequenti]

**ISTRUZIONI:**
- Identifica le materie principali effettivamente trattate nella sentenza
- NON inventare termini, usa SOLO quelli nelle liste
- Se un termine è presente nella sentenza ma non nelle liste, ignoralo
- Priorità: specifico > generico (es: "accertamento analitico" > "accertamento")
- Estrai anche i riferimenti normativi citati (articoli, leggi, DPR)

**OUTPUT JSON (RISPETTA ESATTAMENTE QUESTO FORMATO):**
```json
{
  "materie_mef": ["Irpef", "Iva"],
  "classificazioni_mef": ["Accertamento d'ufficio", "Studi di settore"],
  "keywords_cassazione": ["studi settore", "accertamento", "motivazione"],
  "riferimenti_normativi": [
    {"articolo": "art. 360", "comma": "1, n. 3", "legge": "c.p.c."},
    {"articolo": "art. 62-sexies", "legge": "d.l. 331/1993"}
  ],
  "is_tributaria": true,
  "note": "Sentenza su accertamento IVA tramite studi di settore"
}
```

IMPORTANTE: Rispondi SOLO con il JSON, senza testo aggiuntivo.
```

---

## 🔧 Implementazione Python

### Script di Categorizzazione

```python
#!/usr/bin/env python3
"""Categorizzazione sentenze con Gemini API"""
import os
import json
import requests
from pathlib import Path

# Carica whitelist
def load_whitelist():
    whitelist_file = Path('pattern/whitelist_tributario_completa.txt')
    with open(whitelist_file) as f:
        return [line.strip() for line in f if line.strip()]

# Carica materie MEF
def load_mef_materie():
    mef_file = Path('pattern/mef/mef.json')
    with open(mef_file) as f:
        data = json.load(f)
        materie = []
        for m in data['materie']:
            materie.append(m['descrizione'])
            materie.extend([c['descrizioneVC'] for c in m.get('classificazioni', [])])
        return materie

# Gemini API call
def categorize_with_gemini(txt_content, api_key):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"

    # Carica tassonomie
    whitelist = load_whitelist()[:500]  # Top 500 più frequenti
    materie = load_mef_materie()[:100]

    # Costruisci prompt
    prompt = f"""
Analizza questa sentenza e classificala usando SOLO i termini delle liste.

SENTENZA:
{txt_content}

MATERIE (max 3): {', '.join(materie[:100])}

KEYWORDS (max 10): {', '.join(whitelist[:500])}

OUTPUT JSON:
{{
  "materie_mef": [],
  "keywords_cassazione": [],
  "riferimenti_normativi": [],
  "is_tributaria": true
}}

Rispondi SOLO con JSON.
"""

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.ok:
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        # Parse JSON dalla risposta
        return json.loads(text)
    else:
        raise Exception(f"Gemini API error: {response.status_code}")

# Main
def main():
    api_key = os.getenv('GOOGLE_API_KEY')
    txt_file = Path('txt/snciv2025530039O.txt')

    with open(txt_file) as f:
        txt_content = f.read()

    categorization = categorize_with_gemini(txt_content, api_key)

    print(json.dumps(categorization, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
```

---

## 📊 Vantaggi dell'Approccio

### ✅ PRO:

1. **Categorizzazione supervisionata** → termini validati (MEF, Cassazione)
2. **Consistenza** → output comparabile tra sentenze
3. **Scalabile** → 1000 sentenze/giorno con Gemini free tier
4. **Multilivello** → whitelist (certo) + graylist (contesto)
5. **Correlazione** → sentenze con keywords comuni facilmente linkabili

### ⚠️ ATTENZIONI:

1. **Token limit Gemini** → sentenze lunghe potrebbero eccedere
   - Soluzione: chunking (invia solo sezioni rilevanti)

2. **Prompt troppo lungo** → 500 keywords nel prompt = tanti token
   - Soluzione: limitare a top 200-300 più frequenti

3. **JSON parsing** → LLM può sbagliare formato
   - Soluzione: retry con prompt più strict se parsing fallisce

---

## 🎯 Prossimi Passi

1. ✅ **Pattern estratti** (completato)
2. ✅ **Liste filtrate** (completato)
3. ⏳ **Test su sentenza esempio** (da fare)
4. ⏳ **Integrazione in auto_process_all.py** (da fare)
5. ⏳ **Batch processing 500 sentenze** (da fare)

---

**Ultimo aggiornamento:** 2025-11-22
**Status:** Strategia definita, pronta per implementazione
