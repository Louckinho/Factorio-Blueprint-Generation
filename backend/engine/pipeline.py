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

def execute_generation_pipeline(payload: dict) -> str:
    """
    Executa rigorosamente o Pipeline de Geração (Separation of Concerns).
    A saída de um passo é a entrada do próximo.
    """
    
    target_item = payload.get("target", "unknown-item")
    rate = payload.get("rate_per_minute", 60)
    
    # 1. Rate Solver (Carrega automaticamente receitas nativas do banco do draftsman)
    solver = RateSolver()
    nodes_requirements = solver.resolve_requirements(target_item, rate)
    
    # 2. Clustering (Agrupamento Otimizado)
    clusters = Clusterizer.group(nodes_requirements)
    
    # 3. Bin Packing (Geometria 2D MaxRects)
    layout = MaxRectsPacker(width=100, height=100).pack(clusters)

    # 4. Bus Designer & Lane Mapper
    bus_metadata = BusDesigner.attach_buses(layout, nodes_requirements)
    mapped_lanes = LaneMapper.multiplex_lanes(layout) # Por enquanto opera no layout original

    # 5. Pathfinding (Roteamento de Esteiras A*)
    routed_layout = AStarRouter.route_belts(mapped_lanes)

    # 6. Overlays (Postes, Fluidos, Sinalizadores)
    # Por enquanto as Overlays batem diretamente na array de clusters
    routed_layout["clusters"] = ElectricalOverlay.apply(routed_layout["clusters"])
    routed_layout["clusters"] = FluidsOverlay.apply(routed_layout["clusters"])
    routed_layout["clusters"] = BeaconsOverlay.apply(routed_layout["clusters"])

    # 7. Draftsman Compiler (Gerador Final de Blueprint String)
    compiler = DraftsmanCompiler(label=f"FBG High-Density {target_item} {rate}/min - v4.0")
    blueprint_string = compiler.generate_blueprint_string(
        layout_data=routed_layout["clusters"], 
        bus_metadata=bus_metadata,
        inserters=routed_layout.get("inserters", []),
        belts=routed_layout.get("belts", [])
    )
    
    return blueprint_string
