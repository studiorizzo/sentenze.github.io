#!/usr/bin/env python3
"""Esempi di query sul database"""

import sqlite3
import json

conn = sqlite3.connect('sentenze.db')
conn.row_factory = sqlite3.Row

print("="*80)
print("ESEMPI DI QUERY SUL DATABASE")
print("="*80)

# Query 1: Tutte le sentenze
print("\n1. Tutte le sentenze nel database:")
print("-"*80)
cursor = conn.execute("""
    SELECT id, numero, anno, sezione, tipo_provvedimento, relatore
    FROM sentenze
    ORDER BY anno DESC, numero DESC
""")

for row in cursor.fetchall():
    print(f"  {row['numero']}/{row['anno']} - {row['sezione']} {row['tipo_provvedimento']}")
    print(f"    Relatore: {row['relatore']}")
    print(f"    ID: {row['id']}")
    print()

# Query 2: Sentenze con testo completo
print("\n2. Sentenze con lunghezza testo:")
print("-"*80)
cursor = conn.execute("""
    SELECT numero, anno, testo_length, pdf_num_pages
    FROM sentenze
    WHERE testo_length IS NOT NULL
    ORDER BY testo_length DESC
""")

for row in cursor.fetchall():
    print(f"  {row['numero']}/{row['anno']}: {row['testo_length']:,} caratteri, {row['pdf_num_pages']} pagine")

# Query 3: Statistiche
print("\n3. Statistiche aggregate:")
print("-"*80)
cursor = conn.execute("""
    SELECT
        COUNT(*) as totale,
        COUNT(DISTINCT sezione) as sezioni_distinte,
        COUNT(DISTINCT anno) as anni_distinti,
        MIN(data_deposito) as prima_data,
        MAX(data_deposito) as ultima_data
    FROM sentenze
""")

row = cursor.fetchone()
print(f"  Totale sentenze: {row['totale']}")
print(f"  Sezioni distinte: {row['sezioni_distinte']}")
print(f"  Anni distinti: {row['anni_distinti']}")
print(f"  Prima data deposito: {row['prima_data']}")
print(f"  Ultima data deposito: {row['ultima_data']}")

conn.close()

print("\n" + "="*80)
