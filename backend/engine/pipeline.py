import math
import json
from .solver import RateSolver
from .draftsman_compiler import DraftsmanCompiler
from .ai_bridge import AIBridge
from .translator import ReverseTranslator
from .block_assembler import BlockAssembler

def get_belt_capacity(belt_name: str) -> float:
    """Retorna a capacidade de itens/seg da esteira"""
    if "express" in belt_name: return 45.0
    if "fast" in belt_name: return 30.0
    return 15.0

async def execute_generation_pipeline(payload: dict):
    """
    Novo Pipeline Híbrido:
    Passo A: Matemática de Produção e Saturação (Django)
    Passo B: Ordem de Serviço Modular -> IA (ADAM)
    Passo C: Montagem do Main Bus (BlockAssembler)
    Passo D: Compilação Final (Draftsman)
    """
    target_item = payload.get("target", "unknown-item")
    rate = payload.get("rate_per_minute", 60)
    tech_tier_data = payload.get("tech_tier", {})
    
    belt_name = tech_tier_data.get("belt", "transport-belt")
    belt_capacity_per_sec = get_belt_capacity(belt_name)
    
    # 1. Passo A: Rate Solver (Cérebro Matemático)
    solver = RateSolver()
    solver.oil_recipe = tech_tier_data.get("oil_recipe", "advanced-oil-processing")
    nodes_requirements = solver.resolve_requirements(
        target_item, 
        rate, 
        machine_name=tech_tier_data.get("machine", "assembling-machine-3"), 
        furnace_name=tech_tier_data.get("furnace", "electric-furnace")
    )

    # Filtrar apenas nós de produção (que precisam de máquinas)
    production_nodes = [n for n in nodes_requirements if not n["is_raw_input"]]
    
    if not production_nodes:
        raise ValueError(f"Não foi possível calcular requisitos de produção para {target_item}")

    translator = ReverseTranslator()
    assembler = BlockAssembler()
    modules_data = []

    # 2. Chunking por Saturação de Esteira (Para cada nó da árvore)
    for node in production_nodes:
        item = node["item"]
        total_machines = math.ceil(node["machines_needed"])
        rate_sec = node["rate_per_sec"]
        machine_type = node["machine_type"]
        
        # Se for fluido, a capacidade do cano é enorme, não quebra por saturação de esteira
        capacity = 1200.0 if node.get("is_fluid") else belt_capacity_per_sec
        saturated_belts = math.ceil(rate_sec / capacity) if rate_sec > 0 else 1
        
        machines_per_block = math.ceil(total_machines / saturated_belts) if saturated_belts > 0 else total_machines
        
        # Clamp ao limite de segurança da IA (MAX_AI_MACHINES)
        MAX_AI_MACHINES = 48
        if machines_per_block > MAX_AI_MACHINES:
            machines_per_block = MAX_AI_MACHINES
            saturated_belts = math.ceil(total_machines / MAX_AI_MACHINES)

        if machines_per_block <= 0:
            continue
            
        tier = 1
        if machine_type[-1].isdigit():
            tier = machine_type[-1]
            
        # Work order exata que a IA aprendeu no Treinamento
        work_order = f"Generate: [item={item}|machine={machine_type}|count={machines_per_block}|tier={tier}]"
        
        # Chama a IA para desenhar APENAS UM bloco saturado
        dsl_response = await AIBridge.call_adam(work_order)
        if not dsl_response:
            print(f"[AVISO] IA falhou ao gerar {item}")
            continue
            
        entities, metadata = translator.decode_dsl(dsl_response)
        
        if entities:
            modules_data.append({
                "item": item,
                "entities": entities,
                "num_chunks": saturated_belts,
                "metadata": metadata
            })

    if not modules_data:
        raise RuntimeError("Falha total na geração da fábrica. Nenhum módulo válido foi criado.")

    # 3. Montagem do Main Bus (Tiling)
    final_entities = assembler.assemble(modules_data)

    # 4. Compilação (Draftsman)
    compiler = DraftsmanCompiler(label=f"ADAM Factory: {target_item}")
    blueprint_string, entities_map = compiler.generate_from_entities(
        final_entities,
        label=f"FBG-ADAM | {target_item} | {rate}/min"
    )
    
    return blueprint_string, entities_map
