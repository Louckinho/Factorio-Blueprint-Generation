import heapq
import collections
from draftsman.data import entities, recipes

class GridMap:
    def __init__(self, max_x, max_y):
        self.max_x = max_x + 10 # Sobra de respiro
        self.max_y = max_y + 10
        self.obstacles = set()
        
    def block_area(self, x, y, w, h):
        for i in range(int(x), int(x + w)):
            for j in range(int(y), int(y + h)):
                self.obstacles.add((i, j))

    def is_blocked(self, x, y):
        return (x, y) in self.obstacles or x < -20 or y < -20 or x > self.max_x or y > self.max_y

    def find_path(self, start, end, avoid_diagonal=True):
        """
        Algoritmo A* Clássico para encontrar o caminho mais curto no grid.
        Retorna uma lista de tuplas (x, y).
        """
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        close_set = set()
        came_from = {}
        gscore = {start: 0}
        fscore = {start: self.heuristic(start, end)}
        oheap = []

        heapq.heappush(oheap, (fscore[start], start))
        
        while oheap:
            current = heapq.heappop(oheap)[1]

            if current == end:
                data = []
                while current in came_from:
                    data.append(current)
                    current = came_from[current]
                return data[::-1]

            close_set.add(current)
            for i, j in neighbors:
                neighbor = current[0] + i, current[1] + j
                tentative_g_score = gscore[current] + 1
                
                if self.is_blocked(neighbor[0], neighbor[1]):
                    continue
                
                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                    continue
                    
                if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + self.heuristic(neighbor, end)
                    heapq.heappush(oheap, (fscore[neighbor], neighbor))
                    
        return []

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

class AStarRouter:
    @staticmethod
    def route_belts(layout: list, belt_name: str = "express-transport-belt"):
        """
        Recebe o layout absoluto das máquinas, aplica Inserters, CANOS, DIVISORES e ESTEIRAS.
        """
        # 1. Definir os limites do nosso Universo Virtual para a Malha A*
        if not layout: return layout
        
        # Constantes de distância para Undergrounds
        UNDERGROUND_DIST = {
            "transport-belt": 5,
            "fast-transport-belt": 7,
            "express-transport-belt": 9
        }
        max_dist = UNDERGROUND_DIST.get(belt_name, 9)
        
        max_x = max(c["abs_x"] + c["width"] for c in layout)
        max_y = max(c["abs_y"] + c["height"] for c in layout)
        grid = GridMap(max_x, max_y)

        # 2. Bloquear Fisicamente o espaço das máquinas para que as esteiras não as atravessem
        for cluster in layout:
            for m in cluster["machines"]:
                # Assembling machine tem sempre 3x3
                grid.block_area(m["abs_x"], m["abs_y"], 3, 3)

        # Listas globais matemáticas
        all_inserters = []
        all_belts = []
        all_pipes = []

        # 3. Lógica de Inserters (Braços)
        # Para cada máquina, precisamos de 1 saída e N entradas (simplificação atual: 1 saída, 1 entrada genérica)
        for cluster in layout:
            for index, machine in enumerate(cluster["machines"]):
                # Coordenadas da Máquina (canto superior esquerdo)
                mx = machine["abs_x"]
                my = machine["abs_y"]
                
                # Inserter de SAÍDA (Output): Tentaremos colocar à DIREITA da máquina (mx + 3)
                output_ix = mx + 3
                output_iy = my + 1 # Centro vertical da maquina de altura 3
                
                if not grid.is_blocked(output_ix, output_iy):
                    grid.block_area(output_ix, output_iy, 1, 1)
                    # No factorio, DIRECTION afeta o Inserter. Direction 4 = Leste. Output para leste.
                    all_inserters.append({
                        "name": "fast-inserter",
                        "x": output_ix, "y": output_iy,
                        "direction": 4 # 4 = Leste (Drop fora da maquina, pickup dentro)
                    })
                    
                # Inserter de ENTRADA (Input): Tentaremos colocar à ESQUERDA da máquina (mx - 1)
                input_ix = mx - 1
                input_iy = my + 1 
                
                if not grid.is_blocked(input_ix, input_iy):
                    grid.block_area(input_ix, input_iy, 1, 1)
                    # 12 = Oeste. (Pickup fora da maquina e drop dentro)
                    all_inserters.append({
                        "name": "fast-inserter",
                        "x": input_ix, "y": input_iy,
                        "direction": 12 
                    })

                # --- NOVA LÓGICA DE FLUIDOS ---
                # Verificar se a máquina (Ex: Chemical Plant) requer fluidos
                m_type = machine.get("machine_type", "assembling-machine-3")
                if m_type in entities.raw and "fluid_boxes" in entities.raw[m_type]:
                    # Pegar conexões de fluidos da máquina
                    fluid_boxes = entities.raw[m_type]["fluid_boxes"]
                    for box in fluid_boxes:
                        if not isinstance(box, dict): continue
                        
                        connections = box.get("pipe_connections", [])
                        for conn in connections:
                            # Posição relativa da porta [x, y]
                            rel_px, rel_py = conn["position"]
                            # Posição absoluta da porta no grid
                            # No Draftsman, as posições de fluid_boxes são relativas ao CENTRO da entidade.
                            # Nossas máquinas 3x3 têm centro em (mx+1.5, my+1.5)
                            abs_px = mx + 1.5 + rel_px - 0.5
                            abs_py = my + 1.5 + rel_py - 0.5
                            
                            # Tentar colocar um cano subterrâneo apontando para FORA
                            # A 'direction' do conn nos diz para onde a porta aponta (0=N, 4=E, 8=S, 12=W)
                            p_dir = conn.get("direction", 0)
                            
                            # Como o usuário quer PREFERÊNCIA subterrânea:
                            pipe_name = "pipe-to-ground"
                            
                            # IMPORTANTE: Afrouxar a regra de bloqueio aqui pois a porta fica na borda da maquina
                            all_pipes.append({
                                "name": pipe_name,
                                "x": abs_px, "y": abs_py,
                                "direction": p_dir # Aponta para fora da máquina
                            })
        
        # 4. Roteamento A* Real (V4.2)
        # Ligar os Inserters de ENTRADA ao barramento esquerdo
        bus_x_input = -10
        for ins in all_inserters:
            if ins["direction"] == 12: # Inserter apontando para dentro (Oeste)
                # Origem: No barramento. Destino: atrás do inserter
                start_x = bus_x_input + 1
                start_y = ins["y"]
                dest_x = ins["x"] - 1 # Tile logo atrás do inserter
                dest_y = ins["y"]
                
                path = grid.find_path((start_x, start_y), (dest_x, dest_y))
                
                # Para cada conexão ao barramento, usamos um SPLITTER
                all_belts.append({
                    "name": belt_name.replace("transport-belt", "splitter"), # Ex: express-splitter
                    "x": start_x, "y": start_y,
                    "direction": 4
                })

                # Roteamento de Underground Belts (Votação por distância)
                if len(path) > 2:
                    # Tenta pular vãos longos usando Undergrounds
                    i = 0
                    while i < len(path):
                        tile = path[i]
                        # Ver se podemos pular um trecho
                        remaining = len(path) - 1 - i
                        jump = min(remaining, max_dist)
                        
                        if jump > 2:
                            # Entrada
                            all_belts.append({
                                "name": belt_name.replace("transport-belt", "underground-belt"),
                                "x": tile[0], "y": tile[1],
                                "direction": 4, "type": "input"
                            })
                            # Saída
                            exit_tile = path[i + jump]
                            all_belts.append({
                                "name": belt_name.replace("transport-belt", "underground-belt"),
                                "x": exit_tile[0], "y": exit_tile[1],
                                "direction": 4, "type": "output"
                            })
                            i += jump + 1
                        else:
                            all_belts.append({
                                "name": belt_name,
                                "x": tile[0], "y": tile[1],
                                "direction": 4
                            })
                            i += 1
                else:
                    for tile in path:
                        all_belts.append({
                            "name": belt_name,
                            "x": tile[0], "y": tile[1],
                            "direction": 4
                        })

        # Ligar as portas de FLUIDO ao barramento lateral
        for p in list(all_pipes):
            # Vamos traçar um caminho até a borda do Bus
            target_x = bus_x_input + 1
            target_y = p["y"]
            
            path = grid.find_path((p["x"], p["y"]), (target_x, target_y))
            
            # Converter o path (lista de tiles) em UndergroundPipes se a linha for reta e longa
            if len(path) > 2:
                # Lógica de segmentação: Usar Undergrounds para vãos de até 10 tiles
                first = path[0]
                last = path[-1]
                
                # Se for uma linha reta (X ou Y constante)
                is_straight = all(t[0] == first[0] for t in path) or all(t[1] == first[1] for t in path)
                dist = len(path)
                
                if is_straight and dist <= 11: # 10 + portas
                    # Coloca apenas a entrada e a saída
                    all_pipes.append({
                        "name": "pipe-to-ground",
                        "x": first[0], "y": first[1],
                        "direction": 4 if first[0] < last[0] else 12 # Direção baseada no fluxo
                    })
                    all_pipes.append({
                        "name": "pipe-to-ground",
                        "x": last[0], "y": last[1],
                        "direction": 12 if first[0] < last[0] else 4
                    })
                else:
                    # Se for torto ou muito longo, preenche com canos normais por enquanto
                    for tile in path:
                        all_pipes.append({"name": "pipe", "x": tile[0], "y": tile[1]})

        # Encapsula na resposta final para o Draftsman ler
        return {
            "clusters": layout,
            "inserters": all_inserters,
            "belts": all_belts,
            "pipes": all_pipes,
            "obstacles": grid.obstacles
        }
