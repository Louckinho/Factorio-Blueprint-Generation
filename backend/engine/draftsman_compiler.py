from draftsman.blueprintable import Blueprint
from draftsman.entity import AssemblingMachine, ConstantCombinator, TransportBelt, Inserter, Pipe, UndergroundPipe, Splitter, UndergroundBelt, ElectricPole
from draftsman.data import entities

class DraftsmanCompiler:
    def __init__(self, label: str):
        self.blueprint = Blueprint()
        self.blueprint.label = label

    def generate_from_entities(self, entities_list: list, label: str = None):
        """
        Gera um blueprint a partir de uma lista simples de entidades.
        Cada entidade deve ser um dict: {"name": str, "x": float, "y": float} OU {"name": str, "position": {"x": float, "y": float}}
        """
        if label:
            self.blueprint.label = label

        for ent_data in entities_list:
            try:
                name = ent_data["name"]
                
                # Extração flexível de posição
                if "position" in ent_data:
                    pos = (ent_data["position"]["x"], ent_data["position"]["y"])
                else:
                    pos = (ent_data.get("x", 0), ent_data.get("y", 0))

                direction = ent_data.get("direction", 0)
                
                if "assembling-machine" in name or "furnace" in name or "oil-refinery" in name or "chemical-plant" in name:
                    ent = AssemblingMachine(name, tile_position=pos, direction=direction)
                    recipe = ent_data.get("recipe")
                    if recipe:
                        try:
                            # Tenta aplicar a receita se o objeto suportar
                            ent.recipe = recipe
                        except:
                            pass
                elif "splitter" in name:
                    ent = Splitter(name, tile_position=pos, direction=direction)
                elif "underground-belt" in name:
                    ent = UndergroundBelt(name, tile_position=pos, direction=direction)
                    ent.io_type = ent_data.get("type") or ent_data.get("io_type") or "input"
                elif "transport-belt" in name:
                    ent = TransportBelt(name, tile_position=pos, direction=direction)
                elif "inserter" in name:
                    ent = Inserter(name, tile_position=pos, direction=direction)
                elif "pipe-to-ground" in name:
                    ent = UndergroundPipe(name, tile_position=pos, direction=direction)
                elif "pipe" in name:
                    ent = Pipe(name, tile_position=pos)
                elif "electric-pole" in name or "substation" in name:
                    ent = ElectricPole(name, tile_position=pos)
                else:
                    from draftsman.entity import Entity
                    ent = Entity(name, tile_position=pos, direction=direction)

                self.blueprint.entities.append(ent)
            except Exception as e:
                print(f"Erro ao adicionar entidade {ent_data.get('name')}: {e}")

        blueprint_dict = self.blueprint.to_dict()
        return self.blueprint.to_string(), blueprint_dict["blueprint"].get("entities", [])

    def generate_blueprint_string(self, layout_data: list, bus_metadata: dict = None, inserters: list = None, belts: list = None, pipes: list = None, poles: list = None, belt_name: str = "transport-belt"):
        """
        Materializa o layout e os barramentos em uma string de Blueprint e retorna também o mapa de entidades.
        """
        self.belt_name = belt_name
        raw_entities = []
        # 1. Adicionar máquinas do layout
        for cluster in layout_data:
            for machine in cluster["machines"]:
                try:
                    # Tenta instanciar a entidade baseada no nome da receita/item
                    # Nota: Mapeamos o nome do item para a máquina padrão se necessário
                    ent_name = machine.get("machine_type", "assembling-machine-3")
                    
                    # Garantir que a entidade existe no banco de dados do jogo
                    if ent_name not in entities.raw:
                        ent_name = "assembling-machine-3"
                        
                    ent = AssemblingMachine(ent_name, tile_position=(machine["abs_x"], machine["abs_y"]))
                    
                    # Definir a Receita. Factorio requer receita explícita para fábricas e refinarias.
                    recipe_name = machine["item"]
                    if recipe_name in ("petroleum-gas", "heavy-oil", "light-oil"):
                        recipe_name = "advanced-oil-processing"
                        
                    try:
                        ent.recipe = recipe_name
                    except:
                        pass # Fornalhas (furnaces), por exemplo, assam o que recebem e não aceitam setar recipe.

                    self.blueprint.entities.append(ent)
                except Exception as e:
                    print(f"Erro ao adicionar máquina {machine['item']}: {e}")

        # 2. Adicionar Barramentos e Combinadores
        if bus_metadata:
            # Input Bus
            in_bus = bus_metadata["input_bus"]
            if in_bus:
                self._add_bus_structures(in_bus, direction="input")
            
            # Output Bus
            out_bus = bus_metadata["output_bus"]
            if out_bus:
                self._add_bus_structures(out_bus, direction="output")
                
        # 3. Adicionar Inserters alocados pelo Pathfinding
        if inserters:
            for ins in inserters:
                try:
                    inserter_entity = Inserter(ins["name"], tile_position=(ins["x"], ins["y"]), direction=ins["direction"])
                    self.blueprint.entities.append(inserter_entity)
                except Exception as e:
                    print(f"Erro Inserter: {e}")
                    
        # 4. Adicionar Esteiras alocadas pelo Pathfinding
        if belts:
            for b in belts:
                try:
                    name = b["name"]
                    if "splitter" in name:
                        ent = Splitter(name, tile_position=(b["x"], b["y"]), direction=b.get("direction", 4))
                    elif "underground-belt" in name:
                        ent = UndergroundBelt(name, tile_position=(b["x"], b["y"]), direction=b.get("direction", 4))
                        ent.io_type = b.get("type", "input")
                    else:
                        ent = TransportBelt(name, tile_position=(b["x"], b["y"]), direction=b.get("direction", 0))
                    self.blueprint.entities.append(ent)
                except Exception as e:
                    print(f"Erro Belt/Splitter: {e}")

        # 5. Adicionar Canos alocados pelo Pathfinding
        if pipes:
            from draftsman.entity import Pipe, UndergroundPipe
            for p in pipes:
                try:
                    name = p["name"]
                    if name == "pipe-to-ground":
                        ent = UndergroundPipe(name, tile_position=(p["x"], p["y"]), direction=p.get("direction", 0))
                    else:
                        ent = Pipe(name, tile_position=(p["x"], p["y"]))
                    self.blueprint.entities.append(ent)
                except Exception as e:
                    print(f"Erro Pipe: {e}")

        # 6. Adicionar Postes de Energia (V4.4)
        if poles:
            for p in poles:
                try:
                    ent = ElectricPole(p["name"], tile_position=(p["x"], p["y"]))
                    self.blueprint.entities.append(ent)
                except Exception as e:
                    print(f"Erro Pole: {e}")

        blueprint_dict = self.blueprint.to_dict()
        return self.blueprint.to_string(), blueprint_dict["blueprint"].get("entities", [])

    def _add_bus_structures(self, bus_info: dict, direction: str):
        """
        Adiciona combinadores e uma linha de cintas para representar o barramento.
        """
        comb_data = bus_info["combinator"]
        comb = ConstantCombinator(tile_position=comb_data["position"])
        
        # Adicionar sinais ao combinador
        for i, signal in enumerate(comb_data["signals"]):
            try:
                # set_signal(index, name, count, type)
                sig_type = signal.get("type", "item")
                comb.set_signal(i, signal["name"], signal["count"])
            except:
                pass
        
        self.blueprint.entities.append(comb)

        # Adicionar uma linha de cintas (visualização do barramento)
        # Força a cinta a apontar para o centro do layout se for input, ou para fora se for output
        b_name = getattr(self, 'belt_name', 'transport-belt')
        for y in range(bus_info["min_y"], bus_info["max_y"] + 3, 3):
            # Apenas um guia visual por enquanto
            belt = TransportBelt(b_name, tile_position=(bus_info["x"], y))
            self.blueprint.entities.append(belt)
