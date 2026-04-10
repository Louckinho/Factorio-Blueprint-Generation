from draftsman.blueprintable import Blueprint
from draftsman.entity import AssemblingMachine

class DraftsmanCompiler:
    def __init__(self, label: str):
        self.blueprint = Blueprint()
        self.blueprint.label = label

    def generate_blueprint_string(self, layout_data: list) -> str:
        """
        Recebe a lista de dados processada pelas camadas anteriores
        (Bin Packing, Pathfinding, Overlays) e materializa usando draftsman.
        """
        # --- STUB ---
        # Exemplo Simulado de Entidade Padrão
        machine = AssemblingMachine("assembling-machine-3", tile_position=(0, 0))
        self.blueprint.entities.append(machine)
        
        return self.blueprint.to_string()
