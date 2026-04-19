import math
import json
from .solver import RateSolver
from .draftsman_compiler import DraftsmanCompiler
from .ai_bridge import AIBridge
from .translator import ReverseTranslator
from api.schemas import ADAMWorkOrderSchema, MachineRequirement, AIContextSchema

async def execute_generation_pipeline(payload: dict):
    """
    Novo Pipeline Híbrido:
    Passo A: Matemática de Produção (Django)
    Passo B: Ordem de Serviço -> IA (ADAM)
    Passo C: Tradução DSL -> Entidades (ReverseTranslator)
    Passo D: Escalonamento (Tiling) e Compilação Final (Draftsman)
    """
    
    target_item = payload.get("target", "unknown-item")
    rate = payload.get("rate_per_minute", 60)
    tech_tier_data = payload.get("tech_tier", {})
    ai_context_data = payload.get("ai_context", {})
    
    # 1. Passo A: Rate Solver (Cérebro Matemático)
    solver = RateSolver()
    solver.oil_recipe = tech_tier_data.get("oil_recipe", "advanced-oil-processing")
    nodes_requirements = solver.resolve_requirements(
        target_item, 
        rate, 
        machine_name=tech_tier_data.get("machine", "assembling-machine-3"), 
        furnace_name=tech_tier_data.get("furnace", "electric-furnace")
    )

    # Filtramos apenas o nó final para o ADAM (ou poderíamos enviar a árvore toda)
    # Para este MVP, focamos no layout do item alvo.
    target_node = next((n for n in nodes_requirements if n["item"] == target_item), None)
    if not target_node:
        raise ValueError(f"Não foi possível calcular requisitos para {target_item}")

    # 2. Passo B: Formatar Ordem de Serviço e Chamar IA
    work_order = ADAMWorkOrderSchema(
        target_item=target_item,
        total_rate_per_minute=rate,
        requested_machines=[
            MachineRequirement(
                item=target_item, 
                count=target_node["machines_needed"], 
                machine_type=target_node["machine_type"]
            )
        ],
        tech_tier=tech_tier_data,
        context=AIContextSchema(**ai_context_data)
    )

    dsl_response = await AIBridge.call_adam(work_order.model_dump_json(indent=2))
    if not dsl_response:
        raise RuntimeError("A IA ADAM não retornou uma resposta válida.")

    # 3. Passo C: Tradução DSL
    translator = ReverseTranslator()
    entities, metadata = translator.decode_dsl(dsl_response)
    
    if not entities:
        raise RuntimeError("A DSL retornada pela IA não contém entidades válidas.")

    # 4. Passo D: Tiling (Escalabilidade de Bloco)
    # Calculamos quantos blocos da IA precisamos para atingir a meta do Django
    machines_in_block = sum(1 for e in entities if e["name"] == target_node["machine_type"])
    if machines_in_block == 0:
        # Fallback caso a IA use nomes diferentes ou falhe no contador
        machines_in_block = 1 

    num_blocks = math.ceil(target_node["machines_needed"] / machines_in_block)
    
    # Multiplexação Horizontal com Espaço (Gap)
    final_entities = []
    block_width = metadata.get("width", 10)
    gap = 2 # Espaço entre blocos conforme solicitado

    for i in range(num_blocks):
        offset_x = i * (block_width + gap)
        for ent in entities:
            new_ent = json.loads(json.dumps(ent)) # Deep copy
            new_ent["position"]["x"] += offset_x
            final_entities.append(new_ent)

    # 5. Compilação Final (Draftsman)
    compiler = DraftsmanCompiler(label=f"ADAM Block: {target_item} x{num_blocks}")
    # Nota: Refatoramos o compiler para aceitar entidades brutas da DSL
    blueprint_string, entities_map = compiler.generate_from_entities(
        final_entities,
        label=f"FBG-ADAM | {target_item} | {rate}/min"
    )
    
    return blueprint_string, entities_map
