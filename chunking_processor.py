#!/usr/bin/env python3
"""
Chunking Processor - Step 4
Genera chunks semantici + fixed-size con conteggio token reale (tiktoken)
"""

import json
import re
import tiktoken
from pathlib import Path
from typing import Dict, List
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkingProcessor:
    """Processa testo in chunks semantici e fixed-size"""

    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Args:
            model_name: Modello per tiktoken (default: gpt-3.5-turbo)
        """
        # Tokenizer per conteggio accurato
        self.tokenizer = tiktoken.encoding_for_model(model_name)

        # Text splitter per fixed-size chunks
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,  # Token target
            chunk_overlap=50,
            length_function=self._count_tokens,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def _count_tokens(self, text: str) -> int:
        """Conta token reali con tiktoken"""
        return len(self.tokenizer.encode(text))

    def process_text(self, text: str, sentenza_id: str) -> Dict:
        """
        Processa testo con chunking semantico + fixed-size

        Args:
            text: Testo completo sentenza
            sentenza_id: ID sentenza

        Returns:
            Dict con semantic_chunks e fixed_chunks
        """
        print(f"Chunking per {sentenza_id}...")

        # 1. Semantic chunking
        semantic_chunks = self._semantic_chunking(text)
        print(f"  Semantic chunks: {len(semantic_chunks)}")

        # 2. Fixed-size chunking
        fixed_chunks = self._fixed_size_chunking(text)
        print(f"  Fixed chunks: {len(fixed_chunks)}")

        return {
            'sentenza_id': sentenza_id,
            'semantic_chunks': semantic_chunks,
            'fixed_chunks': fixed_chunks,
            'total_semantic': len(semantic_chunks),
            'total_fixed': len(fixed_chunks)
        }

    def _semantic_chunking(self, text: str) -> List[Dict]:
        """
        Chunking semantico basato su sezioni sentenza

        Sezioni:
        1. Metadata + intestazione
        2. Fatti di causa
        3. Motivi (uno per motivo se numerati)
        4. Dispositivo
        """
        chunks = []

        # Chunk 1: Metadata + intestazione (prime righe fino a ORDINANZA/SENTENZA)
        header_match = re.search(r'(ORDINANZA|SENTENZA)', text, re.IGNORECASE)
        if header_match:
            header_end = header_match.start()
            header_text = text[:header_end].strip()

            if header_text:
                chunks.append({
                    'chunk_id': '001_metadata',
                    'type': 'metadata',
                    'content': header_text,
                    'char_count': len(header_text),
                    'token_count': self._count_tokens(header_text)
                })

        # Chunk 2: Fatti di causa
        fatti_match = re.search(r'FATTI DI CAUSA', text, re.IGNORECASE)
        if fatti_match:
            start = fatti_match.start()

            # Trova fine (prossima sezione MAIUSCOLA o RAGIONI/MOTIVI)
            end_match = re.search(
                r'(RAGIONI DELLA DECISIONE|MOTIVI DELLA DECISIONE|DIRITTO|P\.Q\.M\.)',
                text[start:],
                re.IGNORECASE
            )

            if end_match:
                end = start + end_match.start()
            else:
                # Se non trova, prende fino a metà testo
                end = start + len(text[start:]) // 2

            fatti_text = text[start:end].strip()

            if fatti_text:
                chunks.append({
                    'chunk_id': '002_fatti',
                    'type': 'fatti',
                    'content': fatti_text,
                    'char_count': len(fatti_text),
                    'token_count': self._count_tokens(fatti_text)
                })

        # Chunk 3+: Motivi (cerca pattern numerati: "1.-", "2.-", etc.)
        motivi_match = re.search(
            r'(RAGIONI DELLA DECISIONE|MOTIVI DELLA DECISIONE)',
            text,
            re.IGNORECASE
        )

        if motivi_match:
            motivi_start = motivi_match.start()

            # Trova fine motivi (P.Q.M.)
            pqm_match = re.search(r'P\.Q\.M\.', text[motivi_start:], re.IGNORECASE)
            if pqm_match:
                motivi_end = motivi_start + pqm_match.start()
            else:
                motivi_end = len(text)

            motivi_text = text[motivi_start:motivi_end]

            # Cerca motivi numerati: "1.-", "2.-", etc.
            motivo_splits = re.split(r'\n(\d+)\.-', motivi_text)

            if len(motivo_splits) > 1:
                # Ha motivi numerati
                for i in range(1, len(motivo_splits), 2):
                    if i + 1 < len(motivo_splits):
                        motivo_num = motivo_splits[i]
                        motivo_content = motivo_splits[i + 1].strip()

                        if motivo_content:
                            chunks.append({
                                'chunk_id': f'{int(motivo_num) + 2:03d}_motivo_{motivo_num}',
                                'type': f'motivo_{motivo_num}',
                                'content': motivo_content,
                                'char_count': len(motivo_content),
                                'token_count': self._count_tokens(motivo_content)
                            })
            else:
                # Nessun motivo numerato, prendi tutto insieme
                if motivi_text.strip():
                    chunks.append({
                        'chunk_id': '003_motivazione',
                        'type': 'motivazione',
                        'content': motivi_text.strip(),
                        'char_count': len(motivi_text.strip()),
                        'token_count': self._count_tokens(motivi_text.strip())
                    })

        # Chunk finale: Dispositivo (P.Q.M.)
        pqm_match = re.search(r'P\.Q\.M\.', text, re.IGNORECASE)
        if pqm_match:
            dispositivo_text = text[pqm_match.start():].strip()

            if dispositivo_text:
                chunks.append({
                    'chunk_id': '999_dispositivo',
                    'type': 'dispositivo',
                    'content': dispositivo_text,
                    'char_count': len(dispositivo_text),
                    'token_count': self._count_tokens(dispositivo_text)
                })

        return chunks

    def _fixed_size_chunking(self, text: str) -> List[Dict]:
        """
        Fixed-size chunking con RecursiveCharacterTextSplitter

        Parametri:
        - Chunk size: 512 token
        - Overlap: 50 token
        - Separators: \\n\\n, \\n, ". ", " "
        """
        # Split testo
        text_chunks = self.text_splitter.split_text(text)

        chunks = []
        current_pos = 0

        for idx, chunk_text in enumerate(text_chunks):
            # Trova posizione nel testo originale
            start_pos = text.find(chunk_text, current_pos)
            if start_pos == -1:
                start_pos = current_pos

            end_pos = start_pos + len(chunk_text)

            chunks.append({
                'chunk_id': f'fixed_{idx + 1:03d}',
                'content': chunk_text,
                'char_count': len(chunk_text),
                'token_count': self._count_tokens(chunk_text),
                'start_pos': start_pos,
                'end_pos': end_pos
            })

            current_pos = end_pos

        return chunks

    def save_results(self, results: Dict, output_path: Path):
        """Salva chunks in JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"✓ Salvato: {output_path}")


def process_sentenza_chunking(txt_path: Path, sentenza_id: str, output_dir: Path) -> Dict:
    """
    Processa una sentenza e genera chunks

    Args:
        txt_path: Path al TXT estratto
        sentenza_id: ID sentenza
        output_dir: Directory output

    Returns:
        Statistiche chunking
    """
    # Carica testo
    with open(txt_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Processa chunking
    processor = ChunkingProcessor()
    results = processor.process_text(text, sentenza_id)

    # Salva risultati
    output_path = output_dir / f"{sentenza_id}_chunks.json"
    processor.save_results(results, output_path)

    return {
        'sentenza_id': sentenza_id,
        'semantic_chunks': results['total_semantic'],
        'fixed_chunks': results['total_fixed'],
        'output_file': str(output_path)
    }


if __name__ == '__main__':
    print("="*80)
    print("CHUNKING PROCESSOR - Step 4")
    print("="*80)
    print()

    # Test su sentenza esempio
    txt_path = Path("txt/snciv2025530039O.txt")
    sentenza_id = "snciv2025530039O"
    output_dir = Path("chunks")
    output_dir.mkdir(exist_ok=True)

    stats = process_sentenza_chunking(txt_path, sentenza_id, output_dir)

    print("\n" + "="*80)
    print("RISULTATI:")
    print("="*80)
    print(f"Sentenza: {stats['sentenza_id']}")
    print(f"  Semantic chunks: {stats['semantic_chunks']}")
    print(f"  Fixed chunks: {stats['fixed_chunks']}")
    print(f"\n✓ Output: {stats['output_file']}")
    print("="*80)

    # Mostra preview chunks semantici
    with open(stats['output_file'], 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("\n" + "="*80)
    print("PREVIEW SEMANTIC CHUNKS:")
    print("="*80)
    for chunk in data['semantic_chunks']:
        print(f"\n{chunk['chunk_id']} ({chunk['type']})")
        print(f"  Caratteri: {chunk['char_count']:,}")
        print(f"  Token: {chunk['token_count']:,}")
        print(f"  Preview: {chunk['content'][:100]}...")

    print("\n" + "="*80)
    print(f"PREVIEW FIXED CHUNKS (primi 3 di {len(data['fixed_chunks'])}):")
    print("="*80)
    for chunk in data['fixed_chunks'][:3]:
        print(f"\n{chunk['chunk_id']}")
        print(f"  Token: {chunk['token_count']:,} | Pos: {chunk['start_pos']}-{chunk['end_pos']}")
        print(f"  Preview: {chunk['content'][:80]}...")
