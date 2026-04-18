import requests
import json
import os

class AIBridge:
    """
    Interface de comunicação com o servidor ADAM (Ollama / Local LLM).
    """
    
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    MODEL_NAME = os.getenv("ADAM_MODEL", "adam-v1")
    USE_MOCK = os.getenv("USE_MOCK_AI", "True") == "True"

    @classmethod
    def call_adam(cls, prompt: str):
        """
        Envia o prompt para a IA e retorna a string DSL.
        """
        if cls.USE_MOCK:
            return cls._get_mock_response(prompt)

        payload = {
            "model": cls.MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2, # Baixa temperatura para manter a rigidez da DSL
            }
        }

        try:
            response = requests.post(cls.OLLAMA_URL, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            print(f"Erro na ponte AI: {e}")
            return None

    @classmethod
    def _get_mock_response(cls, prompt: str):
        """
        Retorna um layout fixo de teste para validar o pipeline sem IA.
        Simula uma linha de 3 fornalhas básicas.
        """
        # Exemplo de DSL mockada
        mock_dsl = """
        # Linha de Fornalhas Mock
        F1|0|0|R
        F1|0|3|R
        F1|0|6|R
        B1|2|0|D
        B1|2|1|D
        B1|2|2|D
        B1|2|3|D
        B1|2|4|D
        B1|2|5|D
        B1|2|6|D
        B1|2|7|D
        I1|1|0|R
        I1|1|3|R
        I1|1|6|R
        """
        return mock_dsl.strip()
