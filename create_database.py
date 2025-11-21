#!/usr/bin/env python3
"""
Script per creare e popolare il database delle sentenze
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


class SentenzeDatabase:
    def __init__(self, db_path='sentenze.db'):
        """Inizializza il database"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Per accedere alle colonne per nome
        self.create_tables()

    def create_tables(self):
        """Crea le tabelle nel database"""
        schema_file = Path('database_schema.sql')

        if schema_file.exists():
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = f.read()
                # Esegui tutto lo schema
                self.conn.executescript(schema)
            print("✅ Tabelle create con successo")
        else:
            print("⚠️  File schema non trovato")

    def insert_sentenza(self, sentenza_data, testo_completo=None, testo_markdown=None):
        """Inserisce una sentenza nel database"""

        # Converti date dal formato DD/MM/YYYY a YYYY-MM-DD
        data_deposito = self._convert_date(sentenza_data.get('data_deposito'))
        data_udienza = self._convert_date(sentenza_data.get('data_udienza'))

        sql = """
        INSERT INTO sentenze (
            id, numero, anno, ecli,
            archivio, sezione, tipo_provvedimento,
            data_deposito, data_udienza,
            presidente, relatore,
            pdf_url, pdf_filename, pdf_local_path,
            testo_completo, testo_markdown, testo_length
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        testo_length = len(testo_completo) if testo_completo else None

        values = (
            sentenza_data.get('id'),
            sentenza_data.get('numero'),
            sentenza_data.get('anno'),
            sentenza_data.get('ecli'),
            sentenza_data.get('archivio'),
            sentenza_data.get('sezione'),
            sentenza_data.get('tipo_provvedimento'),
            data_deposito,
            data_udienza,
            sentenza_data.get('presidente'),
            sentenza_data.get('relatore'),
            sentenza_data.get('pdf_url'),
            sentenza_data.get('pdf_filename'),
            sentenza_data.get('pdf_local_path'),
            testo_completo,
            testo_markdown,
            testo_length
        )

        try:
            cursor = self.conn.execute(sql, values)
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"⚠️  Sentenza già presente: {sentenza_data.get('id')}")
            return None

    def _convert_date(self, date_str):
        """Converte data da DD/MM/YYYY a YYYY-MM-DD"""
        if not date_str:
            return None
        try:
            # Formato italiano: 13/11/2025
            parts = date_str.split('/')
            if len(parts) == 3:
                return f"{parts[2]}-{parts[1]}-{parts[0]}"
            return date_str
        except:
            return None

    def get_sentenza(self, sentenza_id):
        """Recupera una sentenza dal database"""
        cursor = self.conn.execute(
            "SELECT * FROM sentenze WHERE id = ?",
            (sentenza_id,)
        )
        return cursor.fetchone()

    def search_sentenze(self, anno=None, sezione=None, limit=10):
        """Cerca sentenze con filtri opzionali"""
        sql = "SELECT * FROM sentenze WHERE 1=1"
        params = []

        if anno:
            sql += " AND anno = ?"
            params.append(anno)

        if sezione:
            sql += " AND sezione = ?"
            params.append(sezione)

        sql += " ORDER BY anno DESC, numero DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.execute(sql, params)
        return cursor.fetchall()

    def get_stats(self):
        """Ottieni statistiche dal database"""
        stats = {}

        # Totale sentenze
        cursor = self.conn.execute("SELECT COUNT(*) FROM sentenze")
        stats['totale_sentenze'] = cursor.fetchone()[0]

        # Per anno
        cursor = self.conn.execute("""
            SELECT anno, COUNT(*) as count
            FROM sentenze
            GROUP BY anno
            ORDER BY anno DESC
        """)
        stats['per_anno'] = [dict(row) for row in cursor.fetchall()]

        # Per sezione
        cursor = self.conn.execute("""
            SELECT sezione, COUNT(*) as count
            FROM sentenze
            GROUP BY sezione
            ORDER BY count DESC
        """)
        stats['per_sezione'] = [dict(row) for row in cursor.fetchall()]

        return stats

    def close(self):
        """Chiudi la connessione al database"""
        self.conn.close()


def main():
    """Test del database"""
    print("="*80)
    print("CREAZIONE DATABASE SENTENZE")
    print("="*80)

    # Crea database
    db = SentenzeDatabase('sentenze.db')

    # Carica i dati di esempio dal JSON
    json_file = Path('sentenze_estratte.json')
    if json_file.exists():
        print(f"\n📥 Caricamento dati da {json_file}...")

        with open(json_file, 'r', encoding='utf-8') as f:
            sentenze = json.load(f)

        print(f"📊 Trovate {len(sentenze)} sentenze da inserire")

        # Inserisci le sentenze
        inserted = 0
        for sentenza in sentenze:
            if db.insert_sentenza(sentenza):
                inserted += 1

        print(f"✅ Inserite {inserted} sentenze")

        # Mostra statistiche
        print("\n" + "="*80)
        print("📈 STATISTICHE DATABASE")
        print("="*80)

        stats = db.get_stats()
        print(f"\nTotale sentenze: {stats['totale_sentenze']}")

        print("\nPer anno:")
        for item in stats['per_anno']:
            print(f"  - {item['anno']}: {item['count']} sentenze")

        print("\nPer sezione:")
        for item in stats['per_sezione']:
            print(f"  - {item['sezione']}: {item['count']} sentenze")

        # Esempio di ricerca
        print("\n" + "="*80)
        print("🔍 ESEMPIO RICERCA")
        print("="*80)

        risultati = db.search_sentenze(anno=2025, limit=3)
        print(f"\nPrime 3 sentenze del 2025:")
        for row in risultati:
            print(f"  - {row['numero']}/{row['anno']} - {row['sezione']} - {row['tipo_provvedimento']}")
            print(f"    {row['ecli']}")

    db.close()

    print("\n" + "="*80)
    print("✅ Database creato: sentenze.db")
    print("="*80)


if __name__ == '__main__':
    main()
