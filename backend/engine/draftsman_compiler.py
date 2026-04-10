from draftsman.blueprintable import Blueprint
from draftsman.entity import AssemblingMachine, ConstantCombinator, TransportBelt
from draftsman.data import entities

class DraftsmanCompiler:
    def __init__(self, label: str):
        self.blueprint = Blueprint()
        self.blueprint.label = label

    def generate_blueprint_string(self, layout_data: list, bus_metadata: dict = None, inserters: list = None, belts: list = None) -> str:
        """
        Materializa o layout e os barramentos em uma string de Blueprint.
        """
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
            from draftsman.entity import Inserter
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
                    belt_entity = TransportBelt(b["name"], tile_position=(b["x"], b["y"]), direction=b.get("direction", 0))
                    self.blueprint.entities.append(belt_entity)
                except Exception as e:
                    print(f"Erro Belt: {e}")

        return self.blueprint.to_string()

    def _add_bus_structures(self, bus_info: dict, direction: str):
        """
        Adiciona combinadores e uma linha de cintas para representar o barramento.
        """
        comb_data = bus_info["combinator"]
        comb = ConstantCombinator(tile_position=comb_data["position"])
        
        # Adicionar sinais ao combinador
        for i, signal in enumerate(comb_data["signals"]):
            try:
                # Na versão 3.x do Draftsman (Factorio 2.0), usamos set_signal
                comb.set_signal(i, signal["name"], signal["count"])
            except:
                pass
        
        self.blueprint.entities.append(comb)

        # Adicionar uma linha de cintas (visualização do barramento)
        # Força a cinta a apontar para o centro do layout se for input, ou para fora se for output
        belt_name = "express-transport-belt"
        for y in range(bus_info["min_y"], bus_info["max_y"] + 3, 3):
            # Apenas um guia visual por enquanto
            belt = TransportBelt(belt_name, tile_position=(bus_info["x"], y))
            self.blueprint.entities.append(belt)
