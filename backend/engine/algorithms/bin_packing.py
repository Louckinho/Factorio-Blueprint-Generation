import math

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def overlaps(self, other):
        return not (self.x >= other.x + other.w or self.x + self.w <= other.x or
                    self.y >= other.y + other.h or self.y + self.h <= other.y)

class MaxRectsPacker:
    # A margem é vital no Factorio. Precisamos de corredores para as esteiras (Bus e lanes) passarem via AStar.
    MARGIN = 5 

    def __init__(self, width: int = 200, height: int = 200):
        # A malha virtual para alocar o City Block. 200x200 é espaçoso para Megabases medias.
        self.bin_width = width
        self.bin_height = height
        self.free_rectangles = [Rect(0, 0, width, height)]

    def pack(self, clusters: list):
        """
        Heurística 2D Bin Packing - Bottom Left Rule (MaxRects).
        Retorna o layout final com as Posições ABSOLUTAS das máquinas preenchidas.
        """
        # Ordenamos iterativamente pelos maiores blocos primeiro (Area descendente)
        clusters.sort(key=lambda c: (c["width"] + self.MARGIN) * (c["height"] + self.MARGIN), reverse=True)

        layout = []

        for cluster in clusters:
            pack_w = cluster["width"] + self.MARGIN
            pack_h = cluster["height"] + self.MARGIN
            
            best_node = Rect(0, 0, 0, 0)
            best_y = float('inf')
            best_x = float('inf')
            best_free_index = -1
            
            # Encontra o melhor nó livre usando a regra Bottom-Left
            for i, free_rect in enumerate(self.free_rectangles):
                if free_rect.w >= pack_w and free_rect.h >= pack_h:
                    if free_rect.y < best_y or (free_rect.y == best_y and free_rect.x < best_x):
                        best_node.x = free_rect.x
                        best_node.y = free_rect.y
                        best_node.w = pack_w
                        best_node.h = pack_h
                        best_y = free_rect.y
                        best_x = free_rect.x
                        best_free_index = i

            if best_free_index == -1:
                raise Exception("Overflow do Bin Packing! Não há espaço matemático nas dimensões da malha informada.")
            
            # Aplica o Absoluto para o Cluster
            abs_x = best_node.x
            abs_y = best_node.y
            
            cluster["abs_x"] = abs_x
            cluster["abs_y"] = abs_y

            # Traduz as posições das máquinas internas relativas para Absolutas
            for machine in cluster["machines"]:
                machine["abs_x"] = abs_x + machine["rel_x"]
                machine["abs_y"] = abs_y + machine["rel_y"]

            layout.append(cluster)
            
            # Subdivide o espaço de vida MaxRects
            self._split_free_rectangles(best_node)

        return layout

    def _split_free_rectangles(self, placed_rect: Rect):
        new_free = []
        for free_rect in self.free_rectangles:
            if not placed_rect.overlaps(free_rect):
                new_free.append(free_rect)
                continue

            # Se houver overlap térmico, divide nas 4 direções
            if placed_rect.x > free_rect.x:
                new_free.append(Rect(free_rect.x, free_rect.y, placed_rect.x - free_rect.x, free_rect.h))
            if placed_rect.x + placed_rect.w < free_rect.x + free_rect.w:
                new_free.append(Rect(placed_rect.x + placed_rect.w, free_rect.y, free_rect.x + free_rect.w - (placed_rect.x + placed_rect.w), free_rect.h))
            if placed_rect.y > free_rect.y:
                new_free.append(Rect(free_rect.x, free_rect.y, free_rect.w, placed_rect.y - free_rect.y))
            if placed_rect.y + placed_rect.h < free_rect.y + free_rect.h:
                new_free.append(Rect(free_rect.x, placed_rect.y + placed_rect.h, free_rect.w, free_rect.y + free_rect.h - (placed_rect.y + placed_rect.h)))

        # Prune: Remove sub-retângulos que estão completamente dentro de outros
        pruned_free = []
        for i, r1 in enumerate(new_free):
            is_sub_rect = False
            for j, r2 in enumerate(new_free):
                if i != j and (r1.x >= r2.x and r1.y >= r2.y and r1.x + r1.w <= r2.x + r2.w and r1.y + r1.h <= r2.y + r2.h):
                    is_sub_rect = True
                    break
            if not is_sub_rect:
                pruned_free.append(r1)
                
        self.free_rectangles = pruned_free
