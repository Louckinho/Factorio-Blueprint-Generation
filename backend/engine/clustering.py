import math

class Clusterizer:
    # Máquinas padrões fatoradas (Asssembling Machine é 3x3)
    ENTITY_SIZE = 3 

    @staticmethod
    def group(nodes_requirements: list):
        """
        Analisa a lista de máquinas requiridas e as agrupa (Clusters).
        Retorna blocos físicos brutos com width/height prontos para Bin Packing.
        """
        clusters = []

        for node in nodes_requirements:
            if node.get("is_raw_input"):
                continue  # Ore/Fluid entra no Bus, não ganha cluster físico de máquina.
            
            item = node["item"]
            
            # Arredonda frações para cima. Ex: 4.8 fornalhas -> 5 fornalhas.
            machines_exact = node.get("machines_needed", 0)
            if machines_exact <= 0:
                continue
                
            qty = math.ceil(machines_exact)

            # Estratégia de Clustering Linear Local (v1):
            # Se tenho N máquinas, farei um bloco de proporção N x 1 (em linha)
            # Futuramente implementaremos Direct Insertion Pairs (ex: Cobre + Verde grudados)
            width = Clusterizer.ENTITY_SIZE
            height = Clusterizer.ENTITY_SIZE * qty

            # Monta o registro interno do cluster e suas posições relativas
            machines = []
            for i in range(qty):
                machines.append({
                    "item": item,
                    "rel_x": 0,                   # Posição X relativa dentro deste cluster
                    "rel_y": i * Clusterizer.ENTITY_SIZE # Cada máquina desce 3 tiles
                })

            clusters.append({
                "type": "cluster_linear",
                "item_group": item,
                "width": width,
                "height": height,
                "qty": qty,
                "machines": machines
            })

        return clusters
