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
    print("\n" + ">>>" * 10)
    print(f"[PIPELINE] INICIANDO GERAÇÃO PARA: {payload.get('target')} ({payload.get('rate_per_minute')}/min)")
    print("<<<" * 10)

    target_item = payload.get("target", "unknown-item")
    rate = payload.get("rate_per_minute", 60)
    tech_tier_data = payload.get("tech_tier", {})
    
    belt_name = tech_tier_data.get("belt", "transport-belt")
    belt_capacity_per_sec = get_belt_capacity(belt_name)
    
    print(f"[STEP 1] Resolvendo matemática de produção...")
    solver = RateSolver()
    solver.oil_recipe = tech_tier_data.get("oil_recipe", "advanced-oil-processing")
    nodes_requirements = solver.resolve_requirements(
        target_item, 
        rate, 
        machine_name=tech_tier_data.get("machine", "assembling-machine-3"), 
        furnace_name=tech_tier_data.get("furnace", "electric-furnace")
    )

    print(f"[MATEMÁTICA] Itens necessários para {target_item}:")
    for n in nodes_requirements:
        print(f"  - {n['item']}: {n['machines_needed']:.2f} máquinas | {n['rate_per_sec']:.2f} itens/seg")

    production_nodes = [n for n in nodes_requirements if not n["is_raw_input"]]
    
    if not production_nodes:
        print("[ERRO] Nenhum nó de produção encontrado!")
        raise ValueError(f"Não foi possível calcular requisitos de produção para {target_item}")

    translator = ReverseTranslator()
    assembler = BlockAssembler()
    modules_data = []

    print(f"\n[STEP 2] Chamando IA ADAM para {len(production_nodes)} módulos...")
    for node in production_nodes:
        item = node["item"]
        total_machines = math.ceil(node["machines_needed"])
        rate_sec = node["rate_per_sec"]
        machine_type = node["machine_type"]
        
        capacity = 1200.0 if node.get("is_fluid") else belt_capacity_per_sec
        saturated_belts = math.ceil(rate_sec / capacity) if rate_sec > 0 else 1
        machines_per_block = math.ceil(total_machines / saturated_belts) if saturated_belts > 0 else total_machines
        
        MAX_AI_MACHINES = 48
        if machines_per_block > MAX_AI_MACHINES:
            machines_per_block = MAX_AI_MACHINES
            saturated_belts = math.ceil(total_machines / MAX_AI_MACHINES)

        tier = machine_type[-1] if machine_type[-1].isdigit() else 1
            
        # Voltando ao prompt ULTRA-LIMPO (Igual ao Treino)
        work_order = f"Generate: [item={item}|machine={machine_type}|count={machines_per_block}|tier={tier}]"
        print(f"  > Ordem de Serviço: {work_order}")
        
        dsl_response = await AIBridge.call_adam(work_order)
        if not dsl_response:
            print(f"  [AVISO] ADAM falhou para {item}")
            continue
            
        print(f"  [IA] Resposta DSL recebida ({len(dsl_response)} chars)")
        print(f"  [RAW DSL]\n{dsl_response}\n[END RAW DSL]")
        entities, metadata = translator.decode_dsl(dsl_response)
        
        if entities:
            print(f"  [OK] Traduzido: {len(entities)} entidades encontradas.")
            modules_data.append({
                "item": item,
                "entities": entities,
                "num_chunks": saturated_belts,
                "metadata": metadata
            })

    print(f"\n[STEP 3] Montando Main Bus com {len(modules_data)} módulos...")
    final_entities = assembler.assemble(modules_data)
    print(f"  - Total final de entidades: {len(final_entities)}")

    print(f"[STEP 4] Compilando Blueprint String...")
    compiler = DraftsmanCompiler(label=f"ADAM Factory: {target_item}")
    blueprint_string, entities_map = compiler.generate_from_entities(
        final_entities,
        label=f"FBG-ADAM | {target_item} | {rate}/min"
    )
    
    print(">>> GERAÇÃO FINALIZADA COM SUCESSO <<<\n")
    return blueprint_string, entities_map
