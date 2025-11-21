#!/usr/bin/env python3
"""
NER Processor - Step 2: Named Entity Recognition con confronto modelli
Basato su OUTPUT REALE dei modelli (non assumzioni)
"""

import json
from pathlib import Path
from transformers import pipeline
from typing import Dict, List, Tuple

class NERProcessor:
    """Processa NER con entrambi i modelli e confronta risultati"""

    def __init__(self):
        """Carica entrambi i modelli UNA VOLTA (warm-up)"""
        print("Caricamento modelli NER...")

        # Modello 1: fabiod20 - Specifico Cassazione
        print("  → fabiod20/italian-legal-ner...")
        self.ner_legal = pipeline(
            "ner",
            model="fabiod20/italian-legal-ner",
            aggregation_strategy="average"  # Unisce subword correttamente
        )

        # Modello 2: DeepMount00 - Generico italiano
        print("  → DeepMount00/Italian_NER_XXL_v2...")
        self.ner_general = pipeline(
            "ner",
            model="DeepMount00/Italian_NER_XXL_v2",
            aggregation_strategy="average"
        )

        print("✓ Modelli caricati\n")

        # Mapping categorie per normalizzazione
        self.category_mapping = {
            # DeepMount00 → Standard
            'COGNOME': 'PERSON',
            'NOME': 'PERSON',
            'PERSONA': 'PERSON',
            # fabiod20 → Standard
            'RCR': 'PARTY_PLAINTIFF',
            'RCT': 'PARTY_DEFENDANT',
            # Aggiungi altri mapping se necessario
        }

    def process_text(self, text: str, max_length: int = 10000) -> Dict:
        """
        Processa testo con entrambi i modelli

        Args:
            text: Testo da analizzare
            max_length: Limita lunghezza per performance (sentenze molto lunghe)

        Returns:
            Dict con risultati di entrambi i modelli + confronto
        """
        # Limita lunghezza per performance
        text_trimmed = text[:max_length]

        print(f"Esecuzione NER su {len(text_trimmed):,} caratteri...")

        # Esegui entrambi i modelli
        fabiod20_results = self.ner_legal(text_trimmed)
        deepmount_results = self.ner_general(text_trimmed)

        print(f"  fabiod20: {len(fabiod20_results)} entità")
        print(f"  DeepMount00: {len(deepmount_results)} entità")

        # Confronta e merge
        comparison = self._compare_results(fabiod20_results, deepmount_results)
        merged = self._merge_best(fabiod20_results, deepmount_results, comparison)

        return {
            'fabiod20_results': fabiod20_results,
            'deepmount_results': deepmount_results,
            'comparison': comparison,
            'merged_best': merged
        }

    def _compare_results(self, fabiod20_entities: List, deepmount_entities: List) -> Dict:
        """Confronta entità trovate dai due modelli"""

        # Crea set di span (start, end) per confronto
        fabiod20_spans = {(e['start'], e['end']): e for e in fabiod20_entities}
        deepmount_spans = {(e['start'], e['end']): e for e in deepmount_entities}

        # Trova entità uniche e comuni
        fabiod20_only_spans = set(fabiod20_spans.keys()) - set(deepmount_spans.keys())
        deepmount_only_spans = set(deepmount_spans.keys()) - set(fabiod20_spans.keys())
        both_found_spans = set(fabiod20_spans.keys()) & set(deepmount_spans.keys())

        # Trova conflitti (stesso span, categoria diversa)
        conflicts = []
        for span in both_found_spans:
            f_ent = fabiod20_spans[span]
            d_ent = deepmount_spans[span]

            if f_ent['entity_group'] != d_ent['entity_group']:
                conflicts.append({
                    'span': span,
                    'text': f_ent['word'],
                    'fabiod20_category': f_ent['entity_group'],
                    'deepmount_category': d_ent['entity_group'],
                    'fabiod20_score': f_ent['score'],
                    'deepmount_score': d_ent['score']
                })

        return {
            'fabiod20_unique': [fabiod20_spans[s] for s in fabiod20_only_spans],
            'deepmount_unique': [deepmount_spans[s] for s in deepmount_only_spans],
            'both_found': [fabiod20_spans[s] for s in both_found_spans],
            'conflicts': conflicts
        }

    def _merge_best(self, fabiod20_entities: List, deepmount_entities: List, comparison: Dict) -> List:
        """
        Merge intelligente: prende la migliore entità per ogni span

        Logica:
        - Se stessa entità (stesso span) trovata da entrambi → prendi quella con score più alto
        - Se solo uno la trova → includi comunque
        - Ordina per posizione nel testo
        """
        merged = {}

        # Aggiungi tutte le entità di fabiod20
        for ent in fabiod20_entities:
            span = (ent['start'], ent['end'])
            merged[span] = {
                **ent,
                'source': 'fabiod20'
            }

        # Aggiungi o sostituisci con DeepMount00 se migliore
        for ent in deepmount_entities:
            span = (ent['start'], ent['end'])

            if span in merged:
                # Stesso span: confronta score
                if ent['score'] > merged[span]['score']:
                    merged[span] = {
                        **ent,
                        'source': 'deepmount'
                    }
            else:
                # Nuovo span
                merged[span] = {
                    **ent,
                    'source': 'deepmount'
                }

        # Ordina per posizione
        merged_list = sorted(merged.values(), key=lambda x: x['start'])

        return merged_list

    def save_results(self, results: Dict, output_path: Path):
        """Salva risultati in JSON"""

        # Converti numpy.float32 → float per JSON serialization
        def convert_types(obj):
            if isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            elif hasattr(obj, 'item'):  # numpy types
                return obj.item()
            return obj

        results_clean = convert_types(results)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_clean, f, ensure_ascii=False, indent=2)

        print(f"✓ Salvato: {output_path}")


def process_single_sentenza(txt_path: Path, sentenza_id: str, output_dir: Path) -> Dict:
    """
    Processa una singola sentenza con NER

    Args:
        txt_path: Path al file TXT estratto
        sentenza_id: ID sentenza (es: snciv2025530039O)
        output_dir: Directory output per JSON

    Returns:
        Statistiche processing
    """
    # Carica testo
    with open(txt_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Processa NER
    processor = NERProcessor()
    results = processor.process_text(text)

    # Salva risultati
    output_path = output_dir / f"{sentenza_id}_entities.json"
    processor.save_results(results, output_path)

    return {
        'sentenza_id': sentenza_id,
        'fabiod20_count': len(results['fabiod20_results']),
        'deepmount_count': len(results['deepmount_results']),
        'merged_count': len(results['merged_best']),
        'conflicts': len(results['comparison']['conflicts']),
        'output_file': str(output_path)
    }


if __name__ == '__main__':
    # Test su sentenza esempio
    print("="*80)
    print("NER PROCESSOR - Step 2")
    print("="*80)
    print()

    txt_path = Path("txt/snciv2025530039O.txt")
    sentenza_id = "snciv2025530039O"
    output_dir = Path("entities")
    output_dir.mkdir(exist_ok=True)

    stats = process_single_sentenza(txt_path, sentenza_id, output_dir)

    print("\n" + "="*80)
    print("RISULTATI:")
    print("="*80)
    print(f"Sentenza: {stats['sentenza_id']}")
    print(f"  fabiod20:   {stats['fabiod20_count']} entità")
    print(f"  DeepMount00: {stats['deepmount_count']} entità")
    print(f"  Merged:     {stats['merged_count']} entità")
    print(f"  Conflitti:  {stats['conflicts']}")
    print(f"\n✓ Output: {stats['output_file']}")
    print("="*80)
