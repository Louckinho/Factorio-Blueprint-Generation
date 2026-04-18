import math

class Clusterizer:
    # Função para deduzir o tamanho da máquina (Footprint 2D real)
    @staticmethod
    def get_entity_size(machine_name: str) -> int:
        if machine_name == "oil-refinery":
            return 5
        if machine_name in ("chemical-plant", "centrifuge"):
            return 3
        if machine_name in ("stone-furnace", "steel-furnace"):
            return 2
        # Assembling machines, electric furnaces e fallbacks
        return 3
    
    # Capacidade nominal das esteiras em itens/seg
    BELT_CAPACITIES = {
        "transport-belt": 15.0,
        "fast-transport-belt": 30.0,
        "express-transport-belt": 45.0
    }

    @staticmethod
    def group(nodes_requirements: list, machine_name: str = "assembling-machine-3", belt_name: str = "express-transport-belt"):
        """
        Analisa a lista de máquinas requiridas e as agrupa (Clusters).
        Se a vazão total do cluster exceder a esteira, divide em múltiplas colunas.
        """
        clusters = []
        belt_cap = Clusterizer.BELT_CAPACITIES.get(belt_name, 45.0)

        for node in nodes_requirements:
            if node.get("is_raw_input"):
                continue  # Ore/Fluid entra no Bus, não ganha cluster físico de máquina.
            
            item = node["item"]
            resolved_machine = node.get("machine_type", machine_name)
            entity_size = Clusterizer.get_entity_size(resolved_machine)
            
            # Arredonda frações para cima. Ex: 4.8 fornalhas -> 5 fornalhas.
            machines_exact = node.get("machines_needed", 0)
            if machines_exact <= 0:
                continue
                
            qty = math.ceil(machines_exact)
            
            # Cálculo de Saturação:
            # Qual a vazão total desse grupo?
            total_rate = node.get("rate_per_sec", 0)
            num_lanes = math.ceil(total_rate / belt_cap) if total_rate > 0 else 1
            
            # Se precisarmos de 2 lanes, teremos 2 colunas de máquinas
            machines_per_lane = math.ceil(qty / num_lanes)
            
            width = entity_size * num_lanes + (num_lanes - 1) * 2 # Espaço para belts entre colunas
            height = entity_size * machines_per_lane

            # Monta o registro interno do cluster e suas posições relativas
            machines = []
            for i in range(qty):
                lane_idx = i // machines_per_lane
                pos_in_lane = i % machines_per_lane
                
                machines.append({
                    "item": item,
                    "machine_type": resolved_machine,
                    "rel_x": lane_idx * (entity_size + 2), # Cada lane pula a maquina + espaço p/ belt
                    "rel_y": pos_in_lane * entity_size
                })

            clusters.append({
                "type": "cluster_linear",
                "item_group": item,
                "width": width,
                "height": height,
                "qty": qty,
                "machines": machines
            })

        return clusters
