#!/usr/bin/env python3
"""
MEF SCRAPER - STEP 3: Estrazione entities aggregate
Input: metadata JSON (da step 2)
Output: JSON con entities aggregate e statistiche

Analizza tutte le entities estratte e crea:
- Lista unica di normative citate
- Lista unica di precedenti giurisprudenziali citati
- Statistiche di utilizzo
- Grafo delle citazioni
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict


def aggregate_entities(metadata_file):
    """
    Aggrega tutte le entities dal metadata JSON

    Returns:
        dict: {
            'normative': {...},  # Normative citate con conteggi
            'giurisprudenza': {...},  # Precedenti citati
            'statistics': {...},  # Statistiche generali
            'by_sentence': [...]  # Entities per ogni sentenza
        }
    """
    print("🔗 MEF SCRAPER - STEP 3: Estrazione Entities")
    print("="*70)

    with open(metadata_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sentences = data.get('sentences', [])
    total_sentences = len(sentences)

    print(f"📋 Sentenze da analizzare: {total_sentences}\n")

    # Contatori
    normative = defaultdict(lambda: {'count': 0, 'sentences': [], 'variations': []})
    giurisprudenza = defaultdict(lambda: {'count': 0, 'sentences': [], 'variations': []})

    # Stats
    total_entities = 0
    sentences_with_entities = 0
    sentences_with_normative = 0
    sentences_with_giurisprudenza = 0

    # Processa ogni sentenza
    by_sentence = []

    for sentence in sentences:
        sentence_id = sentence['id']

        # Entities testo + massima
        entities_testo = sentence.get('entities_testo', [])
        entities_massima = sentence.get('entities_massima', [])
        all_entities = entities_testo + entities_massima

        if not all_entities:
            continue

        sentences_with_entities += 1
        total_entities += len(all_entities)

        # Contatori per questa sentenza
        has_normative = False
        has_giurisprudenza = False

        sentence_entities = {
            'sentence_id': sentence_id,
            'estremi': sentence.get('estremi', ''),
            'entities': all_entities,
            'count': len(all_entities)
        }

        # Aggrega per tipo
        for entity in all_entities:
            etype = entity.get('type', 'unknown')
            urn = entity.get('urn', '')
            text = entity.get('text', '')
            parsed = entity.get('parsed', {})

            # Key univoca basata su URN parsed
            if etype == 'normativa':
                key = create_normativa_key(parsed)
                normative[key]['count'] += 1
                normative[key]['sentences'].append(sentence_id)
                normative[key]['variations'].append(text)
                normative[key]['parsed'] = parsed
                has_normative = True

            elif etype == 'giurisprudenza':
                key = create_giurisprudenza_key(parsed)
                giurisprudenza[key]['count'] += 1
                giurisprudenza[key]['sentences'].append(sentence_id)
                giurisprudenza[key]['variations'].append(text)
                giurisprudenza[key]['parsed'] = parsed
                has_giurisprudenza = True

        if has_normative:
            sentences_with_normative += 1
        if has_giurisprudenza:
            sentences_with_giurisprudenza += 1

        by_sentence.append(sentence_entities)

    # Top normative citate
    top_normative = sorted(
        normative.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )[:20]

    # Top precedenti citati
    top_giurisprudenza = sorted(
        giurisprudenza.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )[:20]

    # Risultato
    result = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'source_file': metadata_file,
            'total_sentences': total_sentences,
            'sentences_analyzed': total_sentences
        },
        'statistics': {
            'total_entities': total_entities,
            'total_unique_normative': len(normative),
            'total_unique_giurisprudenza': len(giurisprudenza),
            'sentences_with_entities': sentences_with_entities,
            'sentences_with_normative': sentences_with_normative,
            'sentences_with_giurisprudenza': sentences_with_giurisprudenza,
            'avg_entities_per_sentence': round(total_entities / total_sentences, 2) if total_sentences > 0 else 0
        },
        'normative': {
            'all': dict(normative),
            'top_20': [
                {
                    'key': key,
                    'count': val['count'],
                    'parsed': val['parsed'],
                    'variations': list(set(val['variations']))[:5],  # Prime 5 variazioni
                    'sentences_count': len(set(val['sentences']))
                }
                for key, val in top_normative
            ]
        },
        'giurisprudenza': {
            'all': dict(giurisprudenza),
            'top_20': [
                {
                    'key': key,
                    'count': val['count'],
                    'parsed': val['parsed'],
                    'variations': list(set(val['variations']))[:5],
                    'sentences_count': len(set(val['sentences']))
                }
                for key, val in top_giurisprudenza
            ]
        },
        'by_sentence': by_sentence
    }

    return result


def create_normativa_key(parsed):
    """
    Crea chiave univoca per normativa

    Es: "DLG_1995_504" o "DLG_1995_504_art7"
    """
    kind = parsed.get('kind', 'UNK')
    year = parsed.get('year', '0')
    number = parsed.get('number', '0')
    article = parsed.get('article', '')

    if article:
        return f"{kind}_{year}_{number}_art{article}"
    else:
        return f"{kind}_{year}_{number}"


def create_giurisprudenza_key(parsed):
    """
    Crea chiave univoca per giurisprudenza

    Es: "CCO_SEN_2020_142"
    """
    court = parsed.get('court', 'UNK')
    kind = parsed.get('kind', 'UNK')
    year = parsed.get('year', '0')
    number = parsed.get('number', '0')

    return f"{court}_{kind}_{year}_{number}"


def print_statistics(result):
    """Stampa statistiche leggibili"""
    stats = result['statistics']

    print("\n📊 STATISTICHE ENTITIES")
    print("="*70)
    print(f"Sentenze analizzate:              {stats['total_sentences']}")
    print(f"Sentenze con entities:            {stats['sentences_with_entities']}")
    print(f"  - con normativa:                {stats['sentences_with_normative']}")
    print(f"  - con giurisprudenza:           {stats['sentences_with_giurisprudenza']}")
    print()
    print(f"Entities totali:                  {stats['total_entities']}")
    print(f"  - Normative uniche:             {stats['total_unique_normative']}")
    print(f"  - Precedenti unici:             {stats['total_unique_giurisprudenza']}")
    print(f"Media entities per sentenza:      {stats['avg_entities_per_sentence']}")

    print("\n🏆 TOP 10 NORMATIVE CITATE")
    print("-"*70)
    for i, item in enumerate(result['normative']['top_20'][:10], 1):
        parsed = item['parsed']
        kind = parsed.get('kind', '?')
        year = parsed.get('year', '?')
        number = parsed.get('number', '?')
        article = parsed.get('article', '')
        art_str = f" art. {article}" if article else ""

        print(f"{i:2d}. {kind} {number}/{year}{art_str:15s} -> {item['count']:3d} citazioni in {item['sentences_count']:3d} sentenze")

    print("\n🏛️  TOP 10 PRECEDENTI CITATI")
    print("-"*70)
    for i, item in enumerate(result['giurisprudenza']['top_20'][:10], 1):
        parsed = item['parsed']
        court = parsed.get('court', '?')
        kind = parsed.get('kind', '?')
        year = parsed.get('year', '?')
        number = parsed.get('number', '?')

        print(f"{i:2d}. {court} {kind} {number}/{year:15s} -> {item['count']:3d} citazioni in {item['sentences_count']:3d} sentenze")


def main():
    parser = argparse.ArgumentParser(
        description="MEF SCRAPER - STEP 3: Estrazione entities aggregate"
    )
    parser.add_argument("--input", required=True, help="File metadata JSON (da step 2)")
    parser.add_argument("--output", required=True, help="File output entities JSON")

    args = parser.parse_args()

    # Estrai entities
    result = aggregate_entities(args.input)

    # Stampa statistiche
    print_statistics(result)

    # Salva JSON
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Entities salvate in: {args.output}")


if __name__ == "__main__":
    main()
