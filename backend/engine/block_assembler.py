import json

class BlockAssembler:
    """
    Construtor Espacial (O Arquiteto do Main Bus).
    Recebe os blocos perfeitos (saturados) desenhados pela IA e os multiplica
    pelo número de chunks necessários, criando o barramento principal (Main Bus).
    """

    def __init__(self, gap_x=4, gap_y=10):
        self.gap_x = gap_x  # Espaço horizontal entre blocos idênticos (para esteiras verticais)
        self.gap_y = gap_y  # Espaço vertical entre etapas de produção (para o Main Bus horizontal)

    def assemble(self, modules_data: list) -> list:
        """
        modules_data deve ser uma lista de dicionários no formato:
        [
            {
                "item": "iron-plate",
                "entities": [...],       # Entidades de UM bloco
                "num_chunks": 8,         # Quantos blocos iguais precisamos
                "metadata": {"width": 10, "height": 15}
            },
            ...
        ]
        """
        final_entities = []
        current_y = 0
        
        for module in modules_data:
            entities = module.get("entities", [])
            num_chunks = module.get("num_chunks", 1)
            meta = module.get("metadata", {"width": 20, "height": 20})
            
            w = meta.get("width", 20)
            h = meta.get("height", 20)
            
            # Carimba (Tile) o bloco horizontalmente 'num_chunks' vezes
            for i in range(num_chunks):
                offset_x = i * (w + self.gap_x)
                offset_y = current_y
                
                for ent in entities:
                    new_ent = json.loads(json.dumps(ent)) # Deep copy rápido
                    new_ent["position"]["x"] += offset_x
                    new_ent["position"]["y"] += offset_y
                    final_entities.append(new_ent)
                    
            # Avança o cursor Y para a próxima etapa da cadeia de produção
            current_y += h + self.gap_y
            
        return final_entities
