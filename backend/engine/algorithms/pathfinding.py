import heapq
import collections

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
        return (x, y) in self.obstacles or x < -15 or y < -15 or x > self.max_x or y > self.max_y

class AStarRouter:
    @staticmethod
    def route_belts(layout: list):
        """
        Recebe o layout absoluto das máquinas, aplica Inserters ao redor delas e 
        roteia os cinturões utilizando A* da origem (Barramento) até o destino (Inserter).
        """
        # 1. Definir os limites do nosso Universo Virtual para a Malha A*
        if not layout: return layout
        
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
        
        # 4. Roteamento A* (A-Star) Simples (Stub Avançado)
        # Aqui, no pipeline final, ligaríamos o Input_Bus até a coordenada do input_ix.
        # Por enquanto vamos forçar esteiras simuladas para provar o sistema.
        for ins in all_inserters:
            # Traçar uma cordinha de belts atrás do inserter
            b_x = ins["x"] + 1 if ins["direction"] == 4 else ins["x"] - 1
            if not grid.is_blocked(b_x, ins["y"]):
                all_belts.append({
                    "name": "express-transport-belt",
                    "x": b_x, "y": ins["y"],
                    "direction": 0 # Apontando pro norte
                })

        # Encapsula na resposta final para o Draftsman ler
        return {
            "clusters": layout,
            "inserters": all_inserters,
            "belts": all_belts
        }
