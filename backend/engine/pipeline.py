from .solver import RateSolver
from .draftsman_compiler import DraftsmanCompiler
from .clustering import Clusterizer
from .algorithms.bin_packing import MaxRectsPacker
from .algorithms.routers.belt_router import BeltRouter
from .algorithms.routers.pipe_router import PipeRouter
from .bus_designer import BusDesigner
from .lane_mapper import LaneMapper
from .overlays.electrical import ElectricalOverlay
from .overlays.fluids import FluidsOverlay
from .overlays.beacons import BeaconsOverlay

def execute_generation_pipeline(payload: dict):
    """
    Executa rigorosamente o Pipeline de Geração (Separation of Concerns).
    A saída de um passo é a entrada do próximo.
    """
    
    target_item = payload.get("target", "unknown-item")
    rate = payload.get("rate_per_minute", 60)
    tech_tier = payload.get("tech_tier", {})
    machine_name = tech_tier.get("machine", "assembling-machine-3")
    furnace_name = tech_tier.get("furnace", "electric-furnace")
    
    # 1. Rate Solver (Carrega automaticamente receitas nativas do banco do draftsman)
    solver = RateSolver()
    solver.oil_recipe = tech_tier.get("oil_recipe", "advanced-oil-processing")
    nodes_requirements = solver.resolve_requirements(target_item, rate, machine_name=machine_name, furnace_name=furnace_name)
    
    # 2. Clustering (Agrupamento Otimizado com Cálculo de Saturação)
    belt_name = tech_tier.get("belt", "express-transport-belt")
    # Nota: O Clusterizer usa o machine_name padrão se o nó não especificar um tipo.
    # Como o RateSolver já atribuiu o tipo de máquina correto ao nó, o Clusterizer respeitará isso.
    clusters = Clusterizer.group(nodes_requirements, machine_name=machine_name, belt_name=belt_name)
    
    # 3. Bin Packing (Geometria 2D MaxRects)
    layout = MaxRectsPacker(width=100, height=100).pack(clusters)

    # 4. Bus Designer & Lane Mapper
    bus_metadata = BusDesigner.attach_buses(layout, nodes_requirements)
    mapped_lanes = LaneMapper.multiplex_lanes(layout) # Por enquanto opera no layout original

    # 5. Roteamento de Esteiras
    inserter_name = tech_tier.get("inserter", "fast-inserter")
    belt_data = BeltRouter.route(mapped_lanes, belt_name=belt_name, inserter_name=inserter_name)
    
    # 6. Roteamento de Canos (Fluid Routing)
    pipe_data = PipeRouter.route(mapped_lanes, belt_data.get("obstacles", set()))

    # 7. Overlays (Postes, Sinalizadores)
    pole_tier = tech_tier.get("pole", "medium-electric-pole")
    all_poles = ElectricalOverlay.apply(
        mapped_lanes, 
        belt_data.get("obstacles", set()), 
        extra_consumers=belt_data.get("inserters", []), 
        pole_type=pole_tier
    )
    
    # Beacons Overlay
    routed_layout = BeaconsOverlay.apply(mapped_lanes)
    
    # 8. Draftsman Compiler (Gerador Final de Blueprint String)
    compiler = DraftsmanCompiler(label=f"FBG High-Density {target_item} {rate}/min - v5.0")
    blueprint_string, entities = compiler.generate_blueprint_string(
        layout_data=routed_layout, 
        bus_metadata=bus_metadata,
        inserters=belt_data.get("inserters", []),
        belts=belt_data.get("belts", []),
        pipes=pipe_data.get("pipes", []),
        poles=all_poles,
        belt_name=belt_name
    )
    
    return blueprint_string, entities
