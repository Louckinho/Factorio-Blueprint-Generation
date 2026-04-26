import math

class AutoRouter:
    """
    O Engenheiro de Campo do ADAM.
    Pega as máquinas posicionadas pela IA e adiciona a logística (esteiras, braços, postes).
    """

    def __init__(self, tier=1):
        self.tier = tier
        # Configurações de Tier
        self.belts = {1: "transport-belt", 2: "fast-transport-belt", 3: "express-transport-belt"}
        self.inserters = {1: "inserter", 2: "fast-inserter", 3: "stack-inserter"}
        self.poles = {1: "small-electric-pole", 2: "medium-electric-pole", 3: "substation"}

    def route_module(self, entities: list, item_name: str) -> list:
        if not entities: return []

        machines = [e for e in entities if "machine" in e["name"] or "furnace" in e["name"]]
        if not machines: return entities

        new_logistics = []
        min_x = min(m["position"]["x"] for m in machines)
        max_x = max(m["position"]["x"] for m in machines)
        min_y = min(m["position"]["y"] for m in machines)
        max_y = max(m["position"]["y"] for m in machines)

        # Detectar Orientação
        is_horizontal = (max_x - min_x) >= (max_y - min_y)

        belt_name = self.belts.get(self.tier, "transport-belt")
        ins_name = self.inserters.get(self.tier, "inserter")
        pole_name = self.poles.get(self.tier, "small-electric-pole")

        for m in machines:
            mx, my = m["position"]["x"], m["position"]["y"]
            is_furnace = "furnace" in m["name"]
            offset = 1.5 if not is_furnace else 1.0
            
            if is_horizontal:
                # Layout Horizontal: Entrada cima, Saída baixo
                # Entrada
                new_logistics.append({"name": belt_name, "position": {"x": mx, "y": my - offset - 0.5}, "direction": 2}) # Leste
                new_logistics.append({"name": ins_name, "position": {"x": mx, "y": my - offset + 0.5}, "direction": 0}) # Norte (Pega cima)
                # Saída
                new_logistics.append({"name": belt_name, "position": {"x": mx, "y": my + offset + 0.5}, "direction": 2}) # Leste
                new_logistics.append({"name": ins_name, "position": {"x": mx, "y": my + offset - 0.5}, "direction": 0}) # Norte (Põe baixo)
            else:
                # Layout Vertical: Entrada esquerda, Saída direita
                # Entrada
                new_logistics.append({"name": belt_name, "position": {"x": mx - offset - 0.5, "y": my}, "direction": 4}) # Sul
                new_logistics.append({"name": ins_name, "position": {"x": mx - offset + 0.5, "y": my}, "direction": 2}) # Leste (Pega esq)
                # Saída
                new_logistics.append({"name": belt_name, "position": {"x": mx + offset + 0.5, "y": my}, "direction": 4}) # Sul
                new_logistics.append({"name": ins_name, "position": {"x": mx + offset - 0.5, "y": my}, "direction": 2}) # Leste (Põe dir)

        # Postes de Energia
        step = 7 if self.tier == 1 else 9
        if is_horizontal:
            for x in range(int(min_x), int(max_x) + 2, step):
                new_logistics.append({"name": pole_name, "position": {"x": x, "y": min_y + 1.5}})
        else:
            for y in range(int(min_y), int(max_y) + 2, step):
                new_logistics.append({"name": pole_name, "position": {"x": min_x + 1.5, "y": y}})

        return entities + new_logistics
