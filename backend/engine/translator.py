import re
from typing import List, Dict, Any, Tuple, Optional
from draftsman.data import entities

class ReverseTranslator:
    """
    Tradutor Reverso: Converte a DSL comprimida da IA ADAM em objetos do factorio-draftsman.
    Implementa normalização de coordenadas e extração de metadados.
    """

    TOKEN_MAP = {
        # Assemblers
        'M1': 'assembling-machine-1',
        'M2': 'assembling-machine-2',
        'M3': 'assembling-machine-3',
        # Furnaces
        'F1': 'stone-furnace',
        'F2': 'steel-furnace',
        'F3': 'electric-furnace',
        # Belts
        'B1': 'transport-belt',
        'B2': 'fast-transport-belt',
        'B3': 'express-transport-belt',
        'U1': 'underground-belt',
        'U2': 'fast-underground-belt',
        'U3': 'express-underground-belt',
        'S1': 'splitter',
        'S2': 'fast-splitter',
        'S3': 'express-splitter',
        # Inserters
        'I1': 'inserter',
        'I2': 'fast-inserter',
        'I3': 'long-handed-inserter',
        'I4': 'stack-inserter',
        # Electrical
        'P1': 'small-electric-pole',
        'P2': 'medium-electric-pole',
        'RP': 'roboport',
        # Logistics
        'CLP': 'passive-provider-chest',
        'CLR': 'requester-chest',
        'CLS': 'storage-chest',
        'CLB': 'buffer-chest',
        'CLA': 'active-provider-chest',
        # Fluids
        'PU': 'pipe',
        'UP': 'pipe-to-ground',
        'T': 'storage-tank',
    }

    DIR_MAP = {
        'U': 0, 'R': 2, 'D': 4, 'L': 6,
        '0': 0, '2': 2, '4': 4, '6': 6,
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

            # Processa Metadados: META|SIZE:WxH
            if line.startswith('META|'):
                metadata = self._parse_meta(line)
                continue

            # Processa Tokens: TOKEN|X|Y|DIR|RECIPE|EXTRA
            entity = self._parse_token_line(line)
            if entity:
                entities_list.append(entity)

        # Normalização de Coordenadas (Ajuste de Offset)
        normalized_entities = self._normalize_coordinates(entities_list)

        return normalized_entities, metadata

    def _parse_meta(self, line: str) -> Dict[str, Any]:
        """Extrai tamanho do bloco: META|SIZE:10x15 -> {'width': 10, 'height': 15}"""
        try:
            match = re.search(r'SIZE:(\d+)x(\d+)', line)
            if match:
                return {
                    "width": int(match.group(1)),
                    "height": int(match.group(2))
                }
        except Exception as e:
            self.hallucination_log.append(f"Erro ao parsear META: {e}")
        return {"width": 0, "height": 0}

    def _parse_token_line(self, line: str) -> Optional[Dict[str, Any]]:
        parts = line.split('|')
        if len(parts) < 3:
            return None

        token = parts[0].upper()
        try:
            x = float(parts[1])
            y = float(parts[2])
        except ValueError:
            self.hallucination_log.append(f"Coordenadas inválidas: {line}")
            return None

        entity_name = self.TOKEN_MAP.get(token)
        if not entity_name:
            # Tenta usar o token diretamente se for um nome válido do Factorio
            if token.lower() in entities.raw:
                entity_name = token.lower()
            else:
                self.hallucination_log.append(f"Token desconhecido: {token}")
                return None

        ent = {
            "name": entity_name,
            "position": {"x": x, "y": y},
            "direction": self.DIR_MAP.get(parts[3] if len(parts) > 3 else 'U', 0)
        }

        # Receita (Opcional)
        if len(parts) > 4 and parts[4]:
            ent["recipe"] = parts[4]

        # Extra (Opcional - ex: io_type para undergrounds)
        if len(parts) > 5 and parts[5]:
            ent["type"] = parts[5] # Pelo drafting, undergrounds usam 'type': 'input'/'output'

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
