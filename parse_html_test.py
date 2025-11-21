#!/usr/bin/env python3
"""
Script per estrarre metadati delle sentenze dagli HTML
"""

from bs4 import BeautifulSoup
import json
import re
import urllib.parse

def parse_sentenze_html(html_path):
    """Estrae tutti i metadati delle sentenze da un file HTML"""

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Trova tutti i div con class="card" che contengono le sentenze
    cards = soup.find_all('div', class_='card')

    sentenze = []

    for card in cards:
        sentenza = {}

        # ID univoco
        id_elem = card.find('span', {'data-role': 'content', 'data-arg': 'id'})
        if id_elem:
            sentenza['id'] = id_elem.text.strip()

        # Link al PDF
        pdf_elem = card.find('img', class_='pdf')
        if pdf_elem and pdf_elem.get('data-arg'):
            pdf_path = pdf_elem['data-arg']
            # Decodifica URL encoding
            pdf_path = pdf_path.replace('%3F', '?').replace('%3D', '=').replace('%26', '&').replace('%2F', '/')
            sentenza['pdf_url'] = f"https://www.italgiure.giustizia.it{pdf_path}"
            sentenza['pdf_path_relative'] = pdf_path

            # Estrai il nome file PDF dal path per identificazione univoca
            if 'snciv@' in pdf_path or 'snpen@' in pdf_path:
                # Estrai il codice della sentenza dal path
                match = re.search(r'(sn(?:civ|pen)@[^/]+\.pdf)', pdf_path)
                if match:
                    sentenza['pdf_filename'] = match.group(1)

        # Sezione
        szdec_elem = card.find('span', {'data-role': 'content', 'data-arg': 'szdec'})
        if szdec_elem:
            sentenza['sezione'] = szdec_elem.text.strip()

        # Tipo archivio (CIVILE/PENALE)
        kind_elem = card.find('span', {'data-role': 'content', 'data-arg': 'kind'})
        if kind_elem:
            sentenza['archivio'] = kind_elem.text.strip()

        # Tipo provvedimento
        tipoprov_elem = card.find('span', {'data-role': 'content', 'data-arg': 'tipoprov'})
        if tipoprov_elem:
            sentenza['tipo_provvedimento'] = tipoprov_elem.text.strip()

        # Numero sentenza
        numcard_elem = card.find('span', {'data-role': 'content', 'data-arg': 'numcard'})
        if numcard_elem:
            sentenza['numero'] = numcard_elem.text.strip()

        # Anno
        anno_elem = card.find('span', {'data-role': 'content', 'data-arg': 'anno'})
        if anno_elem:
            sentenza['anno'] = anno_elem.text.strip()

        # Data deposito/pubblicazione
        datdep_elem = card.find('span', {'data-role': 'content', 'data-arg': 'datdep'})
        if datdep_elem:
            sentenza['data_deposito'] = datdep_elem.text.strip()

        # Data udienza/decisione
        datdec_elem = card.find('span', {'data-role': 'content', 'data-arg': 'datdec'})
        if datdec_elem:
            sentenza['data_udienza'] = datdec_elem.find('span').text.strip() if datdec_elem.find('span') else datdec_elem.text.strip()

        # ECLI
        ecli_elem = card.find('span', {'data-role': 'content', 'data-arg': 'ecli'})
        if ecli_elem:
            sentenza['ecli'] = ecli_elem.text.strip()

        # Presidente
        presidente_elem = card.find('span', {'data-role': 'content', 'data-arg': 'presidente'})
        if presidente_elem:
            sentenza['presidente'] = presidente_elem.text.strip()

        # Relatore
        relatore_elem = card.find('span', {'data-role': 'content', 'data-arg': 'relatore'})
        if relatore_elem:
            sentenza['relatore'] = relatore_elem.text.strip()

        # Estratti OCR (frammenti)
        ocr_fragments = []
        ocr_elems = card.find_all('span', {'data-role': 'multivaluedcontent', 'data-arg': 'ocr'})
        for ocr_elem in ocr_elems:
            text = ocr_elem.get_text(strip=True)
            # Rimuove il "..." iniziale e finale
            text = re.sub(r'^\.\.\.', '', text)
            text = re.sub(r'\.\.\.$', '', text)
            if text:
                ocr_fragments.append(text.strip())

        if ocr_fragments:
            sentenza['ocr_estratti'] = ocr_fragments

        sentenze.append(sentenza)

    return sentenze


if __name__ == '__main__':
    html_file = '/home/user/sentenze.github.io/html/pagina 1 di 5563.html'

    print("🔍 Parsing HTML...")
    sentenze = parse_sentenze_html(html_file)

    print(f"\n✅ Trovate {len(sentenze)} sentenze\n")

    # Mostra il primo risultato in dettaglio
    if sentenze:
        print("📄 Esempio - Prima sentenza:")
        print(json.dumps(sentenze[0], indent=2, ensure_ascii=False))

        # Salva tutti i risultati
        output_file = '/home/user/sentenze.github.io/sentenze_estratte.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sentenze, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Salvate tutte le {len(sentenze)} sentenze in: {output_file}")
