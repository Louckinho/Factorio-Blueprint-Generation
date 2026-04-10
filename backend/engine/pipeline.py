from .solver import RateSolver
from .draftsman_compiler import DraftsmanCompiler
from .clustering import Clusterizer
from .algorithms.bin_packing import MaxRectsPacker
from .algorithms.pathfinding import AStarRouter
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
    
    # 1. Rate Solver (Carrega automaticamente receitas nativas do banco do draftsman)
    solver = RateSolver()
    nodes_requirements = solver.resolve_requirements(target_item, rate, machine_name=machine_name)
    
    # 2. Clustering (Agrupamento Otimizado com Cálculo de Saturação)
    belt_name = tech_tier.get("belt", "express-transport-belt")
    clusters = Clusterizer.group(nodes_requirements, machine_name=machine_name, belt_name=belt_name)
    
    # 3. Bin Packing (Geometria 2D MaxRects)
    layout = MaxRectsPacker(width=100, height=100).pack(clusters)

    # 4. Bus Designer & Lane Mapper
    bus_metadata = BusDesigner.attach_buses(layout, nodes_requirements)
    mapped_lanes = LaneMapper.multiplex_lanes(layout) # Por enquanto opera no layout original

    # 5. Pathfinding (Roteamento de Esteiras A*)
    routed_layout = AStarRouter.route_belts(mapped_lanes)

    # 6. Overlays (Postes, Fluidos, Sinalizadores)
    pole_tier = tech_tier.get("pole", "medium-electric-pole")
    all_poles = ElectricalOverlay.apply(
        routed_layout["clusters"], 
        routed_layout.get("obstacles", set()), 
        extra_consumers=routed_layout.get("inserters", []), # Inclui os braços aqui
        pole_type=pole_tier
    )
    
    # Por enquanto as Overlays batem diretamente na array de clusters
    routed_layout["clusters"] = FluidsOverlay.apply(routed_layout["clusters"])
    routed_layout["clusters"] = BeaconsOverlay.apply(routed_layout["clusters"])
    
    # 7. Draftsman Compiler (Gerador Final de Blueprint String)
    compiler = DraftsmanCompiler(label=f"FBG High-Density {target_item} {rate}/min - v4.0")
    blueprint_string, entities = compiler.generate_blueprint_string(
        layout_data=routed_layout["clusters"], 
        bus_metadata=bus_metadata,
        inserters=routed_layout.get("inserters", []),
        belts=routed_layout.get("belts", []),
        pipes=routed_layout.get("pipes", []),
        poles=all_poles
    )
    
    return blueprint_string, entities
