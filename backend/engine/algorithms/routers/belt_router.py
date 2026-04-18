from ..pathfinding import GridMap

class BeltRouter:
    @staticmethod
    def route(layout: list, belt_name: str = "express-transport-belt", inserter_name: str = "fast-inserter"):
        if not layout: return {"inserters": [], "belts": [], "obstacles": set()}
        
        # Constantes de distância para Undergrounds
        UNDERGROUND_DIST = {
            "transport-belt": 5,
            "fast-transport-belt": 7,
            "express-transport-belt": 9
        }
        max_dist = UNDERGROUND_DIST.get(belt_name, 9)
        
        # 1. Configurar Grid
        max_x = max(c["abs_x"] + c["width"] for c in layout) + 20
        max_y = max(c["abs_y"] + c["height"] for c in layout) + 20
        grid = GridMap(max_x, max_y)

        # 2. Bloquear Máquinas
        for cluster in layout:
            for m in cluster["machines"]:
                m_type = m.get("machine_type", "assembling-machine-3")
                size = 5 if m_type == "oil-refinery" else 2 if m_type in ("stone-furnace", "steel-furnace") else 3
                grid.block_area(m["abs_x"], m["abs_y"], size, size)

        all_inserters = []
        all_belts = []
        seen_belts = {} # Pos -> Direction

        # 3. Colocar Inserters
        for cluster in layout:
            for machine in cluster["machines"]:
                mx, my = machine["abs_x"], machine["abs_y"]
                m_type = machine.get("machine_type", "assembling-machine-3")
                size = 5 if m_type == "oil-refinery" else 2 if m_type in ("stone-furnace", "steel-furnace") else 3
                
                # Output (Saída - Direita)
                out_x, out_y = mx + size, my + (size // 2)
                if not grid.is_blocked(out_x, out_y):
                    all_inserters.append({"name": inserter_name, "x": out_x, "y": out_y, "direction": 4})
                
                # Input (Entrada - Esquerda)
                in_x, in_y = mx - 1, my + (size // 2)
                if not grid.is_blocked(in_x, in_y):
                    all_inserters.append({"name": inserter_name, "x": in_x, "y": in_y, "direction": 12})

        # 4. Roteamento A*
        bus_x_input = -10
        bus_x_output = max_x - 5
        
        for ins in all_inserters:
            path = []
            if ins["direction"] == 12: # Entrando na máquina (Bus da esquerda)
                start = (bus_x_input + 1, ins["y"])
                end = (ins["x"] - 1, ins["y"])
                path = grid.find_path(start, end, turn_penalty=3)
                if path:
                    # Splitter no barramento
                    all_belts.append({"name": belt_name.replace("transport-belt", "splitter"), "x": start[0], "y": start[1], "direction": 4})
            else: # Saindo da máquina (Bus da direita)
                start = (ins["x"] + 1, ins["y"])
                end = (bus_x_output - 1, ins["y"])
                path = grid.find_path(start, end, turn_penalty=3)

            if not path: continue

            # Helper para direção
            def get_dir(curr, nxt):
                dx, dy = nxt[0] - curr[0], nxt[1] - curr[1]
                if dx > 0: return 4
                if dx < 0: return 12
                if dy > 0: return 8
                if dy < 0: return 0
                return 4

            # Converter path em entidades
            margin_safe = 1 # Garante belt normal perto do inserter
            i = 0
            while i < len(path):
                tile = path[i]
                remaining = len(path) - 1 - i
                jump = min(remaining, max_dist)
                
                # Direção do tile atual
                nxt_tile = path[i+1] if remaining > 0 else (ins["x"], ins["y"])
                d = get_dir(tile, nxt_tile)

                # Tentar Underground
                if jump > 2 and i >= margin_safe and remaining > margin_safe:
                    sub_path = path[i:i+jump+1]
                    is_straight = all(t[0] == tile[0] for t in sub_path) or all(t[1] == tile[1] for t in sub_path)
                    
                    if is_straight:
                        # Entrada Túnel
                        all_belts.append({"name": belt_name.replace("transport-belt", "underground-belt"), "x": tile[0], "y": tile[1], "direction": d, "type": "input"})
                        # Saída Túnel
                        exit_tile = path[i + jump]
                        all_belts.append({"name": belt_name.replace("transport-belt", "underground-belt"), "x": exit_tile[0], "y": exit_tile[1], "direction": d, "type": "output"})
                        i += jump + 1
                        continue

                # Belt Normal
                if tile not in seen_belts:
                    all_belts.append({"name": belt_name, "x": tile[0], "y": tile[1], "direction": d})
                    seen_belts[tile] = d
                i += 1

        return {
            "inserters": all_inserters,
            "belts": all_belts,
            "obstacles": grid.obstacles
        }
