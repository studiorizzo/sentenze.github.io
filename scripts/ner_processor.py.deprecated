#!/usr/bin/env python3
"""
NER Processor - Step 2: Named Entity Recognition
Usa SOLO fabiod20/italian-legal-ner (addestrato su 9000 sentenze Cassazione)
"""

import json
from pathlib import Path
from transformers import pipeline
from typing import Dict, List

class NERProcessor:
    """Processa NER con modello specializzato per sentenze Cassazione"""

    def __init__(self):
        """Carica modello fabiod20/italian-legal-ner"""
        print("Caricamento modello NER...")
        print("  → fabiod20/italian-legal-ner (specializzato Cassazione)...")

        self.ner_legal = pipeline(
            "ner",
            model="fabiod20/italian-legal-ner",
            aggregation_strategy="average"  # Unisce subword correttamente
        )

        print("✓ Modello caricato\n")

    def process_text(self, text: str, max_length: int = 10000) -> Dict:
        """
        Processa testo con NER

        Args:
            text: Testo da analizzare
            max_length: Limita lunghezza per performance (sentenze molto lunghe)

        Returns:
            Dict con entità estratte
        """
        # Limita lunghezza per performance
        text_trimmed = text[:max_length]

        print(f"Esecuzione NER su {len(text_trimmed):,} caratteri...")

        # Esegui NER
        entities = self.ner_legal(text_trimmed)

        print(f"  ✓ {len(entities)} entità estratte")

        # Aggiungi labels esplicite per chiarezza
        entities_with_labels = []
        for ent in entities:
            entity_copy = dict(ent)
            entity_copy['label_extended'] = self._get_label_description(ent['entity_group'])
            entities_with_labels.append(entity_copy)

        return {
            'model': 'fabiod20/italian-legal-ner',
            'entities': entities_with_labels,
            'count': len(entities_with_labels)
        }

    def _get_label_description(self, entity_group: str) -> str:
        """Mappa categorie fabiod20 a descrizioni chiare"""
        label_map = {
            'RCR': 'Ricorrente',
            'CTR': 'Controricorrente',
            'AVV': 'Avvocato',
            'CNS': 'Consigliere/Giudice',
            'RIC': 'Riferimento Ricorso',
            'GIU': 'Giudice',
            'PRE': 'Presidente',
            'REL': 'Relatore',
            'TRI': 'Tribunale'
        }
        return label_map.get(entity_group, entity_group)

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


def process_sentenza_ner(txt_path: Path, sentenza_id: str, output_dir: Path) -> Dict:
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
        'entities_count': results['count'],
        'model': results['model'],
        'output_file': str(output_path)
    }


if __name__ == '__main__':
    # Test su sentenza esempio
    print("="*80)
    print("NER PROCESSOR - Step 2 (fabiod20 ONLY)")
    print("="*80)
    print()

    txt_path = Path("txt/snciv2025530039O.txt")
    sentenza_id = "snciv2025530039O"
    output_dir = Path("entities")
    output_dir.mkdir(exist_ok=True)

    stats = process_sentenza_ner(txt_path, sentenza_id, output_dir)

    print("\n" + "="*80)
    print("RISULTATI:")
    print("="*80)
    print(f"Sentenza: {stats['sentenza_id']}")
    print(f"  Modello:  {stats['model']}")
    print(f"  Entità:   {stats['entities_count']}")
    print(f"\n✓ Output: {stats['output_file']}")
    print("="*80)
