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
        return (x, y) in self.obstacles or x < -20 or y < -20 or x > self.max_x or y > self.max_y

    def find_path(self, start, end, turn_penalty=5):
        """
        Algoritmo A* com penalidade de curvas para caminhos mais limpos.
        """
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        close_set = set()
        came_from = {}
        gscore = {start: 0}
        fscore = {start: self.heuristic(start, end)}
        directions = {start: (0, 0)} # Direção que chegou no nó
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
                
                if self.is_blocked(neighbor[0], neighbor[1]):
                    continue
                
                # Calcular custo do movimento
                move_dir = (i, j)
                prev_dir = directions.get(current, (0, 0))
                
                # Se mudou de direção e não é o primeiro passo, aplica penalidade
                penalty = 0
                if prev_dir != (0, 0) and move_dir != prev_dir:
                    penalty = turn_penalty
                
                tentative_g_score = gscore[current] + 1 + penalty
                
                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, float('inf')):
                    continue
                    
                if tentative_g_score < gscore.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    directions[neighbor] = move_dir
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + self.heuristic(neighbor, end)
                    heapq.heappush(oheap, (fscore[neighbor], neighbor))
                    
        return []

    def heuristic(self, a, b):
        # Manhattan distance
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
