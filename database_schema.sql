-- Schema Database Sentenze della Cassazione
-- Compatibile con SQLite e PostgreSQL

-- Tabella principale delle sentenze
CREATE TABLE IF NOT EXISTS sentenze (
    -- Identificatori
    id TEXT PRIMARY KEY,                    -- ID univoco (es: snciv2025530039O)
    numero INTEGER NOT NULL,                 -- Numero sentenza
    anno INTEGER NOT NULL,                   -- Anno
    ecli TEXT UNIQUE,                        -- European Case Law Identifier

    -- Classificazione
    archivio TEXT NOT NULL,                  -- CIVILE o PENALE
    sezione TEXT NOT NULL,                   -- PRIMA, SECONDA, TERZA, QUINTA, SESTA, LAVORO, UNITE
    tipo_provvedimento TEXT NOT NULL,        -- Ordinanza, Sentenza, Decreto, Ordinanza Interlocutoria

    -- Date
    data_deposito DATE NOT NULL,             -- Data pubblicazione/deposito
    data_udienza DATE,                       -- Data udienza/decisione

    -- Soggetti
    presidente TEXT,                         -- Nome presidente
    relatore TEXT NOT NULL,                  -- Nome relatore

    -- PDF
    pdf_url TEXT NOT NULL,                   -- URL completo del PDF
    pdf_filename TEXT,                       -- Nome file PDF
    pdf_local_path TEXT,                     -- Path locale se scaricato
    pdf_size_bytes INTEGER,                  -- Dimensione PDF in bytes
    pdf_num_pages INTEGER,                   -- Numero pagine PDF

    -- Testo
    testo_completo TEXT,                     -- Testo completo estratto dal PDF
    testo_markdown TEXT,                     -- Testo in formato Markdown per AI
    testo_length INTEGER,                    -- Lunghezza testo in caratteri

    -- Metadata tecnici
    html_source_file TEXT,                   -- File HTML di origine
    data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_aggiornamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    elaborazione_completata BOOLEAN DEFAULT FALSE,

    -- Indici per ricerche veloci
    CHECK (archivio IN ('CIVILE', 'PENALE')),
    CHECK (anno >= 1900 AND anno <= 2100)
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_sentenze_anno ON sentenze(anno);
CREATE INDEX IF NOT EXISTS idx_sentenze_numero_anno ON sentenze(numero, anno);
CREATE INDEX IF NOT EXISTS idx_sentenze_sezione ON sentenze(sezione);
CREATE INDEX IF NOT EXISTS idx_sentenze_archivio ON sentenze(archivio);
CREATE INDEX IF NOT EXISTS idx_sentenze_data_deposito ON sentenze(data_deposito);
CREATE INDEX IF NOT EXISTS idx_sentenze_ecli ON sentenze(ecli);

-- Full-text search (solo PostgreSQL)
-- Per SQLite si usa FTS5, syntax diversa
-- CREATE INDEX IF NOT EXISTS idx_sentenze_testo_fts ON sentenze USING GIN(to_tsvector('italian', testo_completo));

-- Tabella per estratti OCR parziali dall'HTML (opzionale)
CREATE TABLE IF NOT EXISTS ocr_estratti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sentenza_id TEXT NOT NULL,
    frammento TEXT NOT NULL,
    ordine INTEGER NOT NULL,
    FOREIGN KEY (sentenza_id) REFERENCES sentenze(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ocr_estratti_sentenza ON ocr_estratti(sentenza_id);

-- Tabella per tracking download e processing
CREATE TABLE IF NOT EXISTS processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sentenza_id TEXT NOT NULL,
    operazione TEXT NOT NULL,              -- 'download_pdf', 'extract_text', 'extract_markdown'
    stato TEXT NOT NULL,                   -- 'success', 'error', 'in_progress'
    messaggio TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sentenza_id) REFERENCES sentenze(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_processing_log_sentenza ON processing_log(sentenza_id);
CREATE INDEX IF NOT EXISTS idx_processing_log_stato ON processing_log(stato);

-- Tabella per metadati batch (pagine HTML elaborate)
CREATE TABLE IF NOT EXISTS batch_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    html_filename TEXT UNIQUE NOT NULL,
    pagina_numero INTEGER,                  -- Numero pagina (1-5563)
    totale_sentenze INTEGER,                -- Sentenze trovate in questa pagina
    sentenze_elaborate INTEGER DEFAULT 0,   -- Sentenze completamente elaborate
    data_elaborazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- View per statistiche rapide
CREATE VIEW IF NOT EXISTS sentenze_stats AS
SELECT
    anno,
    archivio,
    sezione,
    tipo_provvedimento,
    COUNT(*) as totale,
    SUM(CASE WHEN elaborazione_completata THEN 1 ELSE 0 END) as elaborate,
    AVG(pdf_num_pages) as media_pagine,
    AVG(testo_length) as media_caratteri
FROM sentenze
GROUP BY anno, archivio, sezione, tipo_provvedimento;

-- View per sentenze non ancora elaborate
CREATE VIEW IF NOT EXISTS sentenze_da_elaborare AS
SELECT
    id,
    numero,
    anno,
    archivio,
    sezione,
    pdf_url,
    pdf_local_path
FROM sentenze
WHERE elaborazione_completata = FALSE
ORDER BY anno DESC, numero DESC;
