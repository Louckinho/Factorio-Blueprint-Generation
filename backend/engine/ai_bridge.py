import httpx
import json
import os
import asyncio

class AIBridge:
    """
    Interface de comunicação assíncrona com o servidor ADAM (Ollama / Local LLM).
    """
    
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    MODEL_NAME = os.getenv("ADAM_MODEL", "adam-v1")
    USE_MOCK = os.getenv("USE_MOCK_AI", "True") == "True"

    @classmethod
    async def call_adam(cls, work_order_json: str):
        """
        Envia a Ordem de Serviço para a IA e retorna a string DSL.
        """
        prompt = f"Gerar layout Factorio baseado nesta Ordem de Serviço:\n{work_order_json}"

        if cls.USE_MOCK:
            await asyncio.sleep(0.5) # Simula latência
            return cls._get_mock_response(prompt)

        payload = {
            "model": cls.MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1, # Rigidez máxima para DSL
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(cls.OLLAMA_URL, json=payload, timeout=60.0)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "").strip()
        except Exception as e:
            print(f"Erro na ponte AI Assíncrona: {e}")
            return None

    @classmethod
    def _get_mock_response(cls, prompt: str):
        """
        Retorna um layout fixo de teste seguindo o padrão META|SIZE.
        """
        mock_dsl = """
META|SIZE:10x5
# Layout de Teste de Fornalhas
F1|0|0|R
F1|0|3|R
B1|2|0|D
B1|2|1|D
B1|2|2|D
B1|2|3|D
B1|2|4|D
I1|1|0|R
I1|1|3|R
"""
        return mock_dsl.strip()
