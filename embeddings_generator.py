#!/usr/bin/env python3
"""
Embeddings Generator - Step 5
Genera embeddings con sentence-transformers per semantic search
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

class EmbeddingsGenerator:
    """Genera embeddings per chunks con sentence-transformers"""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"):
        """
        Args:
            model_name: Modello sentence-transformers (default: multilingue italiano)
        """
        print(f"Caricamento modello {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        print(f"✓ Modello caricato (dimensioni: {self.model.get_sentence_embedding_dimension()})")

    def generate_embeddings(self, chunks_path: Path, use_both: bool = False) -> Dict:
        """
        Genera embeddings per chunks

        Args:
            chunks_path: Path al JSON chunks
            use_both: Se True usa semantic+fixed, altrimenti solo semantic

        Returns:
            Dict con embeddings e metadata
        """
        # Carica chunks
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)

        sentenza_id = chunks_data['sentenza_id']
        print(f"\nGenerazione embeddings per {sentenza_id}...")

        # Seleziona chunks
        if use_both:
            chunks = chunks_data['semantic_chunks'] + chunks_data['fixed_chunks']
            print(f"  Usando TUTTI i chunks: {len(chunks)}")
        else:
            chunks = chunks_data['semantic_chunks']
            print(f"  Usando solo semantic chunks: {len(chunks)}")

        # Estrai testi e metadata
        texts = [chunk['content'] for chunk in chunks]
        chunk_ids = [chunk['chunk_id'] for chunk in chunks]
        chunk_types = [chunk.get('type', 'fixed') for chunk in chunks]

        # Genera embeddings in batch
        print(f"  Generando embeddings (batch_size=32)...")
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        print(f"  ✓ Generati {len(embeddings)} embeddings di {embeddings.shape[1]} dimensioni")

        return {
            'sentenza_id': sentenza_id,
            'embeddings': embeddings,
            'chunk_ids': chunk_ids,
            'chunk_types': chunk_types,
            'model_name': self.model_name,
            'num_chunks': len(chunks),
            'embedding_dim': embeddings.shape[1]
        }

    def save_embeddings(self, results: Dict, output_path: Path):
        """
        Salva embeddings in formato .npz (NumPy compressed)

        File contiene:
        - embeddings: array (n_chunks, 768)
        - chunk_ids: array di stringhe
        - chunk_types: array di stringhe
        - model_name: stringa
        """
        np.savez_compressed(
            str(output_path),
            embeddings=results['embeddings'],
            chunk_ids=np.array(results['chunk_ids']),
            chunk_types=np.array(results['chunk_types']),
            model_name=results['model_name']
        )

        print(f"✓ Salvato: {output_path}")
        print(f"  Dimensione file: {output_path.stat().st_size:,} bytes")


def process_sentenza_embeddings(chunks_path: Path, sentenza_id: str,
                                output_dir: Path, use_both: bool = False,
                                force_regenerate: bool = False) -> Dict:
    """
    Processa una sentenza e genera embeddings

    Args:
        chunks_path: Path al JSON chunks
        sentenza_id: ID sentenza
        output_dir: Directory output
        use_both: Se True usa semantic+fixed chunks
        force_regenerate: Se True rigenera anche se embeddings esistono

    Returns:
        Statistiche embeddings
    """
    output_path = output_dir / f"{sentenza_id}_embeddings.npz"

    # CHECK TIMESTAMP: Rigenera se chunks più recente di embeddings
    if output_path.exists() and not force_regenerate:
        chunks_mtime = chunks_path.stat().st_mtime
        embeddings_mtime = output_path.stat().st_mtime

        if chunks_mtime <= embeddings_mtime:
            print(f"⏭️  Embeddings già aggiornati per {sentenza_id} (skip)")
            return {
                'sentenza_id': sentenza_id,
                'num_chunks': 'N/A',
                'embedding_dim': 768,
                'model_name': 'cached',
                'output_file': str(output_path),
                'file_size': output_path.stat().st_size,
                'status': 'cached'
            }
        else:
            print(f"⚠️  Chunks modificati dopo embeddings - RIGENERAZIONE necessaria")

    # Genera embeddings
    generator = EmbeddingsGenerator()
    results = generator.generate_embeddings(chunks_path, use_both=use_both)

    # Salva
    generator.save_embeddings(results, output_path)

    return {
        'sentenza_id': sentenza_id,
        'num_chunks': results['num_chunks'],
        'embedding_dim': results['embedding_dim'],
        'model_name': results['model_name'],
        'output_file': str(output_path),
        'file_size': output_path.stat().st_size,
        'status': 'generated'
    }


def test_embeddings_search(embeddings_path: Path):
    """
    Test veloce: carica embeddings e mostra similarity tra chunks

    Esempio di come usare gli embeddings per semantic search
    """
    print("\n" + "="*80)
    print("TEST SIMILARITY SEARCH")
    print("="*80)

    # Carica embeddings
    data = np.load(embeddings_path)
    embeddings = data['embeddings']
    chunk_ids = data['chunk_ids']
    chunk_types = data['chunk_types']

    print(f"\nCaricati {len(embeddings)} embeddings")

    # Calcola similarity tra primo chunk (metadata) e tutti gli altri
    from sklearn.metrics.pairwise import cosine_similarity

    query_idx = 0  # metadata chunk
    query_embedding = embeddings[query_idx].reshape(1, -1)

    similarities = cosine_similarity(query_embedding, embeddings)[0]

    # Trova top 5 più simili
    top_indices = np.argsort(similarities)[::-1][1:6]  # Escludi se stesso

    print(f"\nQuery chunk: {chunk_ids[query_idx]} ({chunk_types[query_idx]})")
    print("\nTop 5 chunks più simili:")
    for i, idx in enumerate(top_indices, 1):
        print(f"  {i}. {chunk_ids[idx]} ({chunk_types[idx]}) - Similarity: {similarities[idx]:.3f}")


if __name__ == '__main__':
    print("="*80)
    print("EMBEDDINGS GENERATOR - Step 5")
    print("="*80)

    # Test su sentenza esempio
    chunks_path = Path("chunks/snciv2025530039O_chunks.json")
    sentenza_id = "snciv2025530039O"
    output_dir = Path("embeddings")
    output_dir.mkdir(exist_ok=True)

    # Genera embeddings (solo semantic chunks per default)
    stats = process_sentenza_embeddings(
        chunks_path,
        sentenza_id,
        output_dir,
        use_both=False  # Cambia a True per includere anche fixed chunks
    )

    print("\n" + "="*80)
    print("RISULTATI:")
    print("="*80)
    print(f"Sentenza: {stats['sentenza_id']}")
    print(f"  Chunks processati: {stats['num_chunks']}")
    print(f"  Dimensioni embedding: {stats['embedding_dim']}")
    print(f"  Modello: {stats['model_name']}")
    print(f"  File size: {stats['file_size']:,} bytes")
    print(f"\n✓ Output: {stats['output_file']}")
    print("="*80)

    # Test similarity search
    test_embeddings_search(Path(stats['output_file']))
