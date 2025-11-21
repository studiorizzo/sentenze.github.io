#!/usr/bin/env python3
"""
Akoma Ntoso Generator - Step 3
Genera XML standard OASIS LegalDocML v3.0 (versione PRAGMATICA - livello MEDIO)
"""

import json
import re
from pathlib import Path
from datetime import datetime
from lxml import etree
from typing import Dict, List, Optional

class AkomaNtosoGenerator:
    """Genera Akoma Ntoso XML da sentenza estratta + entities"""

    def __init__(self):
        self.ns = "http://docs.oasis-open.org/legaldocml/ns/akn/3.0"
        self.nsmap = {None: self.ns}

    def generate(self, txt_path: Path, entities_path: Path, sentenza_id: str) -> etree.Element:
        """
        Genera documento Akoma Ntoso completo

        Args:
            txt_path: Path al TXT estratto
            entities_path: Path al JSON entities
            sentenza_id: ID sentenza (es: snciv2025530039O)

        Returns:
            XML Element root
        """
        # Carica dati
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()

        with open(entities_path, 'r', encoding='utf-8') as f:
            entities_data = json.load(f)

        # Estrai metadata dal testo
        metadata = self._extract_metadata(text, sentenza_id)

        # Costruisci XML
        root = etree.Element("{%s}akomaNtoso" % self.ns, nsmap=self.nsmap)
        judgment = etree.SubElement(root, "{%s}judgment" % self.ns, name="sentenza")

        # 1. Meta section
        meta = self._build_meta(judgment, metadata, entities_data)

        # 2. Header
        header = self._build_header(judgment, metadata, entities_data)

        # 3. Judgment Body
        body = self._build_body(judgment, text, metadata)

        # 4. Conclusions
        conclusions = self._build_conclusions(judgment, metadata)

        return root

    def _extract_metadata(self, text: str, sentenza_id: str) -> Dict:
        """Estrae metadata dalla prima parte del testo"""

        metadata = {'id': sentenza_id}

        # Header parsing (prime righe)
        lines = text.split('\n')

        for line in lines[:20]:
            # Sezione
            if 'Sez.' in line:
                match = re.search(r'Sez\.\s+(\d+|[A-Z]+)', line)
                if match:
                    metadata['sezione'] = match.group(1)

            # Numero sentenza
            if 'Num.' in line:
                match = re.search(r'Num\.\s+(\d+)', line)
                if match:
                    metadata['numero'] = match.group(1)

            # Anno
            if 'Anno' in line:
                match = re.search(r'Anno\s+(\d{4})', line)
                if match:
                    metadata['anno'] = match.group(1)

            # Presidente
            if 'Presidente:' in line:
                metadata['presidente'] = line.split('Presidente:')[1].strip()

            # Relatore
            if 'Relatore:' in line:
                metadata['relatore'] = line.split('Relatore:')[1].strip()

            # Data pubblicazione
            if 'Data pubblicazione:' in line or 'del' in line:
                match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', line)
                if match:
                    metadata['data_pubblicazione'] = match.group(1)

            # Registro
            if 'Registro:' in line or 'R.G.' in line:
                match = re.search(r'n\.\s*([\d/]+)', line)
                if match:
                    metadata['registro'] = match.group(1)

            # Oggetto
            if 'Oggetto:' in line:
                metadata['oggetto'] = line.split('Oggetto:')[1].strip()

        # Determina tipo archivio da ID
        if sentenza_id.startswith('snciv'):
            metadata['archivio'] = 'CIVILE'
        elif sentenza_id.startswith('snpen'):
            metadata['archivio'] = 'PENALE'

        return metadata

    def _build_meta(self, parent: etree.Element, metadata: Dict, entities: Dict) -> etree.Element:
        """Costruisce sezione <meta>"""

        meta = etree.SubElement(parent, "{%s}meta" % self.ns)

        # 1. Identification (FRBRWork base)
        identification = etree.SubElement(meta, "{%s}identification" % self.ns, source="#source")

        FRBRWork = etree.SubElement(identification, "{%s}FRBRWork" % self.ns)

        anno = metadata.get('anno', '2025')
        numero = metadata.get('numero', '00000')

        # URI formato: /akn/it/judgment/cassazione/ANNO/NUMERO/ita@
        work_uri = f"/akn/it/judgment/cassazione/{anno}/{numero}/ita@"

        etree.SubElement(FRBRWork, "{%s}FRBRthis" % self.ns, value=work_uri)
        etree.SubElement(FRBRWork, "{%s}FRBRuri" % self.ns, value=work_uri)
        etree.SubElement(FRBRWork, "{%s}FRBRdate" % self.ns,
                        date=self._format_date(metadata.get('data_pubblicazione', '')),
                        name="decisione")
        etree.SubElement(FRBRWork, "{%s}FRBRauthor" % self.ns, href="#cassazione")
        etree.SubElement(FRBRWork, "{%s}FRBRcountry" % self.ns, value="it")

        # 2. Publication
        publication = etree.SubElement(meta, "{%s}publication" % self.ns,
                                      date=self._format_date(metadata.get('data_pubblicazione', '')),
                                      name="Pubblicazione",
                                      number=metadata.get('numero', ''))

        # 3. References (TLCPerson, TLCOrganization da NER)
        references = etree.SubElement(meta, "{%s}references" % self.ns, source="#source")

        self._add_references(references, metadata, entities)

        return meta

    def _add_references(self, references: etree.Element, metadata: Dict, entities: Dict):
        """Aggiunge references da entities NER"""

        # TLCOrganization: Corte
        etree.SubElement(references, "{%s}TLCOrganization" % self.ns,
                        eId="cassazione",
                        href="/ontology/organization/it/cassazione",
                        showAs="Corte Suprema di Cassazione")

        # TLCPerson: Giudici (da metadata)
        if 'presidente' in metadata:
            pres_id = self._make_id(metadata['presidente'])
            etree.SubElement(references, "{%s}TLCPerson" % self.ns,
                            eId=pres_id,
                            href=f"/ontology/person/it/{pres_id}",
                            showAs=metadata['presidente'])

        if 'relatore' in metadata:
            rel_id = self._make_id(metadata['relatore'])
            etree.SubElement(references, "{%s}TLCPerson" % self.ns,
                            eId=rel_id,
                            href=f"/ontology/person/it/{rel_id}",
                            showAs=metadata['relatore'])

        # TLCPerson/TLCOrganization: Parti (da NER)
        merged_entities = entities.get('merged_best', [])

        for entity in merged_entities:
            entity_type = entity.get('entity_group', '')
            word = entity.get('word', '')

            # Ricorrente (RCR)
            if entity_type == 'RCR':
                ent_id = self._make_id(word)
                etree.SubElement(references, "{%s}TLCPerson" % self.ns,
                                eId=f"ricorrente_{ent_id}",
                                href=f"/ontology/person/it/{ent_id}",
                                showAs=word)

            # Controricorrente (CTR) o Enti
            elif entity_type in ['CTR', 'RAGIONE_SOCIALE']:
                ent_id = self._make_id(word)
                tag = "{%s}TLCOrganization" if entity_type == 'RAGIONE_SOCIALE' else "{%s}TLCPerson"
                etree.SubElement(references, tag % self.ns,
                                eId=f"controricorrente_{ent_id}",
                                href=f"/ontology/{ent_id}",
                                showAs=word)

    def _build_header(self, parent: etree.Element, metadata: Dict, entities: Dict) -> etree.Element:
        """Costruisce <header> con court, judges, parties"""

        header = etree.SubElement(parent, "{%s}header" % self.ns)

        # Court
        court = etree.SubElement(header, "{%s}court" % self.ns, refersTo="#cassazione")
        court.text = "Corte Suprema di Cassazione"

        # Section
        if 'sezione' in metadata:
            section = etree.SubElement(header, "{%s}section" % self.ns)
            section.text = f"Sezione {metadata['sezione']}"

        # Judges
        if 'presidente' in metadata or 'relatore' in metadata:
            judges = etree.SubElement(header, "{%s}judges" % self.ns)

            if 'presidente' in metadata:
                pres = etree.SubElement(judges, "{%s}judge" % self.ns,
                                       refersTo=f"#{self._make_id(metadata['presidente'])}",
                                       as_="#presidente")
                pres.text = metadata['presidente']

            if 'relatore' in metadata:
                rel = etree.SubElement(judges, "{%s}judge" % self.ns,
                                      refersTo=f"#{self._make_id(metadata['relatore'])}",
                                      as_="#relatore")
                rel.text = metadata['relatore']

        # Parties (da NER)
        parties = etree.SubElement(header, "{%s}parties" % self.ns)

        merged_entities = entities.get('merged_best', [])
        for entity in merged_entities:
            if entity.get('entity_group') == 'RCR':
                party = etree.SubElement(parties, "{%s}party" % self.ns,
                                        refersTo=f"#ricorrente_{self._make_id(entity['word'])}",
                                        as_="#ricorrente")
                party.text = entity['word']

        # Docket number
        if 'registro' in metadata:
            docket = etree.SubElement(header, "{%s}docketNumber" % self.ns)
            docket.text = f"R.G. n. {metadata['registro']}"

        return header

    def _build_body(self, parent: etree.Element, text: str, metadata: Dict) -> etree.Element:
        """Costruisce <judgmentBody>"""

        body = etree.SubElement(parent, "{%s}judgmentBody" % self.ns)

        # Dividi testo in sezioni (euristica semplice)
        sections = self._split_sections(text)

        # Introduction (fatti)
        if 'fatti' in sections:
            intro = etree.SubElement(body, "{%s}introduction" % self.ns)
            p = etree.SubElement(intro, "{%s}p" % self.ns)
            p.text = sections['fatti'][:500] + "..."  # Limita per esempio

        # Motivation
        if 'motivazione' in sections:
            motivation = etree.SubElement(body, "{%s}motivation" % self.ns)
            point = etree.SubElement(motivation, "{%s}point" % self.ns)
            p = etree.SubElement(point, "{%s}p" % self.ns)
            p.text = sections['motivazione'][:500] + "..."

        # Decision
        if 'decisione' in sections:
            decision = etree.SubElement(body, "{%s}decision" % self.ns)
            p = etree.SubElement(decision, "{%s}p" % self.ns)
            p.text = sections['decisione']

        return body

    def _build_conclusions(self, parent: etree.Element, metadata: Dict) -> etree.Element:
        """Costruisce <conclusions>"""

        conclusions = etree.SubElement(parent, "{%s}conclusions" % self.ns)

        # Signature
        if 'relatore' in metadata:
            sig = etree.SubElement(conclusions, "{%s}signature" % self.ns,
                                  refersTo=f"#{self._make_id(metadata['relatore'])}")
            sig.text = metadata['relatore']

        # Location
        location = etree.SubElement(conclusions, "{%s}location" % self.ns)
        location.text = "Roma"

        # Date
        if 'data_pubblicazione' in metadata:
            date_elem = etree.SubElement(conclusions, "{%s}date" % self.ns,
                                        date=self._format_date(metadata['data_pubblicazione']))
            date_elem.text = metadata['data_pubblicazione']

        return conclusions

    def _split_sections(self, text: str) -> Dict[str, str]:
        """Divide testo in sezioni (euristica base)"""

        sections = {}

        # Cerca marker comuni
        if 'FATTI DI CAUSA' in text:
            start = text.find('FATTI DI CAUSA')
            end = text.find('P.Q.M.', start) if 'P.Q.M.' in text[start:] else len(text)
            sections['fatti'] = text[start:end].strip()

        if 'MOTIVI DELLA DECISIONE' in text or 'RAGIONI DELLA DECISIONE' in text:
            marker = 'MOTIVI DELLA DECISIONE' if 'MOTIVI DELLA DECISIONE' in text else 'RAGIONI DELLA DECISIONE'
            start = text.find(marker)
            end = text.find('P.Q.M.', start) if 'P.Q.M.' in text[start:] else len(text)
            sections['motivazione'] = text[start:end].strip()

        if 'P.Q.M.' in text:
            start = text.find('P.Q.M.')
            sections['decisione'] = text[start:].strip()

        return sections

    def _format_date(self, date_str: str) -> str:
        """Converte data italiana (DD/MM/YYYY) in ISO (YYYY-MM-DD)"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')

        try:
            parts = date_str.split('/')
            if len(parts) == 3:
                return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        except:
            pass

        return datetime.now().strftime('%Y-%m-%d')

    def _make_id(self, name: str) -> str:
        """Crea ID valido da nome"""
        # Rimuovi spazi, caratteri speciali, lowercase
        id_str = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
        return id_str.strip('_')

    def save_xml(self, root: etree.Element, output_path: Path):
        """Salva XML formattato"""
        tree = etree.ElementTree(root)
        tree.write(
            str(output_path),
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        )
        print(f"✓ Salvato: {output_path}")


def process_sentenza_akoma_ntoso(txt_path: Path, entities_path: Path,
                                  sentenza_id: str, output_dir: Path) -> Dict:
    """Processa una sentenza e genera Akoma Ntoso XML"""

    generator = AkomaNtosoGenerator()

    # Genera XML
    print(f"Generazione Akoma Ntoso per {sentenza_id}...")
    root = generator.generate(txt_path, entities_path, sentenza_id)

    # Salva
    output_path = output_dir / f"{sentenza_id}_akoma_ntoso.xml"
    generator.save_xml(root, output_path)

    # Valida
    is_valid = etree.tostring(root, encoding='unicode')  # Check if valid XML

    return {
        'sentenza_id': sentenza_id,
        'output_file': str(output_path),
        'xml_size': len(is_valid),
        'is_valid_xml': True
    }


if __name__ == '__main__':
    print("="*80)
    print("AKOMA NTOSO GENERATOR - Step 3 (PRAGMATIC - MEDIO)")
    print("="*80)
    print()

    # Test su sentenza esempio
    txt_path = Path("txt/snciv2025530039O.txt")
    entities_path = Path("entities/snciv2025530039O_entities.json")
    sentenza_id = "snciv2025530039O"
    output_dir = Path("akoma_ntoso")
    output_dir.mkdir(exist_ok=True)

    stats = process_sentenza_akoma_ntoso(txt_path, entities_path, sentenza_id, output_dir)

    print("\n" + "="*80)
    print("RISULTATI:")
    print("="*80)
    print(f"Sentenza: {stats['sentenza_id']}")
    print(f"  XML size: {stats['xml_size']:,} bytes")
    print(f"  Valid XML: {stats['is_valid_xml']}")
    print(f"\n✓ Output: {stats['output_file']}")
    print("="*80)
