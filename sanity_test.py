import requests

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
      "machine": "chemical-plant"
    },
    "modules": {
      "beaconized": True,
      "beacon_entity": "beacon",
      "machine_modules": ["productivity-module-3"],
      "beacon_modules": ["speed-module-3"]
    }
}

try:
    response = requests.post("http://127.0.0.1:8000/api/generate/", json=payload)
    print("Status:", response.status_code)
    print("JSON:", response.json())
except Exception as e:
    print("Connection error:", str(e))
