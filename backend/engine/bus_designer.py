class BusDesigner:
    @staticmethod
    def attach_buses(layout: list, nodes_requirements: list):
        """
        Define os barramentos de entrada e saída e adiciona combinadores constantes.
        """
        if not layout:
            return {"layout": layout, "input_bus": None, "output_bus": None}

        # 1. Calcular o Bounding Box do layout atual
        min_x = min(c["abs_x"] for c in layout)
        max_x = max(c["abs_x"] + c["width"] for c in layout)
        min_y = min(c["abs_y"] for c in layout)
        max_y = max(c["abs_y"] + c["height"] for c in layout)

        # 2. Definir posições dos barramentos (Default: Input esquerda, Output direita)
        # Deixamos um espaço extra para os barramentos e combinadores
        input_bus_x = min_x - 10
        output_bus_x = max_x + 10

        # 3. Coletar estatísticas para os combinadores
        input_signals = []
        output_signals = []

        for node in nodes_requirements:
            item = node["item"]
            rate_per_min = node.get("rate_per_sec", 0) * 60
            
            if node.get("is_raw_input"):
                # Consumo (Sinais negativos)
                input_signals.append({
                    "name": item, 
                    "count": -int(rate_per_min),
                    "type": "fluid" if node.get("is_fluid") else "item"
                })
            elif node.get("machines_needed", 0) > 0 and item == nodes_requirements[0]["item"]:
                # Produção do item alvo (Sinais positivos)
                output_signals.append({
                    "name": item, 
                    "count": int(rate_per_min),
                    "type": "fluid" if node.get("is_fluid") else "item"
                })

        # 4. Criar entidades de combinadores
        # Posicionamos os combinadores no início dos barramentos
        input_combinator = {
            "name": "constant-combinator",
            "position": (input_bus_x, min_y),
            "signals": input_signals
        }
        
        output_combinator = {
            "name": "constant-combinator",
            "position": (output_bus_x, min_y),
            "signals": output_signals
        }

        return {
            "layout": layout,
            "input_bus": {
                "x": input_bus_x,
                "min_y": min_y,
                "max_y": max_y,
                "combinator": input_combinator
            },
            "output_bus": {
                "x": output_bus_x,
                "min_y": min_y,
                "max_y": max_y,
                "combinator": output_combinator
            }
        }
