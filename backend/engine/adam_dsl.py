class AdamDSLParser:
    """
    Tradutor Reverso para a DSL do Projeto ADAM.
    Converte strings comprimidas (tokens) em dicionários de entidades do Factorio.
    """
    
    TOKEN_MAP = {
        'M1': 'assembling-machine-1',
        'M2': 'assembling-machine-2',
        'M3': 'assembling-machine-3',
        'F1': 'stone-furnace',
        'F2': 'steel-furnace',
        'F3': 'electric-furnace',
        'B1': 'transport-belt',
        'B2': 'fast-transport-belt',
        'B3': 'express-transport-belt',
        'U1': 'underground-belt',
        'U2': 'fast-underground-belt',
        'U3': 'express-underground-belt',
        'S1': 'splitter',
        'S2': 'fast-splitter',
        'S3': 'express-splitter',
        'I1': 'inserter',
        'I2': 'fast-inserter',
        'I3': 'long-handed-inserter',
        'I4': 'stack-inserter',
        'P1': 'small-electric-pole',
        'P2': 'medium-electric-pole',
    }
    
    DIR_MAP = {
        'U': 0, # Up
        'R': 2, # Right
        'D': 4, # Down
        'L': 6, # Left
    }

    RECIPE_MAP = {
        'IronG': 'iron-gear-wheel',
        'CoppW': 'copper-cable',
        'ElecC': 'electronic-circuit',
        'AdvC': 'advanced-circuit',
        'ProcS': 'processing-unit',
        'IronP': 'iron-plate',
        'CoppP': 'copper-plate',
        'SteelP': 'steel-plate',
        'RedS': 'automation-science-pack',
        'GreenS': 'logistic-science-pack',
        'BlueS': 'chemical-science-pack',
    }

    @classmethod
    def parse_line(cls, line: str):
        """
        Interpreta uma única linha da DSL: TOKEN|X|Y|DIR|RECIPE|EXTRA
        Exemplo: M3|10|15|R|IronG
        """
        parts = line.split('|')
        if len(parts) < 3:
            return None
            
        token = parts[0]
        x = float(parts[1])
        y = float(parts[2])
        
        entity_name = cls.TOKEN_MAP.get(token, token) # Fallback para o nome direto
        
        entry = {
            "name": entity_name,
            "x": x,
            "y": y
        }
        
        if len(parts) > 3:
            entry["direction"] = cls.DIR_MAP.get(parts[3], 0)
            
        if len(parts) > 4:
            recipe_token = parts[4]
            entry["recipe"] = cls.RECIPE_MAP.get(recipe_token, recipe_token)
            
        if len(parts) > 5:
            # Extra info (ex: io_type para undergrounds)
            extra = parts[5]
            if extra in ('input', 'output'):
                entry["io_type"] = extra

        return entry

    @classmethod
    def parse_block(cls, dsl_block: str):
        """
        Parsing de um bloco multi-linha de DSL.
        """
        entities = []
        for line in dsl_block.strip().split('\n'):
            if not line.strip() or line.startswith('#'):
                continue
            ent = cls.parse_line(line.strip())
            if ent:
                entities.append(ent)
        return entities
