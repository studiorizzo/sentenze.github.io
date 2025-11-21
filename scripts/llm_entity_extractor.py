#!/usr/bin/env python3
"""
LLM Entity Extractor - Step 2 Alternative
Usa LLM (Claude/Gemini/Ollama) invece di NER per estrarre entità con maggiore precisione
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import time

# Supporto per multiple LLM backends
LLM_BACKEND = os.getenv("LLM_BACKEND", "gemini")  # "claude", "gemini", o "ollama"


class LLMEntityExtractor:
    """Estrae entità usando LLM invece di modello NER"""

    def __init__(self, backend: str = None):
        """
        Inizializza extractor con backend specificato

        Args:
            backend: "claude", "gemini", o "ollama"
        """
        self.backend = backend or LLM_BACKEND
        self.client = None

        print(f"Inizializzazione LLM Entity Extractor (backend: {self.backend})...")

        if self.backend == "claude":
            self._init_claude()
        elif self.backend == "gemini":
            self._init_gemini()
        elif self.backend == "ollama":
            self._init_ollama()
        else:
            raise ValueError(f"Backend non supportato: {self.backend}")

        print("✓ LLM pronto\n")

    def _init_claude(self):
        """Inizializza Claude API"""
        try:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY non trovata!\n"
                    "Esporta la tua API key: export ANTHROPIC_API_KEY='sk-ant-...'"
                )
            self.client = anthropic.Anthropic(api_key=api_key)
            print("  → Claude API configurato")
        except ImportError:
            raise ImportError("Installa: pip install anthropic")

    def _init_gemini(self):
        """Inizializza Gemini API (FREE tier: 1500 req/day) usando REST API"""
        import requests
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("\n⚠️  GOOGLE_API_KEY non trovata!")
            print("Per usare Gemini FREE tier:")
            print("1. Vai su https://aistudio.google.com/app/apikey")
            print("2. Crea API key gratuita")
            print("3. Export: export GOOGLE_API_KEY='...'")
            raise ValueError("GOOGLE_API_KEY richiesta")

        self.api_key = api_key
        self.client = requests.Session()  # Usa HTTP REST diretto
        print("  → Gemini 1.5 Flash REST API (FREE tier: 1500 req/day)")

    def _init_ollama(self):
        """Inizializza Ollama locale"""
        try:
            import ollama
            # Test connection
            models = ollama.list()
            print(f"  → Ollama locale: {len(models.get('models', []))} modelli disponibili")
            self.client = ollama
        except ImportError:
            raise ImportError("Installa: pip install ollama")
        except Exception as e:
            raise ValueError(f"Ollama non in esecuzione! Avvia: ollama serve\nErrore: {e}")

    def _build_extraction_prompt(self, text: str) -> str:
        """
        Costruisce prompt per estrazione entità

        NOTA: Questo prompt è ottimizzato per sentenze Cassazione italiane
        """
        prompt = f"""Sei un esperto di analisi di sentenze della Corte di Cassazione italiana.

Analizza il seguente testo di una sentenza ed estrai TUTTE le entità rilevanti.

CATEGORIE RICHIESTE:
1. **Presidente**: Nome del Presidente della sezione
2. **Relatore**: Nome del Giudice relatore
3. **Ricorrente** (RCR): Parte che ha presentato ricorso
4. **Controricorrente** (CTR): Parte controricorrente
5. **Avvocati** (AVV): Tutti gli avvocati menzionati (con indicazione di quale parte rappresentano)
6. **Riferimenti Ricorso** (RIC): Numeri di ricorso, RG, etc.
7. **Norme Citate**: Articoli di legge citati (con nome della legge)
8. **Precedenti**: Sentenze precedenti citate (numero e anno)
9. **Tribunali** (TRI): Tribunali/Corti menzionati nel procedimento

FORMATO OUTPUT (JSON valido):
```json
{{
  "presidente": "COGNOME NOME",
  "relatore": "COGNOME NOME",
  "ricorrenti": ["NOME1", "NOME2"],
  "controricorrenti": ["NOME1", "NOME2"],
  "avvocati": [
    {{"nome": "NOME COGNOME", "parte": "ricorrente/controricorrente"}}
  ],
  "riferimenti_ricorso": ["n. 12952/2018", "RG n. ..."],
  "norme_citate": [
    {{"articolo": "art. 360 c.p.c.", "comma": "1, n. 3", "legge": "codice di procedura civile"}}
  ],
  "precedenti_citati": [
    {{"numero": "12345", "anno": "2020", "sezione": "lavoro"}}
  ],
  "tribunali": ["Tribunale di Roma", "Corte d'Appello di ..."]
}}
```

REGOLE:
- Se un'entità non è presente, usa lista vuota [] o null
- Estrai TUTTI i nomi anche se ripetuti
- Per presidente/relatore cerca nell'header: "Presidente: COGNOME NOME"
- Per avvocati indica sempre quale parte rappresentano
- Sii preciso con numeri di articoli e commi

TESTO SENTENZA:
{text[:15000]}

Rispondi SOLO con il JSON, senza altre spiegazioni."""

        return prompt

    def extract_entities(self, text: str, max_retries: int = 3) -> Dict:
        """
        Estrae entità dal testo usando LLM

        Args:
            text: Testo sentenza completo
            max_retries: Tentativi in caso di errore

        Returns:
            Dict con entità estratte
        """
        prompt = self._build_extraction_prompt(text)

        for attempt in range(max_retries):
            try:
                if self.backend == "claude":
                    response = self._extract_claude(prompt)
                elif self.backend == "gemini":
                    response = self._extract_gemini(prompt)
                elif self.backend == "ollama":
                    response = self._extract_ollama(prompt)

                # Parse JSON response
                entities = self._parse_response(response)
                return entities

            except Exception as e:
                print(f"  ⚠️  Tentativo {attempt+1}/{max_retries} fallito: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    # Fallback: return empty structure
                    return self._empty_entities()

        return self._empty_entities()

    def _extract_claude(self, prompt: str) -> str:
        """Estrae usando Claude API"""
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def _extract_gemini(self, prompt: str) -> str:
        """Estrae usando Gemini REST API"""
        # API key va nell'header X-goog-api-key, non nell'URL
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key
        }

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        response = self.client.post(url, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']

    def _extract_ollama(self, prompt: str) -> str:
        """Estrae usando Ollama locale"""
        response = self.client.chat(
            model='llama3.1',  # O 'mistral', 'mixtral', etc.
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']

    def _parse_response(self, response: str) -> Dict:
        """Parse JSON response da LLM"""
        # Estrai JSON da markdown code blocks se presente
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]

        try:
            entities = json.loads(response.strip())
            entities['extraction_method'] = f'llm_{self.backend}'
            entities['count'] = self._count_entities(entities)
            return entities
        except json.JSONDecodeError as e:
            print(f"  ⚠️  Errore parsing JSON: {e}")
            print(f"  Response: {response[:200]}...")
            raise

    def _count_entities(self, entities: Dict) -> int:
        """Conta totale entità estratte"""
        count = 0
        for key, value in entities.items():
            if key in ['extraction_method', 'count']:
                continue
            if isinstance(value, list):
                count += len(value)
            elif value is not None:
                count += 1
        return count

    def _empty_entities(self) -> Dict:
        """Struttura vuota in caso di fallimento"""
        return {
            'presidente': None,
            'relatore': None,
            'ricorrenti': [],
            'controricorrenti': [],
            'avvocati': [],
            'riferimenti_ricorso': [],
            'norme_citate': [],
            'precedenti_citati': [],
            'tribunali': [],
            'extraction_method': f'llm_{self.backend}_failed',
            'count': 0
        }

    def save_results(self, results: Dict, output_path: Path):
        """Salva risultati in JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✓ Salvato: {output_path}")


def process_sentenza_llm(txt_path: Path, sentenza_id: str, output_dir: Path,
                         backend: str = None) -> Dict:
    """
    Processa una singola sentenza con LLM entity extraction

    Args:
        txt_path: Path al file TXT estratto
        sentenza_id: ID sentenza
        output_dir: Directory output
        backend: "claude", "gemini", o "ollama"

    Returns:
        Statistiche processing
    """
    # Carica testo
    with open(txt_path, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"Processamento {sentenza_id} ({len(text):,} caratteri)...")

    # Estrai entità
    extractor = LLMEntityExtractor(backend=backend)
    entities = extractor.extract_entities(text)

    # Salva risultati
    output_path = output_dir / f"{sentenza_id}_entities.json"
    extractor.save_results(entities, output_path)

    return {
        'sentenza_id': sentenza_id,
        'entities_count': entities['count'],
        'extraction_method': entities['extraction_method'],
        'output_file': str(output_path)
    }


if __name__ == '__main__':
    print("="*80)
    print("LLM ENTITY EXTRACTOR - Step 2 Alternative")
    print("="*80)
    print()
    print("BACKEND SUPPORTATI:")
    print("  1. Claude API    → export ANTHROPIC_API_KEY='sk-ant-...'")
    print("  2. Gemini FREE   → export GOOGLE_API_KEY='...' (1500 req/day GRATIS)")
    print("  3. Ollama locale → ollama serve + ollama pull llama3.1")
    print()
    print(f"Backend attivo: {os.getenv('LLM_BACKEND', 'gemini')}")
    print("="*80)
    print()

    # Test su sentenza esempio
    txt_path = Path("txt/snciv2025530039O.txt")
    sentenza_id = "snciv2025530039O"
    output_dir = Path("entities")
    output_dir.mkdir(exist_ok=True)

    if not txt_path.exists():
        print(f"❌ File non trovato: {txt_path}")
        print("Esegui prima: python scripts/final_pdf_extractor.py")
        exit(1)

    try:
        stats = process_sentenza_llm(txt_path, sentenza_id, output_dir)

        print("\n" + "="*80)
        print("RISULTATI:")
        print("="*80)
        print(f"Sentenza: {stats['sentenza_id']}")
        print(f"  Metodo:   {stats['extraction_method']}")
        print(f"  Entità:   {stats['entities_count']}")
        print(f"\n✓ Output: {stats['output_file']}")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Errore: {e}")
        print("\nVerifica:")
        print("  - API key configurata (ANTHROPIC_API_KEY o GOOGLE_API_KEY)")
        print("  - Backend selezionato: export LLM_BACKEND='gemini'")
        print("  - Ollama in esecuzione: ollama serve")
