import json
import os
import networkx as nx
import math
from draftsman.data import recipes

class RateSolver:
    def __init__(self):
        # A Biblioteca factorio-draftsman possui TODAS as centenas de receitas puras do Vanilla internamente.
        self.recipe_data = recipes.raw
        self.graph = nx.DiGraph()

    def resolve_requirements(self, target_item: str, rate_per_minute: float, default_crafting_speed: float = 1.25):
        """
        Calcula a quantidade exata de ingredientes e máquinas necessárias subindo a árvore com DFS.
        default_crafting_speed: 1.25 (Assembling Machine 3)
        """
        # Convert rate to per second
        rate_per_sec = rate_per_minute / 60.0
        
        # Iniciar recursão
        self._traverse_recipe(target_item, rate_per_sec, default_crafting_speed)

        # Extrair os nós ordenados (opcionalmente sort topológico, embora Graph já tenha estrutura)
        nodes = []
        for node in self.graph.nodes(data=True):
            item_name = node[0]
            data = node[1]
            nodes.append({
                "item": item_name,
                "machines_needed": data.get("machines", 0.0),
                "is_raw_input": data.get("is_raw", False),
                "rate_per_sec": data.get("rate", 0.0)
            })

        return nodes

    def _traverse_recipe(self, item_name: str, required_rate_per_sec: float, crafting_speed: float, current_path: set = None):
        if current_path is None:
            current_path = set()

        if item_name in current_path:
            raise ValueError(f"Ciclo infinito detectado na receita para: {item_name}")
            
        current_path.add(item_name)

        if item_name not in self.recipe_data:
            # É um ore cru, fluido base ou item não craftavel (Input Bus)
            if self.graph.has_node(item_name) and 'rate' in self.graph.nodes[item_name]:
                self.graph.nodes[item_name]['rate'] += required_rate_per_sec
            else:
                self.graph.add_node(item_name, machines=0, is_raw=True, rate=required_rate_per_sec)
            current_path.remove(item_name)
            return

        recipe = self.recipe_data[item_name]
        
        # Encontra output amount do item alvo
        output_amount = 1.0 # Default fallback
        if "results" in recipe:
            for res in recipe["results"]:
                if res["name"] == item_name:
                    output_amount = res["amount"]
                    break

        energy_required = recipe.get("energy_required", 1.0)
        
        # Taxa de base de 1 máquina
        items_per_sec_per_machine = (output_amount / energy_required) * crafting_speed
        machines_exact = required_rate_per_sec / items_per_sec_per_machine

        # Atualiza Grafo
        if self.graph.has_node(item_name) and 'rate' in self.graph.nodes[item_name]:
            self.graph.nodes[item_name]['rate'] += required_rate_per_sec
            self.graph.nodes[item_name]['machines'] += machines_exact
            self.graph.nodes[item_name]['is_raw'] = False
        else:
            self.graph.add_node(item_name, machines=machines_exact, is_raw=False, rate=required_rate_per_sec)

        # Traverse ingredientes
        for ingredient in recipe.get("ingredients", []):
            ing_name = ingredient["name"]
            ing_amount_per_recipe = ingredient["amount"]
            
            # Quanta receita(ciclos) rodamos por segundo para bater nossa meta?
            recipes_per_sec = required_rate_per_sec / output_amount
            ing_rate_per_sec = recipes_per_sec * ing_amount_per_recipe

            # Adiciona Aresta (Edge)
            self.graph.add_edge(ing_name, item_name, weight=ing_rate_per_sec)

            # Recursão descendente
            self._traverse_recipe(ing_name, ing_rate_per_sec, crafting_speed, current_path)

        current_path.remove(item_name)
