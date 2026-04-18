import json
import os
import networkx as nx
import math
from draftsman.data import recipes, entities

class RateSolver:
    def __init__(self):
        # A Biblioteca factorio-draftsman possui TODAS as centenas de receitas puras do Vanilla internamente.
        self.recipe_data = recipes.raw
        self.graph = nx.DiGraph()

    def resolve_requirements(self, target_item: str, rate_per_minute: float, machine_name: str = "assembling-machine-3", furnace_name: str = "electric-furnace"):
        """
        Calcula a quantidade exata de ingredientes e máquinas necessárias subindo a árvore com DFS.
        """
        self.default_assembler = machine_name
        self.default_furnace = furnace_name
        
        # Convert rate to per second
        rate_per_sec = rate_per_minute / 60.0
        
        # Iniciar recursão
        self._traverse_recipe(target_item, rate_per_sec)

        # Extrair os nós ordenados por topologia estrutural (Input -> Furnaces -> Assemblers)
        nodes = []
        try:
            topo_nodes = list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            # Em caso de ciclo, fallback
            topo_nodes = list(self.graph.nodes())
            
        for item_name in topo_nodes:
            data = self.graph.nodes[item_name]
            nodes.append({
                "item": item_name,
                "machines_needed": data.get("machines", 0.0),
                "is_raw_input": data.get("is_raw", False),
                "is_fluid": data.get("is_fluid", False),
                "rate_per_sec": data.get("rate", 0.0),
                "machine_type": data.get("machine_type", self.default_assembler)
            })

        return nodes

    def _get_machine_for_category(self, category: str) -> str:
        if "chemistry" in category:
            return "chemical-plant"
        elif "oil" in category:
            return "oil-refinery"
        elif "smelting" in category or category == "metallurgy":
            return getattr(self, "default_furnace", "electric-furnace")
        elif "centrifuging" in category:
            return "centrifuge"
        else:
            return getattr(self, "default_assembler", "assembling-machine-3")

    def _traverse_recipe(self, item_name: str, required_rate_per_sec: float, current_path: set = None):
        if current_path is None:
            current_path = set()

        if item_name in current_path:
            raise ValueError(f"Ciclo infinito detectado na receita para: {item_name}")
            
        current_path.add(item_name)

        recipe_key = item_name
        # Mapeamento para fluidos resultantes de refinamento
        if recipe_key in ("petroleum-gas", "heavy-oil", "light-oil"):
            recipe_key = getattr(self, "oil_recipe", "advanced-oil-processing")

        if recipe_key not in self.recipe_data:
            # É um ore cru, fluido base ou item não craftavel (Input Bus)
            if self.graph.has_node(item_name) and 'rate' in self.graph.nodes[item_name]:
                self.graph.nodes[item_name]['rate'] += required_rate_per_sec
            else:
                # Como saber se o insumo básico é fluido se não tem receita dele?
                # No Factorio, itens crus básicos como 'water' ou 'crude-oil' são fluidos.
                # Podemos conferir no banco de dados de 'items' ou 'fluids' do draftsman
                is_fluid = False 
                # (Simplificação: se estiver na lista de fluidos do draftsman)
                from draftsman.data import fluids
                if item_name in fluids.raw:
                    is_fluid = True

                self.graph.add_node(item_name, machines=0, is_raw=True, rate=required_rate_per_sec, is_fluid=is_fluid)
            current_path.remove(item_name)
            return

        recipe = self.recipe_data[recipe_key]
        
        # Encontra output amount do item alvo
        output_amount = 1.0 # Default fallback
        if "results" in recipe:
            for res in recipe["results"]:
                if res["name"] == item_name:
                    output_amount = res["amount"]
                    break

        category = recipe.get("category", "crafting")
        machine_type = self._get_machine_for_category(category)
        
        crafting_speed = 1.0 # Default factorio
        if machine_type in entities.raw:
            crafting_speed = entities.raw[machine_type].get("crafting_speed", 1.0)
            
        energy_required = recipe.get("energy_required", 1.0)
        
        # Taxa de base de 1 máquina
        items_per_sec_per_machine = (output_amount / energy_required) * crafting_speed
        machines_exact = required_rate_per_sec / items_per_sec_per_machine

        # Atualiza Grafo
        is_fluid = False
        if "results" in recipe:
            for res in recipe["results"]:
                if res["name"] == item_name and res.get("type") == "fluid":
                    is_fluid = True
                    break

        if self.graph.has_node(item_name) and 'rate' in self.graph.nodes[item_name]:
            self.graph.nodes[item_name]['rate'] += required_rate_per_sec
            self.graph.nodes[item_name]['machines'] += machines_exact
            self.graph.nodes[item_name]['is_raw'] = False
            self.graph.nodes[item_name]['is_fluid'] = is_fluid
            self.graph.nodes[item_name]['machine_type'] = machine_type
        else:
            self.graph.add_node(item_name, machines=machines_exact, is_raw=False, rate=required_rate_per_sec, is_fluid=is_fluid, machine_type=machine_type)

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
            self._traverse_recipe(ing_name, ing_rate_per_sec, current_path)

        current_path.remove(item_name)
