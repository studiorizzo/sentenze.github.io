# Scraper Sentenze CIVILE - QUINTA SEZIONE

Script per scaricare automaticamente le sentenze della Cassazione con filtro **CIVILE** e **QUINTA SEZIONE** dal sito italgiure.giustizia.it.

## Funzionamento

Lo script utilizza Selenium per automatizzare la navigazione sul sito della Cassazione, applicare i filtri necessari e salvare l'HTML di ogni pagina dei risultati.

## Requisiti

### Localmente

Per eseguire lo script localmente, è necessario:

1. Python 3.11 o superiore
2. Google Chrome installato
3. Dipendenze Python:
   ```bash
   pip install selenium
   ```

### GitHub Actions

L'automazione via GitHub Actions è già configurata e non richiede installazioni locali.

## Uso

### Esecuzione locale

```bash
# Scarica tutte le pagine (dalla 1 all'ultima disponibile)
python3 scripts/scrape_sentenze_civili_quinta.py

# Scarica un intervallo specifico di pagine
python3 scripts/scrape_sentenze_civili_quinta.py --start 1 --end 100

# Specifica una directory di output diversa
python3 scripts/scrape_sentenze_civili_quinta.py --output mia_directory

# Mostra il browser durante l'esecuzione (utile per debug)
python3 scripts/scrape_sentenze_civili_quinta.py --no-headless
```

### Parametri disponibili

- `--start N`: Pagina iniziale (default: 1)
- `--end N`: Pagina finale (default: tutte le pagine disponibili)
- `--output DIR`: Directory dove salvare i file HTML (default: data/html)
- `--no-headless`: Mostra il browser durante l'esecuzione (default: modalità headless)

### GitHub Actions

Lo script può essere eseguito automaticamente via GitHub Actions in due modi:

#### 1. Esecuzione manuale

1. Vai su **Actions** nel repository GitHub
2. Seleziona il workflow "Scrape Sentenze CIVILE - QUINTA SEZIONE"
3. Clicca su "Run workflow"
4. Specifica opzionalmente:
   - **Pagina iniziale**: numero della pagina da cui iniziare (default: 1)
   - **Pagina finale**: numero della pagina finale (lascia vuoto per scaricare tutte)
5. Clicca su "Run workflow"

#### 2. Esecuzione automatica schedulata

Il workflow è configurato per eseguirsi automaticamente:
- **Frequenza**: ogni giorno alle 2:00 AM UTC (3:00 AM CET)
- **Comportamento**: scarica le prime 10 pagine per verificare nuove sentenze

Per modificare la schedulazione, edita il file `.github/workflows/scrape-sentenze-civili.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # Modifica qui
```

Esempi di cron:
- `'0 */6 * * *'` - ogni 6 ore
- `'0 0 * * 1'` - ogni lunedì a mezzanotte
- `'0 2 1 * *'` - il primo giorno di ogni mese alle 2:00 AM

## Output

I file HTML vengono salvati nella directory `data/html/` con il formato:
```
pagina X di YYYY.html
```

Dove:
- `X` è il numero della pagina
- `YYYY` è il totale delle pagine disponibili al momento dello scraping

## Struttura dei file salvati

Ogni file HTML contiene:
- La lista di 10 sentenze della pagina
- I metadati delle sentenze (numero, data, presidente, relatore, ecc.)
- I link ai PDF delle sentenze complete
- I link al testo OCR delle sentenze

## Note tecniche

### Gestione della paginazione

Il sito usa JavaScript per la navigazione tra le pagine. Lo script:
1. Carica la pagina iniziale
2. Applica i filtri CIVILE e QUINTA SEZIONE
3. Naviga tra le pagine usando i link con `data-arg`
4. Per pagine oltre la 10, usa il pulsante ">" (pagina successiva)

### Rate limiting

Lo script include pause di 1-2 secondi tra le richieste per non sovraccaricare il server del sito.

### Robustezza

Lo script gestisce:
- Timeout nel caricamento delle pagine
- Elementi non trovati
- Interruzione manuale (Ctrl+C)

## Troubleshooting

### Errore: "chromedriver not found"

Se esegui localmente, assicurati che Chrome sia installato:
- **Ubuntu/Debian**: `sudo apt-get install google-chrome-stable`
- **macOS**: Installa Chrome dal sito ufficiale
- **Windows**: Installa Chrome dal sito ufficiale

### Errore: Timeout durante il caricamento

Il sito potrebbe essere lento o non disponibile. Prova:
1. Aumentare il timeout nel codice (modificare `WebDriverWait(driver, 20)`)
2. Verificare che il sito sia accessibile: https://www.italgiure.giustizia.it/sncass/
3. Riavviare lo script

### Le pagine salvate non contengono dati

Verifica che i filtri siano applicati correttamente. Puoi eseguire lo script con `--no-headless` per vedere cosa sta succedendo nel browser.

## Esempio completo

```bash
# Scarica le pagine da 1 a 50 mostrando il browser
python3 scripts/scrape_sentenze_civili_quinta.py \
  --start 1 \
  --end 50 \
  --no-headless

# Output atteso:
# Avvio scraping sentenze CIVILE - QUINTA SEZIONE
# Directory output: /path/to/data/html
# Caricamento pagina iniziale: https://www.italgiure.giustizia.it/sncass/
# Applicazione filtro CIVILE...
# Applicazione filtro QUINTA SEZIONE...
# Numero totale di pagine: 5592
# Scarico pagine da 1 a 50
#
# Pagina 1/5592
# ✓ Salvata: pagina 1 di 5592.html
#
# Pagina 2/5592
# ✓ Salvata: pagina 2 di 5592.html
# ...
```

## Contribuire

Per migliorare lo script:
1. Testa le modifiche localmente
2. Assicurati che i file vengano salvati correttamente
3. Verifica che la GitHub Action funzioni
4. Crea una pull request con una descrizione delle modifiche
