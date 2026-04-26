import re
import sys
import os
from typing import List, Dict, Any, Tuple, Optional
from draftsman.data import entities

# Configuração global: Caminho para o projeto ADAM (Single Source of Truth para a DSL)
ADAM_PROJECT_PATH = "/mnt/c/Code/Pessoal/Projeto_ADAM_Factorio/src/encoders"
if ADAM_PROJECT_PATH not in sys.path:
    sys.path.append(ADAM_PROJECT_PATH)

try:
    from abbreviation_table import ABBREV_TO_FULL
except ImportError:
    print("ERRO: Não foi possível carregar a tabela de abreviações do ADAM.")
    ABBREV_TO_FULL = {}

class ReverseTranslator:
    """
    Tradutor Reverso: Converte a DSL comprimida da IA ADAM em objetos do factorio-draftsman.
    Implementa normalização de coordenadas e extração de metadados.
    """

    DIR_MAP = {
        '0': 0, '2': 2, '4': 4, '6': 6,
        'U': 0, 'R': 2, 'D': 4, 'L': 6,
    }

    def __init__(self):
        self.hallucination_log = []

    def decode_dsl(self, dsl_string: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Decodifica o bloco DSL completo.
        Retorna (lista_de_entidades, metadados).
        """
        lines = dsl_string.strip().split('\n')
        entities_list = []
        metadata = {"width": 0, "height": 0}

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Processa Metadados: S W H
            if line.startswith('S '):
                metadata = self._parse_meta(line)
                continue

            # Processa Tokens: TOKEN X Y DIR RECIPE
            entity = self._parse_token_line(line)
            if entity:
                entities_list.append(entity)

        # Normalização de Coordenadas (Ajuste de Offset)
        normalized_entities = self._normalize_coordinates(entities_list)

        return normalized_entities, metadata

    def _parse_meta(self, line: str) -> Dict[str, Any]:
        """Extrai tamanho do bloco: S 12 8 -> {'width': 12, 'height': 8}"""
        try:
            parts = line.split()
            if len(parts) >= 3 and parts[0] == 'S':
                return {
                    "width": int(parts[1]),
                    "height": int(parts[2])
                }
        except Exception as e:
            self.hallucination_log.append(f"Erro ao parsear META: {e}")
        return {"width": 0, "height": 0}

    def _parse_token_line(self, line: str) -> Optional[Dict[str, Any]]:
        parts = line.split()
        if len(parts) < 4:
            return None

        token = parts[0].lower()
        try:
            x = float(parts[1])
            y = float(parts[2])
        except ValueError:
            print(f"[TRANSLATOR] Erro: Coordenadas invalidas '{line}'")
            return None

        # 1. Tenta mapear abreviacao (ex: b1 -> transport-belt)
        entity_name = ABBREV_TO_FULL.get(token)
        
        # 2. Se nao for abreviacao, checa se ja e o nome completo
        if not entity_name:
            if token in entities.raw:
                entity_name = token
            else:
                # 3. Fallback: Se for algo como 'k2', mas nao estava no dict por algum motivo
                print(f"[TRANSLATOR] Aviso: Token desconhecido '{token}' na linha: {line}")
                return None

        ent = {
            "name": entity_name,
            "position": {"x": x, "y": y},
            "direction": self.DIR_MAP.get(parts[3].upper() if len(parts) > 3 else '0', 0)
        }

        # Receita ou Extra (Opcional - ex: io_type para undergrounds)
        if len(parts) > 4 and parts[4]:
            ent["recipe"] = parts[4]
            ent["type"] = parts[4] # Pelo drafting, undergrounds usam 'type': 'input'/'output'

        return ent

    def _normalize_coordinates(self, entities_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Garante que as entidades começam em (0,0) ou offset positivo próximo.
        Evita que a IA gere coordenadas negativas que quebrem o tiling.
        """
        if not entities_list:
            return []

        min_x = min(e["position"]["x"] for e in entities_list)
        min_y = min(e["position"]["y"] for e in entities_list)

        # Se houver offset negativo ou muito deslocado, normalizamos para 0
        # Permitimos um pequeno offset positivo se for intencional (ex: 0.5 para centralizar)
        for e in entities_list:
            e["position"]["x"] -= min_x
            e["position"]["y"] -= min_y
            
            # Arredondamento para evitar imprecisões de float (ex: 0.9999 -> 1.0)
            # No Factorio, a maioria das entidades está em grades de 0.5 ou 1.0
            e["position"]["x"] = round(e["position"]["x"] * 2) / 2
            e["position"]["y"] = round(e["position"]["y"] * 2) / 2

        return entities_list
