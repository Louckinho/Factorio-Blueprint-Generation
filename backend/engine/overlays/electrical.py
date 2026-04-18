import math

class ElectricalOverlay:
    # Estatísticas técnicas dos postes do Factorio 1.1+
    POLE_STATS = {
        "small-electric-pole": {"supply": 5, "wire": 7.5, "size": 1},
        "medium-electric-pole": {"supply": 7, "wire": 9.0, "size": 1},
        "substation": {"supply": 18, "wire": 18.0, "size": 2}
    }

    @staticmethod
    def _find_best_pole(unpowered, candidates, obstacles, stats, supply_radius):
        best_pos = None
        best_covered = []
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
                # Distância Chebyshev
                if abs(up["x"] - (cx + stats["size"]/2.0)) <= supply_radius and \
                   abs(up["y"] - (cy + stats["size"]/2.0)) <= supply_radius:
                    covered.append(up)
            
            if len(covered) > len(best_covered):
                best_covered = covered
                best_pos = (cx, cy)
                
        return best_pos, best_covered

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
                m_type = m.get("machine_type", "assembling-machine-3")
                size = 5 if m_type == "oil-refinery" else 2 if m_type in ("stone-furnace", "steel-furnace") else 3
                
                consumers.append({
                    "id": f"m_{m['abs_x']}_{m['abs_y']}",
                    "x": m["abs_x"] + (size / 2.0),
                    "y": m["abs_y"] + (size / 2.0),
                    "powered": False
                })
        
        # 2. Identificar consumidores secundários (braços/beacons/etc)
        if extra_consumers:
            for ent in extra_consumers:
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
        
        if not consumers: return []
        
        max_iters = 100
        while unpowered and max_iters > 0:
            max_iters -= 1
            
            candidates = set()
            for up in unpowered:
                # Gerar candidatos ao redor de máquinas não energizadas
                for dx in range(-int(supply_radius), int(supply_radius) + 1):
                    for dy in range(-int(supply_radius), int(supply_radius) + 1):
                        cand_x, cand_y = math.floor(up["x"] + dx), math.floor(up["y"] + dy)
                        
                        # Se já temos postes, o novo poste DEVE estar ao alcance de pelo menos um existente
                        if all_poles:
                            is_reachable = False
                            for p in all_poles:
                                dist = math.sqrt((cand_x - p["x"])**2 + (cand_y - p["y"])**2)
                                if dist <= stats["wire"]:
                                    is_reachable = True
                                    break
                            if not is_reachable:
                                continue
                                
                        candidates.add((cand_x, cand_y))

            # Se não houver candidatos conectados, mas ainda houver máquinas sem energia, 
            # permitimos um novo ponto inicial (uma nova "ilha" de energia, que o jogador conectará manualmente)
            if not candidates and unpowered:
                for up in unpowered:
                    for dx in range(-int(supply_radius), int(supply_radius) + 1):
                        for dy in range(-int(supply_radius), int(supply_radius) + 1):
                            candidates.add((math.floor(up["x"] + dx), math.floor(up["y"] + dy)))

            best_pos, best_covered = ElectricalOverlay._find_best_pole(unpowered, candidates, obstacles, stats, supply_radius)
            
            if not best_pos and candidates:
                # Tenta novamente ignorando obstáculos se necessário
                best_pos, best_covered = ElectricalOverlay._find_best_pole(unpowered, candidates, set(), stats, supply_radius)
            
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
                break
        
        return all_poles

