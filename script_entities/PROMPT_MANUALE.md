# Prompt per Estrazione Manuale su Claude.ai

Se non puoi usare lo script automatico, puoi estrarre le entità manualmente usando Claude.ai.

---

## 🎯 Come Usare Questo Prompt

1. Vai su: https://claude.ai
2. Apri il file TXT della sentenza da analizzare (es: `txt/snciv2025530039O.txt`)
3. Copia il prompt qui sotto
4. Incollalo nella chat di Claude.ai
5. Aggiungi sotto il testo completo della sentenza
6. Invia
7. Claude ti risponderà con un JSON strutturato
8. Copia il JSON e salvalo in `entities/NOME_SENTENZA_entities.json`

---

## 📋 PROMPT DA COPIARE

```
Sei un esperto di analisi di sentenze della Corte di Cassazione italiana.

Analizza il seguente testo di una sentenza ed estrai TUTTE le entità rilevanti.

CATEGORIE RICHIESTE:
1. **Presidente**: Nome del Presidente della sezione
2. **Relatore**: Nome del Giudice relatore
3. **Ricorrente** (RCR): Parte che ha presentato ricorso
4. **Controricorrente** (CTR): Parte controricorrente
5. **Avvocati** (AVV): Tutti gli avvocati menzionati (con indicazione di quale parte rappresentano)
6. **Riferimenti Ricorso** (RIC): Numeri di ricorso, RG, etc.
7. **Norme Citate**: Articoli di legge citati (con nome della legge)
8. **Precedenti**: Sentenze precedenti citate (numero e anno)
9. **Tribunali** (TRI): Tribunali/Corti menzionati nel procedimento

FORMATO OUTPUT (JSON valido):
{
  "presidente": "COGNOME NOME",
  "relatore": "COGNOME NOME",
  "ricorrenti": ["NOME1", "NOME2"],
  "controricorrenti": ["NOME1", "NOME2"],
  "avvocati": [
    {"nome": "NOME COGNOME", "parte": "ricorrente/controricorrente"}
  ],
  "riferimenti_ricorso": ["n. 12952/2018", "RG n. ..."],
  "norme_citate": [
    {"articolo": "art. 360 c.p.c.", "comma": "1, n. 3", "legge": "codice di procedura civile"}
  ],
  "precedenti_citati": [
    {"numero": "12345", "anno": "2020", "sezione": "lavoro"}
  ],
  "tribunali": ["Tribunale di Roma", "Corte d'Appello di ..."]
}

REGOLE IMPORTANTI:
- Se un'informazione NON è presente nel testo, usa null o []
- Per nomi di persone: usa formato "COGNOME NOME" in MAIUSCOLO
- Per norme: separa articolo, comma e legge
- Per precedenti: estrai numero, anno e sezione (se presente)
- Ignora abbreviazioni ambigue (es. "Cass." senza numero/anno)
- Estrai SOLO informazioni esplicitamente presenti nel testo

Rispondi SOLO con il JSON, senza altre spiegazioni o commenti.

---

TESTO SENTENZA:
[INCOLLA QUI IL TESTO COMPLETO DELLA SENTENZA]
```

---

## 📝 Esempio Pratico

### Input:

```
[Copi tutto il prompt sopra e poi sotto scrivi:]

SENTENZA N. 5304/2025
REPUBBLICA ITALIANA
IN NOME DEL POPOLO ITALIANO
LA CORTE SUPREMA DI CASSAZIONE
SEZIONE PRIMA CIVILE

Composta dagli Ill.mi Sigg.ri Magistrati:
Dott. MARIO ROSSI - Presidente
Dott. LUCA BIANCHI - Consigliere, Relatore
...

Ha pronunciato la seguente:
SENTENZA

sul ricorso 12345/2023 proposto da:
ALFA SRL, in persona del legale rappresentante pro tempore,
rappresentata e difesa dall'avvocato GIUSEPPE VERDI
- ricorrente -

contro

BETA SPA, in persona del legale rappresentante pro tempore,
rappresentata e difesa dall'avvocato ANNA NERI
- controricorrente -

[... resto del testo della sentenza ...]
```

### Output di Claude:

```json
{
  "presidente": "ROSSI MARIO",
  "relatore": "BIANCHI LUCA",
  "ricorrenti": ["ALFA SRL"],
  "controricorrenti": ["BETA SPA"],
  "avvocati": [
    {"nome": "VERDI GIUSEPPE", "parte": "ricorrente"},
    {"nome": "NERI ANNA", "parte": "controricorrente"}
  ],
  "riferimenti_ricorso": ["n. 12345/2023"],
  "norme_citate": [],
  "precedenti_citati": [],
  "tribunali": []
}
```

Copi questo JSON e lo salvi in: `entities/snciv2025530039O_entities.json`

---

## ⚙️ Automazione con Claude.ai

Se hai molte sentenze da processare:

1. **Usa Projects su Claude.ai:**
   - Crea un nuovo Project
   - Aggiungi questo prompt come "Custom Instructions"
   - Carica i file TXT delle sentenze come documenti del progetto
   - Claude ricorderà le istruzioni per tutte le conversazioni

2. **Processamento batch:**
   - Apri una nuova conversazione nel Project
   - Scrivi: "Analizza il file snciv2025530039O.txt"
   - Claude estrarrà automaticamente le entità
   - Ripeti per ogni sentenza

---

## 🔍 Controllo Qualità

Dopo aver estratto le entità, verifica:

✅ **Presidente e Relatore:** Controlla che siano corretti guardando l'intestazione della sentenza
✅ **Ricorrenti:** Verifica che siano le parti che hanno fatto ricorso
✅ **Formato nomi:** Devono essere "COGNOME NOME" in maiuscolo
✅ **JSON valido:** Copia il JSON su https://jsonlint.com/ per verificare che sia valido
✅ **Campi vuoti:** Se un campo è vuoto, deve essere `[]` o `null`, NON stringa vuota `""`

---

## ⏱️ Tempo Stimato

Per una sentenza media (10-20 pagine):
- Claude.ai: ~1-2 minuti
- Include: copia prompt + testo, attesa risposta, salvataggio JSON

Per 50 sentenze:
- Tempo totale: ~2-3 ore
- Consiglio: Fai 10-15 sentenze per sessione per evitare errori da stanchezza

---

## 💡 Consigli

1. **Salva il prompt:** Tienilo in un file di testo a parte per copiarlo velocemente
2. **Usa editor JSON:** Per salvare i file usa un editor di testo (Notepad++, VS Code, Sublime)
3. **Nomi file:** Usa lo stesso nome del file TXT ma con `_entities.json` alla fine
4. **Backup:** Fai una copia dei JSON estratti in una cartella separata
5. **Log errori:** Se Claude non riesce a estrarre qualcosa, segna quale sentenza per ricontrollarla

---

## ❓ Domande Frequenti

**Q: Claude può sbagliare?**
A: Raramente, ma può succedere. Controlla sempre presidente/relatore nell'intestazione.

**Q: Cosa faccio se Claude non trova un'entità?**
A: Se nel testo non c'è, è corretto che Claude la lasci vuota. Se c'è ma Claude non la trova, ripeti la richiesta specificando cosa cercare.

**Q: Posso usare ChatGPT invece di Claude?**
A: Sì, il prompt funziona anche con ChatGPT o altri LLM. Claude tende ad essere più preciso per documenti legali italiani.

**Q: Quanto costa?**
A: Claude.ai ha un piano gratuito generoso. Per 50-100 sentenze non avrai problemi.

---

**Ultima modifica:** 2025-11-21
