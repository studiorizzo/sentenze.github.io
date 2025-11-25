# 🚀 Scraper Sentenze MEF - Super Efficiente

Scraper per estrarre sentenze da [def.finanze.it](https://def.finanze.it) (Ministero Economia e Finanze)

## 🎯 Perché è SUPER EFFICIENTE?

1. **Dati già strutturati**: Il sito embedding i risultati in XML dentro JavaScript
2. **Zero parsing HTML complesso**: Estraiamo direttamente l'XML
3. **Velocissimo**: Solo 2-3 secondi per pagina
4. **Bypass del 403**: Usa Selenium con headers realistici

## 📋 Struttura XML estratta

```xml
<risultatiRicerca>
  <contatori>
    <contatoreGiurisprudenza>139</contatoreGiurisprudenza>
  </contatori>
  <risultati>
    <pagina>1</pagina>
    <ultimaPagina>5</ultimaPagina>
    <totaleProvvedimenti>50</totaleProvvedimenti>
    <Provvedimento idProvvedimento="{GUID}">
      <estremi link="true">Sentenza del 30/12/2022 n. 38131...</estremi>
      <titoliProvvedimento>
        <titoloProvvedimento><![CDATA[...]]></titoloProvvedimento>
      </titoliProvvedimento>
    </Provvedimento>
    ...
  </risultati>
</risultatiRicerca>
```

## 🛠️ Installazione

```bash
# Requisiti (già presenti nel progetto)
pip install selenium lxml

# Assicurati di avere ChromeDriver installato
# Il progetto lo usa già per lo scraper Cassazione
```

## 📖 Utilizzo Base

### Esempio 1: Sentenze Cassazione 2022

```bash
python3 scraper/scripts/finanze_download_html.py \
  --ente "Corte di Cassazione" \
  --data-da "01/01/2022" \
  --data-a "31/12/2022"
```

**Output**: JSON con 139 sentenze strutturate

### Esempio 2: Solo sentenze massimate

```bash
python3 scraper/scripts/finanze_download_html.py \
  --ente "Corte di Cassazione" \
  --data-da "01/01/2023" \
  --data-a "31/12/2023" \
  --massimate
```

### Esempio 3: Ricerca per parole chiave

```bash
python3 scraper/scripts/finanze_download_html.py \
  --ente "Corte di Cassazione" \
  --parole "IVA" \
  --data-da "01/01/2024" \
  --data-a "31/12/2024"
```

### Esempio 4: Sentenza specifica

```bash
python3 scraper/scripts/finanze_download_html.py \
  --ente "Corte di Cassazione" \
  --numero "38131" \
  --anno "2022"
```

## 📊 Output

Il file JSON generato ha questa struttura:

```json
{
  "timestamp": "20241124_143022",
  "filters": {
    "ente": "Corte di Cassazione",
    "data_da": "01/01/2022",
    "data_a": "31/12/2022"
  },
  "metadata": {
    "contatore_giurisprudenza": "139",
    "pagina": "1",
    "ultima_pagina": "5",
    "totale_provvedimenti": "50"
  },
  "sentenze": [
    {
      "id": "{84B3CC19-CC89-46BE-B7FB-79EA80772CA2}",
      "url": "https://def.finanze.it/DocTribFrontend/getGiurisprudenzaDetail.do?id={84B3CC19-CC89-46BE-B7FB-79EA80772CA2}",
      "estremi": "Sentenza del 30/12/2022 n. 38131 - Corte di Cassazione - Sezione/Collegio 5",
      "titoli": [
        "Cartella di pagamento - Accise - Imposta di fabbricazione..."
      ]
    },
    ...
  ]
}
```

## 🎛️ Parametri disponibili

| Parametro | Descrizione | Esempio |
|-----------|-------------|---------|
| `--ente` | Autorità emanante | "Corte di Cassazione" |
| `--data-da` | Data emissione DA | "01/01/2022" |
| `--data-a` | Data emissione A | "31/12/2022" |
| `--anno` | Anno sentenza | "2022" |
| `--numero` | Numero sentenza | "38131" |
| `--parole` | Parole chiave | "IVA" |
| `--massimate` | Solo sentenze massimate | flag |
| `--output` | Directory output | "scraper/data/finanze" |
| `--no-headless` | Mostra browser (debug) | flag |

## 📚 Enti disponibili

- **Corte di Cassazione**
- Commissione Tributaria Centrale
- Commissione Tributaria Provinciale
- Commissione Tributaria Regionale

(Verifica i nomi esatti sul sito per altri enti)

## 🔧 Debug

Se lo scraper non funziona:

1. **Modalità visibile**: Usa `--no-headless` per vedere cosa succede
2. **Controlla HTML**: Lo script salva l'HTML in caso di errori
3. **Verifica ChromeDriver**: Deve essere compatibile con Chrome installato

```bash
# Test con browser visibile
python3 scraper/scripts/finanze_download_html.py \
  --ente "Corte di Cassazione" \
  --data-da "01/01/2022" \
  --data-a "31/01/2022" \
  --no-headless
```

## ⚡ Performance

- **Tempo per pagina**: ~2-3 secondi
- **Sentenze per pagina**: 50
- **Esempio 139 sentenze (3 pagine)**: ~10 secondi totali

Molto più veloce del parsing HTML tradizionale! 🚀

## 🔄 Integrazione con workflow esistente

Puoi integrare questo scraper nel tuo workflow esistente:

```python
# Import nel tuo script
from scraper.scripts.finanze_download_html import scrape_finanze

# Uso programmatico
filters = {
    'ente': 'Corte di Cassazione',
    'data_da': '01/01/2022',
    'data_a': '31/12/2022'
}

results = scrape_finanze(filters, output_dir="data/finanze", headless=True)
print(f"Raccolte {len(results['sentenze'])} sentenze")
```

## 💡 Tips

1. **Usa date range brevi**: Per evitare timeout su grandi dataset
2. **Parallelizza**: Puoi lanciare più scraper con range di date diversi
3. **Salva spesso**: Lo script salva automaticamente alla fine
4. **Rispetta il server**: Pause di 2s tra pagine (già implementate)

## 🐛 Troubleshooting

### Errore 403

Se ottieni ancora 403:
- Lo script usa headers realistici
- Selenium emula un browser vero
- Se persiste, il sito potrebbe aver rafforzato le protezioni

### Browser non si apre

```bash
# Verifica ChromeDriver
which chromedriver

# Reinstalla se necessario
```

### XML non estratto

Il sito potrebbe aver cambiato struttura. Controlla:
1. Variabile JavaScript `xmlResult` ancora presente
2. Formato XML cambiato

## 📝 TODO Future

- [ ] Parallelizzazione multi-processo
- [ ] Retry automatici su errori di rete
- [ ] Download PDF delle sentenze
- [ ] Export in formati multipli (CSV, Excel)
- [ ] Caching intelligente per evitare riscraping

## 🤝 Contributi

Questo script è parte del progetto `sentenze.github.io` per la raccolta e analisi di sentenze tributarie.
