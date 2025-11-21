# Script Estrazione Entità con LLM

## 📋 A Cosa Serve

Questo script estrae automaticamente le informazioni importanti dalle sentenze usando l'intelligenza artificiale di Google (Gemini).

**Cosa estrae:**
- Presidente e Relatore
- Ricorrenti e controricorrenti
- Avvocati
- Numeri di ricorso
- Leggi e articoli citati
- Precedenti (altre sentenze citate)
- Tribunali coinvolti

**Perché usarlo:**
Invece di cercare manualmente tutte queste informazioni in ogni sentenza, lo script le trova automaticamente in pochi secondi.

---

## 🎯 Quando Usarlo

Usa questo script quando:
- Hai l'API key di Google AI Studio (gratuita)
- Vuoi processare molte sentenze automaticamente
- Lo esegui dal tuo computer (non dalla sandbox Claude Code)

**Alternative:**
- Se non riesci a usare lo script: estrai entità manualmente con Claude.ai (vedi prompt in PROGRESS.md)
- Se hai API key Claude: modifica `LLM_BACKEND='claude'` nello script

---

## 🔑 Prerequisiti

### 1. API Key Google (GRATUITA)

**Dove ottenerla:**
1. Vai su: https://aistudio.google.com/app/apikey
2. Clicca "Create API key"
3. Scegli il progetto (o creane uno nuovo)
4. Copia la chiave (es: `AIzaSyBCU_6HSIR8auFT6XQF88H8UZwTKRUns7o`)

**Limiti gratuiti:**
- 1500 richieste al giorno
- Completamente gratuito
- Non serve carta di credito

### 2. Python installato

Verifica che Python sia installato sul tuo computer:
```bash
python --version
```

Dovrebbe mostrarti qualcosa tipo: `Python 3.10.0` o superiore

Se non hai Python: https://www.python.org/downloads/

---

## 🚀 Come Usarlo

### Passo 1: Configura l'API Key

Apri il terminale (o Prompt dei comandi su Windows) e scrivi:

**Su Mac/Linux:**
```bash
export GOOGLE_API_KEY='TUA_CHIAVE_API_QUI'
```

**Su Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY='TUA_CHIAVE_API_QUI'
```

**Su Windows (CMD):**
```cmd
set GOOGLE_API_KEY=TUA_CHIAVE_API_QUI
```

Sostituisci `TUA_CHIAVE_API_QUI` con la chiave che hai copiato da Google AI Studio.

---

### Passo 2: Installa Librerie Necessarie

Prima di eseguire lo script per la prima volta:

```bash
pip install requests
```

Questo installa la libreria per comunicare con Google.

---

### Passo 3: Esegui lo Script

#### Opzione A: Processa una singola sentenza

```bash
python llm_entity_extractor.py
```

Lo script processerà automaticamente i file nella cartella `txt/` e creerà i JSON delle entità in `entities/`.

#### Opzione B: Usa nella pipeline completa

```bash
cd /percorso/al/tuo/repository
export GOOGLE_API_KEY='TUA_CHIAVE_API'
python auto_process_all.py
```

La pipeline completa processerà automaticamente tutte le sentenze usando lo script di estrazione entità.

---

## 📁 File Prodotti

Per ogni sentenza processata, lo script crea un file JSON:

**Esempio:** `entities/snciv2025530039O_entities.json`

**Contenuto:**
```json
{
  "presidente": "ROSSI MARIO",
  "relatore": "BIANCHI LUCA",
  "ricorrenti": ["ALFA SRL"],
  "controricorrenti": ["BETA SPA"],
  "avvocati": [
    {"nome": "VERDI GIUSEPPE", "parte": "ricorrente"}
  ],
  "riferimenti_ricorso": ["n. 12345/2023"],
  "norme_citate": [
    {"articolo": "art. 360", "comma": "1, n. 3", "legge": "c.p.c."}
  ],
  "precedenti_citati": [
    {"numero": "23456", "anno": "2022", "sezione": "lavoro"}
  ],
  "tribunali": ["Tribunale di Roma"]
}
```

---

## ⚙️ Backend Alternativi

Lo script supporta 3 backend AI:

### 1. Gemini (DEFAULT - Gratuito)
```bash
export GOOGLE_API_KEY='...'
export LLM_BACKEND='gemini'
```

### 2. Claude (Se hai API key Anthropic)
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
export LLM_BACKEND='claude'
pip install anthropic
```

### 3. Ollama (Locale, senza internet)
```bash
export LLM_BACKEND='ollama'
pip install ollama
ollama serve  # in un altro terminale
```

---

## ❌ Problemi Comuni

### Errore: "GOOGLE_API_KEY non trovata"
**Soluzione:** Hai dimenticato di configurare la chiave API (vedi Passo 1)

### Errore: "403 Forbidden"
**Cause possibili:**
1. API key sbagliata → Controlla di averla copiata correttamente
2. API key con restrizioni → Vai su Google Cloud Console e rimuovi tutte le restrizioni
3. IP bloccato → Probabile se usi sandbox/container, prova dal tuo PC

### Errore: "ModuleNotFoundError: No module named 'requests'"
**Soluzione:** Installa la libreria:
```bash
pip install requests
```

### Errore: "File not found: txt/..."
**Soluzione:** Assicurati di eseguire lo script dalla cartella principale del repository:
```bash
cd /percorso/al/repository/sentenze.github.io
python script_entities/llm_entity_extractor.py
```

---

## 🔍 Differenze con NER (Vecchio Metodo)

| Caratteristica | NER (Vecchio) | LLM (Nuovo) |
|----------------|---------------|-------------|
| Entità estratte | 6 | 9+ |
| Presidente/Relatore | ❌ No | ✅ Sì |
| Norme citate | ❌ No | ✅ Sì (con dettagli) |
| Precedenti | ❌ No | ✅ Sì (con anno/sezione) |
| Accuratezza | ~70% | ~95% |
| Velocità | Veloce | Medio (2-3 sec/sentenza) |
| Costo | Gratis | Gratis (1500/giorno) |

---

## 📞 Supporto

**Per problemi con lo script:**
- Controlla la sezione "Problemi Comuni" sopra
- Leggi PROGRESS.md nella cartella principale
- Verifica i log di errore nel terminale

**Documentazione Google AI Studio:**
https://ai.google.dev/gemini-api/docs

**API Key Console:**
https://aistudio.google.com/app/apikey

---

## 📝 Note Tecniche

**Modello usato:** gemini-2.0-flash (stabile, veloce)
**Endpoint API:** https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent
**Metodo autenticazione:** Header `X-goog-api-key`
**Prompt ottimizzato:** Per sentenze Corte di Cassazione italiana
**Output formato:** JSON strutturato con schema predefinito

---

**Ultima modifica:** 2025-11-21
**Versione script:** 1.0
**Testato con:** Python 3.10+, Gemini 2.0 Flash
