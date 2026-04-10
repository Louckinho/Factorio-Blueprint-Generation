import math

class ElectricalOverlay:
    # Estatísticas técnicas dos postes do Factorio 1.1+
    POLE_STATS = {
        "small-electric-pole": {"supply": 5, "wire": 7.5, "size": 1},
        "medium-electric-pole": {"supply": 7, "wire": 9.0, "size": 1},
        "substation": {"supply": 18, "wire": 18.0, "size": 2}
    }

    @staticmethod
    def apply(layout: list, obstacles: set, extra_consumers: list = None, pole_type: str = "medium-electric-pole"):
        """
        Aplica um algoritmo guloso (Set Cover) para garantir 100% de energia em máquinas E braços.
        """
        stats = ElectricalOverlay.POLE_STATS.get(pole_type, ElectricalOverlay.POLE_STATS["medium-electric-pole"])
        supply_radius = stats["supply"] / 2.0
        
        # 1. Identificar consumidores primários (máquinas)
        consumers = []
        for cluster in layout:
            for m in cluster["machines"]:
                consumers.append({
                    "id": f"m_{m['abs_x']}_{m['abs_y']}",
                    "x": m["abs_x"] + 1.5,
                    "y": m["abs_y"] + 1.5,
                    "powered": False
                })
        
        # 2. Identificar consumidores secundários (braços/beacons/etc)
        if extra_consumers:
            for ent in extra_consumers:
                # Filtrar apenas o que consome energia (ex: constant-combinator não consome)
                name = ent.get("name", "")
                if "inserter" in name or "beacon" in name or "mining-drill" in name:
                    consumers.append({
                        "id": f"e_{ent['x']}_{ent['y']}",
                        "x": ent["x"] + 0.5,
                        "y": ent["y"] + 0.5,
                        "powered": False
                    })
        
        all_poles = []
        unpowered = [c for c in consumers if not c["powered"]]
        
        # 2. Definir área de busca (Bounding Box do layout)
        if not consumers: return []
        min_x = min(c["x"] for c in consumers) - 10
        max_x = max(c["x"] for c in consumers) + 10
        min_y = min(c["y"] for c in consumers) - 10
        max_y = max(c["y"] for c in consumers) + 10

        # Limite de iterações para evitar loop infinito
        max_iters = 100
        while unpowered and max_iters > 0:
            max_iters -= 1
            best_pos = None
            best_covered = []
            
            # 3. Heurística Gulosa: Testar posições ao redor das máquinas não alimentadas
            # Em vez de testar o mapa todo (lento), testamos tiles próximos às máquinas unpowered
            candidates = set()
            for up in unpowered:
                for dx in range(-int(supply_radius), int(supply_radius) + 1):
                    for dy in range(-int(supply_radius), int(supply_radius) + 1):
                        candidates.add((math.floor(up["x"] + dx), math.floor(up["y"] + dy)))

            for cx, cy in candidates:
                # Verificar se o tile está livre (não é obstáculo)
                if (cx, cy) in obstacles: continue
                
                # Para subestações (2x2), verificar os outros 3 tiles
                if stats["size"] == 2:
                    if (cx+1, cy) in obstacles or (cx, cy+1) in obstacles or (cx+1, cy+1) in obstacles:
                        continue

                # Calcular quantas máquinas cobre
                covered = []
                for up in unpowered:
                    # Distância Chebyshev (quadrado) para a área de suprimento
                    if abs(up["x"] - (cx + stats["size"]/2)) <= supply_radius and \
                       abs(up["y"] - (cy + stats["size"]/2)) <= supply_radius:
                        covered.append(up)
                
                if len(covered) > len(best_covered):
                    best_covered = covered
                    best_pos = (cx, cy)
            
            if best_pos:
                all_poles.append({
                    "name": pole_type,
                    "x": best_pos[0],
                    "y": best_pos[1]
                })
                for c in best_covered:
                    c["powered"] = True
                unpowered = [c for c in consumers if not c["powered"]]
            else:
                # Se não achou posição válida, mas ainda tem máquina, 
                # pode estar tudo bloqueado. (Corner case)
                break
        
        return all_poles

