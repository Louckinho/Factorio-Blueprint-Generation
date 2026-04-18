import urllib.request
import json

payload = {
    "mode": "simple",
    "target": "plastic-bar",
    "rate_per_minute": 5000,
    "options": {
      "tileable_block": True,
      "max_machines_per_block": 15
    },
    "tech_tier": {
      "belt": "express-transport-belt",
      "inserter": "fast-inserter",
      "machine": "assembling-machine-3",
      "oil_recipe": "advanced-oil-processing"
    },
    "modules": {
      "beaconized": False,
      "beacon_entity": "beacon",
      "machine_modules": ["productivity-module-3"],
      "beacon_modules": ["speed-module-3"]
    }
}

try:
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/generate/",
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        # Salva o resultado
        bp_string = data.get("blueprint_string", "")
        with open("meu_blueprint.txt", "w") as f:
            f.write(bp_string)
            
        print("Sucesso! A Blueprint String gigante foi salva em 'meu_blueprint.txt'!")
        print("Basta copiar o miolo dela e colar no Factorio!")
        
except Exception as e:
    print("Connection error:", str(e))
