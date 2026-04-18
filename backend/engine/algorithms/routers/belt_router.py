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

        # Helper para adicionar belt
        def add_belt(x, y, d, name=belt_name, is_splitter=False):
            if is_splitter:
                bname = belt_name.replace("transport-belt", "splitter")
            else:
                bname = name
            if (x, y) not in seen_belts:
                all_belts.append({"name": bname, "x": x, "y": y, "direction": d})
                seen_belts[(x, y)] = d
                grid.obstacles.add((x, y))

        bus_x_input = -10
        bus_x_output = max_x - 5

        # 3. Roteamento por Cluster/Coluna para evitar spaghetti
        for cluster in layout:
            # Agrupar máquinas por coluna para criar as "Lanes" verticais
            columns = {}
            for machine in cluster["machines"]:
                mx, my = machine["abs_x"], machine["abs_y"]
                m_type = machine.get("machine_type", "assembling-machine-3")
                size = 5 if m_type == "oil-refinery" else 2 if m_type in ("stone-furnace", "steel-furnace") else 3
                columns.setdefault(mx, []).append({"machine": machine, "my": my, "size": size})

            for mx, m_list in columns.items():
                m_list.sort(key=lambda x: x["my"])
                
                # Input (Esquerda) e Output (Direita)
                first_my = m_list[0]["my"]
                last_my = m_list[-1]["my"]
                first_size = m_list[0]["size"]
                last_size = m_list[-1]["size"]
                
                # --- INPUT ---
                in_x = mx - 1
                belt_in_x = in_x - 1
                start_y = first_my + (first_size // 2)
                end_y = last_my + (last_size // 2)

                # Criar a linha vertical de Input
                for y in range(int(start_y), int(end_y) + 1):
                    add_belt(belt_in_x, y, 4 if y == start_y else 8) # Apontando para os inserters se for curva, senão descendo

                # Inserters de Input
                for item in m_list:
                    iy = item["my"] + (item["size"] // 2)
                    if not grid.is_blocked(in_x, iy):
                        all_inserters.append({"name": inserter_name, "x": in_x, "y": iy, "direction": 12})
                        # Virar a esteira para o inserter
                        if (belt_in_x, iy) in seen_belts:
                            seen_belts[(belt_in_x, iy)] = 4 # Aponta para a direita

                # Roteamento A* da ponta superior da linha de entrada para o Barramento Input
                path_in = grid.find_path((bus_x_input + 1, start_y), (belt_in_x - 1, start_y), turn_penalty=5)
                if path_in:
                    add_belt(bus_x_input + 1, start_y, 4, is_splitter=True) # Splitter no Bus
                    for i in range(len(path_in)):
                        tile = path_in[i]
                        nxt = path_in[i+1] if i + 1 < len(path_in) else (belt_in_x, start_y)
                        dx, dy = nxt[0] - tile[0], nxt[1] - tile[1]
                        d = 4 if dx > 0 else (12 if dx < 0 else (8 if dy > 0 else 0))
                        add_belt(tile[0], tile[1], d)

                # --- OUTPUT ---
                out_x = mx + first_size
                belt_out_x = out_x + 1
                start_out_y = first_my + (first_size // 2)
                end_out_y = last_my + (last_size // 2)

                # Criar a linha vertical de Output
                for y in range(int(start_out_y), int(end_out_y) + 1):
                    add_belt(belt_out_x, y, 8) # Descendo coletando

                # Inserters de Output
                for item in m_list:
                    iy = item["my"] + (item["size"] // 2)
                    if not grid.is_blocked(out_x, iy):
                        all_inserters.append({"name": inserter_name, "x": out_x, "y": iy, "direction": 4})
                        
                # Roteamento A* da ponta inferior da linha de saida para o Barramento Output
                path_out = grid.find_path((belt_out_x + 1, end_out_y), (bus_x_output - 1, end_out_y), turn_penalty=5)
                if path_out:
                    for i in range(len(path_out)):
                        tile = path_out[i]
                        nxt = path_out[i+1] if i + 1 < len(path_out) else (bus_x_output, end_out_y)
                        dx, dy = nxt[0] - tile[0], nxt[1] - tile[1]
                        d = 4 if dx > 0 else (12 if dx < 0 else (8 if dy > 0 else 0))
                        add_belt(tile[0], tile[1], d)

        return {
            "inserters": all_inserters,
            "belts": all_belts,
            "obstacles": grid.obstacles
        }
