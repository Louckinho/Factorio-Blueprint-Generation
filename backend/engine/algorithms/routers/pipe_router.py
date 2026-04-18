from ..pathfinding import GridMap
from draftsman.data import entities

class PipeRouter:
    @staticmethod
    def route(layout: list, obstacles: set):
        if not layout: return {"pipes": []}
        
        # 1. Configurar Grid (Reaproveita limites do layout)
        max_x = max(c["abs_x"] + c["width"] for c in layout) + 20
        max_y = max(c["abs_y"] + c["height"] for c in layout) + 20
        grid = GridMap(max_x, max_y)
        grid.obstacles = obstacles # Usa os obstáculos das máquinas e esteiras
        
        all_pipes = []
        
        # 2. Identificar Portas de Fluido
        bus_x_input = -10
        
        for cluster in layout:
            for machine in cluster["machines"]:
                mx, my = machine["abs_x"], machine["abs_y"]
                m_type = machine.get("machine_type", "assembling-machine-3")
                recipe_name = machine.get("item")
                size = 5 if m_type == "oil-refinery" else 2 if m_type in ("stone-furnace", "steel-furnace") else 3
                
                # Checar se a receita tem fluidos
                from draftsman.data import recipes
                recipe_data = recipes.raw.get(recipe_name, {})
                uses_fluid = False
                for ing in recipe_data.get("ingredients", []):
                    if ing.get("type") == "fluid": uses_fluid = True
                for res in recipe_data.get("results", []):
                    if res.get("type") == "fluid": uses_fluid = True
                
                if not uses_fluid and m_type != "oil-refinery" and m_type != "chemical-plant":
                    continue

                if m_type in entities.raw and "fluid_boxes" in entities.raw[m_type]:
                    fluid_boxes = entities.raw[m_type]["fluid_boxes"]
                    for box in fluid_boxes:
                        if not isinstance(box, dict): continue
                        
                        for conn in box.get("pipe_connections", []):
                            rel_px, rel_py = conn["position"]
                            abs_px = mx + (size / 2.0) + rel_px - 0.5
                            abs_py = my + (size / 2.0) + rel_py - 0.5
                            p_dir = conn.get("direction", 0)
                            
                            # Rota até o Barramento
                            start = (int(abs_px), int(abs_py))
                            end = (bus_x_input + 1, int(abs_py))
                            
                            # Como a peça de conexão está na borda, precisamos garantir que o A* possa partir dali
                            # Temporariamente remove do obstacles se estiver lá
                            is_at_border = start in grid.obstacles
                            if is_at_border: grid.obstacles.remove(start)
                            
                            path = grid.find_path(start, end, turn_penalty=10)
                            
                            if is_at_border: grid.obstacles.add(start)
                            
                            if path:
                                # Priorizar Underground Pipes (máximo 10 de gap) só se tiver algo no caminho (por simplicidade, usando tubo normal a menos que distante)
                                if len(path) > 2:
                                    first = path[0]
                                    last = path[-1]
                                    is_straight = all(t[0] == first[0] for t in path) or all(t[1] == first[1] for t in path)
                                    dist = len(path)
                                    
                                    if is_straight and dist > 2:
                                        all_pipes.append({"name": "pipe-to-ground", "x": first[0], "y": first[1], "direction": 4 if first[0] < last[0] else 12})
                                        all_pipes.append({"name": "pipe-to-ground", "x": last[0], "y": last[1], "direction": 12 if first[0] < last[0] else 4})

                                    else:
                                        for tile in path:
                                            all_pipes.append({"name": "pipe", "x": tile[0], "y": tile[1]})
                                else:
                                    for tile in path:
                                        all_pipes.append({"name": "pipe", "x": tile[0], "y": tile[1]})
                                        
        return {"pipes": all_pipes}
