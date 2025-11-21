#!/usr/bin/env python3
"""
Markdown Generator - Step 7
Genera Markdown AI-optimized con frontmatter YAML
"""

import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class MarkdownGenerator:
    """Genera Markdown ottimizzato per AI/RAG da dati estratti"""

    def generate(self, txt_path: Path, entities_path: Path,
                 chunks_path: Path, sentenza_id: str) -> str:
        """
        Genera Markdown completo

        Args:
            txt_path: Path al TXT estratto
            entities_path: Path al JSON entities
            chunks_path: Path al JSON chunks
            sentenza_id: ID sentenza

        Returns:
            Stringa Markdown completa
        """
        # Carica dati
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()

        with open(entities_path, 'r', encoding='utf-8') as f:
            entities = json.load(f)

        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)

        # Estrai metadata
        metadata = self._extract_metadata(text, sentenza_id, entities)

        # Costruisci frontmatter YAML
        frontmatter = self._build_frontmatter(metadata, text)

        # Costruisci corpo markdown
        body = self._build_body(metadata, chunks_data, entities, text)

        # Combina
        markdown = f"---\n{yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)}---\n\n{body}"

        return markdown

    def _extract_metadata(self, text: str, sentenza_id: str, entities: Dict) -> Dict:
        """Estrae metadata dal testo e entities"""

        metadata = {'id': sentenza_id}
        lines = text.split('\n')

        # Parse header (prime 20 righe)
        for line in lines[:20]:
            # Numero
            if 'Num.' in line:
                match = re.search(r'Num\.\s+(\d+)', line)
                if match:
                    metadata['numero'] = match.group(1)

            # Anno
            if 'Anno' in line:
                match = re.search(r'Anno\s+(\d{4})', line)
                if match:
                    metadata['anno'] = int(match.group(1))

            # Sezione
            if 'Sez.' in line:
                match = re.search(r'Sez\.\s+(\d+|[A-Z]+)', line)
                if match:
                    metadata['sezione'] = match.group(1)

            # Presidente
            if 'Presidente:' in line:
                metadata['presidente'] = line.split('Presidente:')[1].strip()

            # Relatore
            if 'Relatore:' in line:
                metadata['relatore'] = line.split('Relatore:')[1].strip()

            # Data pubblicazione
            if 'Data pubblicazione:' in line:
                match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', line)
                if match:
                    metadata['data_pubblicazione'] = match.group(1)

            # RG
            if 'R.G.' in line or 'Registro:' in line:
                match = re.search(r'n\.\s*([\d/]+)', line)
                if match:
                    metadata['rg_numero'] = match.group(1)

            # Oggetto
            if 'Oggetto:' in line:
                metadata['oggetto'] = line.split('Oggetto:')[1].strip()

        # Estrai parti da entities
        merged = entities.get('merged_best', [])
        for entity in merged:
            if entity['entity_group'] == 'RCR':
                metadata['ricorrente'] = entity['word']
            elif entity['entity_group'] in ['CTR', 'RAGIONE_SOCIALE']:
                metadata['controricorrente'] = entity['word']

        # Estrai esito dal dispositivo
        if 'Rigetta il ricorso' in text or 'rigetta il ricorso' in text:
            metadata['esito'] = 'rigetto'
        elif 'Accoglie il ricorso' in text or 'accoglie il ricorso' in text:
            metadata['esito'] = 'accoglimento'
        else:
            metadata['esito'] = 'altro'

        # Estrai spese
        spese_match = re.search(r'€\.\s*([\d.,]+)', text)
        if spese_match:
            metadata['spese'] = f"€ {spese_match.group(1)}"

        return metadata

    def _build_frontmatter(self, metadata: Dict, text: str) -> Dict:
        """Costruisce frontmatter YAML"""

        frontmatter = {
            'numero': metadata.get('numero', ''),
            'anno': metadata.get('anno', ''),
            'sezione': metadata.get('sezione', ''),
            'rg_numero': metadata.get('rg_numero', ''),
            'data_pubblicazione': metadata.get('data_pubblicazione', ''),
        }

        # Composizione
        if 'presidente' in metadata or 'relatore' in metadata:
            frontmatter['presidente'] = metadata.get('presidente', '')
            frontmatter['relatore'] = metadata.get('relatore', '')

        # Parti
        if 'ricorrente' in metadata or 'controricorrente' in metadata:
            frontmatter['ricorrente'] = metadata.get('ricorrente', '')
            frontmatter['controricorrente'] = metadata.get('controricorrente', '')

        # Esito
        frontmatter['esito'] = metadata.get('esito', '')
        if 'spese' in metadata:
            frontmatter['spese'] = metadata.get('spese', '')

        # Classificazione (da oggetto)
        materie = []
        oggetto = metadata.get('oggetto', '').lower()

        # Keywords comuni
        keyword_map = {
            'iva': 'IVA',
            'irpef': 'IRPEF',
            'irap': 'IRAP',
            'tribut': 'tributario',
            'studi di settore': 'studi_settore',
            'accertamento': 'accertamento',
            'reverse charge': 'reverse_charge',
            'contraddittorio': 'contraddittorio_preventivo'
        }

        for keyword, tag in keyword_map.items():
            if keyword in oggetto or keyword in text.lower()[:5000]:
                if tag not in materie:
                    materie.append(tag)

        if materie:
            frontmatter['materie'] = materie

        # Precedenti citati (estrazione base)
        precedenti = []
        precedenti_matches = re.findall(r'Cass\.\s+.*?n\.\s*(\d+).*?del.*?(\d{1,2}).*?(\w+).*?(\d{4})', text)
        for match in precedenti_matches[:5]:  # Top 5
            precedenti.append({
                'numero': match[0],
                'anno': int(match[3])
            })

        if precedenti:
            frontmatter['precedenti'] = precedenti

        # Norme (estrazione pattern base)
        norme = []
        norme_matches = re.findall(r'art\.\s+\d+[^.]{0,50}c\.p\.c\.', text, re.IGNORECASE)
        norme_matches += re.findall(r'd\.P\.R\.\s+n\.\s+\d+/\d{4}', text, re.IGNORECASE)

        # Deduplica e limita
        norme_set = set(norme_matches)
        norme = list(norme_set)[:10]

        if norme:
            frontmatter['norme'] = norme

        return frontmatter

    def _build_body(self, metadata: Dict, chunks_data: Dict,
                    entities: Dict, text: str) -> str:
        """Costruisce corpo Markdown"""

        lines = []

        # Titolo
        numero = metadata.get('numero', 'N/A')
        anno = metadata.get('anno', 'N/A')
        lines.append(f"# Sentenza Cassazione n. {numero}/{anno}\n")

        sezione = metadata.get('sezione', 'N/A')
        data_pub = metadata.get('data_pubblicazione', 'N/A')
        lines.append(f"**Sezione {sezione} Civile** | **Pubblicata: {data_pub}**\n")

        # Sintesi (prime righe oggetto o fatti)
        if 'oggetto' in metadata:
            lines.append(f"## 📋 Oggetto\n\n{metadata['oggetto']}\n")

        # Parti
        lines.append("## 👥 Parti\n")
        if 'ricorrente' in metadata:
            lines.append(f"**Ricorrente**: {metadata['ricorrente']}  ")
        if 'controricorrente' in metadata:
            lines.append(f"**Controricorrente**: {metadata['controricorrente']}  ")
        lines.append("")

        # Fatti di causa
        fatti_chunk = next((c for c in chunks_data['semantic_chunks'] if c['type'] == 'fatti'), None)
        if fatti_chunk:
            lines.append("## 📖 Fatti di Causa\n")
            # Limita lunghezza per leggibilità
            fatti_text = fatti_chunk['content'][:1500]
            if len(fatti_chunk['content']) > 1500:
                fatti_text += "...\n\n*[continua nel testo completo]*"
            lines.append(fatti_text + "\n")

        # Motivi del ricorso
        motivi_chunks = [c for c in chunks_data['semantic_chunks']
                        if c['type'].startswith('motivo_') and c['type'] != 'motivo']

        if motivi_chunks:
            lines.append("## ⚖️ Motivi e Valutazioni\n")

            # TODO: Dopo fix chunking, dividere ricorrente/corte
            # Per ora: ogni chunk come blocco unico
            for i, chunk in enumerate(motivi_chunks, 1):
                motivo_num = chunk['type'].split('_')[-1]
                lines.append(f"### Blocco Motivo {motivo_num}\n")

                # Preview (primi 500 char)
                content_preview = chunk['content'][:500]
                if len(chunk['content']) > 500:
                    content_preview += "...\n\n*[continua nel testo completo]*"

                lines.append(content_preview + "\n")

        # Dispositivo
        dispositivo_chunk = next((c for c in chunks_data['semantic_chunks']
                                 if c['type'] == 'dispositivo'), None)
        if dispositivo_chunk:
            lines.append("## 🎯 Dispositivo\n")
            lines.append(dispositivo_chunk['content'] + "\n")

        # Precedenti citati (se presenti in frontmatter)
        # (già nel YAML, opzionale ripeterli qui)

        # Entità estratte
        lines.append("## 🔗 Entità Estratte (NER)\n")

        merged = entities.get('merged_best', [])

        # Raggruppa per tipo
        giudici = [e['word'] for e in merged if e['entity_group'] in ['CNS', 'COGNOME', 'NOME']]
        org = [e['word'] for e in merged if e['entity_group'] in ['RAGIONE_SOCIALE', 'CTR']]

        if giudici:
            lines.append(f"**Giudici/Persone**: {', '.join(set(giudici[:5]))}  ")
        if org:
            lines.append(f"**Organizzazioni**: {', '.join(set(org[:3]))}  ")

        lines.append("\n---\n")
        lines.append("*Documento generato automaticamente | Fonte: Corte Suprema di Cassazione*")

        return '\n'.join(lines)

    def save_markdown(self, markdown: str, output_path: Path):
        """Salva Markdown"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"✓ Salvato: {output_path}")


def process_sentenza_markdown(txt_path: Path, entities_path: Path,
                              chunks_path: Path, sentenza_id: str,
                              output_dir: Path) -> Dict:
    """
    Processa una sentenza e genera Markdown AI-optimized

    Args:
        txt_path: Path al TXT
        entities_path: Path al JSON entities
        chunks_path: Path al JSON chunks
        sentenza_id: ID sentenza
        output_dir: Directory output

    Returns:
        Statistiche markdown
    """
    generator = MarkdownGenerator()

    # Genera markdown
    print(f"Generazione Markdown per {sentenza_id}...")
    markdown = generator.generate(txt_path, entities_path, chunks_path, sentenza_id)

    # Salva
    output_path = output_dir / f"{sentenza_id}.md"
    generator.save_markdown(markdown, output_path)

    return {
        'sentenza_id': sentenza_id,
        'output_file': str(output_path),
        'markdown_length': len(markdown),
        'file_size': output_path.stat().st_size
    }


if __name__ == '__main__':
    print("="*80)
    print("MARKDOWN GENERATOR - Step 7 (AI-Optimized)")
    print("="*80)
    print()

    # Test su sentenza esempio
    txt_path = Path("txt/snciv2025530039O.txt")
    entities_path = Path("entities/snciv2025530039O_entities.json")
    chunks_path = Path("chunks/snciv2025530039O_chunks.json")
    sentenza_id = "snciv2025530039O"
    output_dir = Path("markdown_ai")
    output_dir.mkdir(exist_ok=True)

    stats = process_sentenza_markdown(
        txt_path, entities_path, chunks_path,
        sentenza_id, output_dir
    )

    print("\n" + "="*80)
    print("RISULTATI:")
    print("="*80)
    print(f"Sentenza: {stats['sentenza_id']}")
    print(f"  Markdown length: {stats['markdown_length']:,} caratteri")
    print(f"  File size: {stats['file_size']:,} bytes")
    print(f"\n✓ Output: {stats['output_file']}")
    print("="*80)

    # Mostra preview
    with open(stats['output_file'], 'r', encoding='utf-8') as f:
        content = f.read()

    print("\n" + "="*80)
    print("PREVIEW FRONTMATTER:")
    print("="*80)
    # Estrai solo frontmatter
    if '---' in content:
        parts = content.split('---')
        if len(parts) >= 3:
            print(parts[1])

    print("\n" + "="*80)
    print("PREVIEW BODY (primi 800 char):")
    print("="*80)
    body_start = content.find('---', 4) + 4
    print(content[body_start:body_start+800] + "...")
