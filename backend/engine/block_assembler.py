import json

class BlockAssembler:
    """
    Construtor Espacial (O Arquiteto do Main Bus).
    Recebe os blocos perfeitos (saturados) desenhados pela IA e os multiplica
    pelo número de chunks necessários, criando o barramento principal (Main Bus).
    """

    def __init__(self, gap_x=2, gap_y=4):
        self.gap_x = gap_x 
        self.gap_y = gap_y 

    def assemble(self, modules_data: list) -> list:
        final_entities = []
        current_y = 0
        
        for module in modules_data:
            entities = module.get("entities", [])
            if not entities: continue
            
            num_chunks = module.get("num_chunks", 1)
            meta = module.get("metadata", {})
            
            # Se a IA nao informou o tamanho, calculamos o tamanho REAL baseado nas entidades
            min_x = min(e["position"]["x"] for e in entities)
            max_x = max(e["position"]["x"] for e in entities)
            min_y = min(e["position"]["y"] for e in entities)
            max_y = max(e["position"]["y"] for e in entities)
            
            # Tamanho real (com margem de seguranca de 2 tiles)
            w = meta.get("width") or (max_x - min_x + 2)
            h = meta.get("height") or (max_y - min_y + 2)
            
            print(f"[ASSEMBLER] Modulo {module.get('item')}: Tamanho calculado {w}x{h}")
            
            for i in range(num_chunks):
                offset_x = i * (w + self.gap_x)
                offset_y = current_y
                
                for ent in entities:
                    new_ent = json.loads(json.dumps(ent)) 
                    new_ent["position"]["x"] += offset_x
                    new_ent["position"]["y"] += offset_y
                    final_entities.append(new_ent)
                    
            current_y += h + self.gap_y
            
        return final_entities
