<div align="center">
  <h1>🏭 FBG-Django: Algorithmic Blueprint Generator</h1>
  <p><b>High-Density Edition (v4.0)</b></p>
  <p><i>The Ultimate Factorio 1.1+ Routing and Packing Engine</i></p>
</div>

<p align="center">
  Uma plataforma baseada em <b>Django REST Framework + React/Vite</b> construída do zero para resolver matematicamente o caos do Factorio. Em vez de criar *spaghettis*, esta API calcula proporções perfeitas usando Teoria dos Grafos, agrupa montadoras via algoritmos de inserção direta e as envelopa num city block compacto perfeito utilizando <b>Bin Packing 2D</b> espacial puro e pathfinding A*.
</p>

---

## 🧰 Stack Tecnológica e Filosofia
* **Backend:** Python 3.12+, Django 5.x, DRF, Pydantic (validação blindada), NetworkX (Grafos Lineares), `factorio-draftsman`.
* **Frontend:** React 19, Vite, TypeScript, Vanilla CSS (estética rica de Glassmorphism/Dark Mode sem frameworks intrusivos).
* **Paradigmas:** *Separation of Concerns*, Pipeline 100% Desacoplado, Test-Driven Architecture.

---

## 🧠 Arquitetura do Motor (O Pipeline Principal)

Nenhum arquivo chama o outro acidentalmente. A API recebe o payload JSON e injeta no `engine/pipeline.py`, que cruza as camadas sequencialmente:

1. **Rate Solver (`solver.py`)**: Valida o Grafo Topológico. Usa dados nativos para calcular quantas máquinas exatas são precisas para suprir a requisição sem sub ou superprodução.
2. **Clustering (`clustering.py`)**: Analisa as "taxas". Se X fios de cobre sustentam Y máquinas de circuito verde com proximidade de inserters (ratio 3:2 por exemplo), o sistema as "cola" e bane esteiras intermediárias ali. É o poder da Inserção Direta Máxima.
3. **Bin Packing (`bin_packing.py`)**: Algoritmos de *MaxRects* e *Guillotine*. Os clusters são tratados como rectângulos imutáveis 2D e rotacionados inteligentemente dentro de um grande quadrado buscando Aspect Ratio 1:1.
4. **Bus Designer (`bus_designer.py`)**: Aloca de forma imutável o *Input Bus* num flanco, o *Output Bus* no outro, e insere os *Constant Combinators* com os consumos/produções por minuto assinalados e perfeitamente calculados.
5. **Lane Mapper / Pathfinding (`lane_mapper.py` e `pathfinding.py`)**: Algoritmos customizados de *A-Star (A\*)* correm num grid ortogonal, desviando de fornalhas, privilegiando *Underground Belts* (custo heurístico pífio) para maximizar "weaves" insanos, sem cruzar fluídos.

---

## 🗃️ De onde vêm os Dados (Receitas / Factorio Data)?

O gerador precisa saber o "custo" exato de cada receita, tempos de crafting e velocidades.
Para fornecer isso, usaremos o padrão purista `data/recipes.json` e a biblioteca `factorio-draftsman`.

**Como conseguir e atualizar essas informações?**
1. O *Draftsman* já injeta boa parte das dimensões das entidades padrões internamente (o tamanho físico de um Chemical Plant, etc).
2. Para gerar dump customizado e puro (ex: receitas de Mods complexos), é utilizado um mod in-game do Factorio como o **gvv** (Gopher's Variables Viewer) ou dumper CLI do próprio Factorio. Este dump deve ser parametrizado num arquivo master para alimentar o nosso *Rate Solver*. No futuro, nossa pasta `engine/data/` armazenará isso de forma dinâmica em JSON puro para velocidade de memória (cache in-memory).

---

## 🚀 Como Executar o Projeto Localmente

O sistema roda localmente dividindo o cérebro em duas frentes independentes: A API que pensa a geometria, e o SPA que desenha o painel.

### 1️⃣ Subindo a API Django (Porta 8000)
```bash
cd backend/

# Ative seu ambiente virtual (Importante!)
.\venv\Scripts\Activate.ps1    # PowerShell (Windows)

# Instale os pacotes requeridos Pydantic, Draftsman, DRF
pip install -r requirements.txt

# Inicialize o banco base do Django
python manage.py migrate

# Inicie o ecossistema nas portas
python manage.py runserver
```

### 2️⃣ Subindo o SPA React (Porta 5173)
Em um **novo** terminal:
```bash
cd frontend/

# Garanta o node_modules na raiz do front
npm install

# Suba o Hot Reload do Vite
npm run dev
```
Após isso, seu portal visual estará vivo e comunicando via Fetch com o Django! O CORS da API já esta preparado para aceitar pacotes do Vite.

---

## 📡 Como Consumir nossa API e Exemplo de Payload

Acesso total na rota: **`POST http://localhost:8000/api/generate/`**  

### 🧰 Modo Simples (Recomendado)
A interface pede ao Engine apenas: *"Me resolva X plásticos por minuto usando Y Tech e me devolva o blueprint."*

**Exemplo via Node.js/Fetch Assíncrono:**
```javascript
const response = await fetch("http://127.0.0.1:8000/api/generate/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    "mode": "simple",
    "target": "plastic-bar",
    "rate_per_minute": 5000,
    "options": {
      "tileable_block": true,
      "max_machines_per_block": 15
    },
    "tech_tier": {
      "belt": "express-transport-belt",
      "inserter": "fast-inserter",
      "machine": "chemical-plant"
    },
    "modules": {
      "beaconized": true,
      "beacon_entity": "beacon",
      "machine_modules": ["productivity-module-3"],
      "beacon_modules": ["speed-module-3"]
    }
  })
});
const data = await response.json();
console.log(data.blueprint_string); // "0eNq....."
```

### 🔬 O Significado do Contrato de Payload (Regras de Segurança v4.0)

Nossa camada recebe proteção e sanitização estrita via `Pydantic` debaixo do capô:
* **`target` / `rate_per_minute`:** Diz ao Solver qual nó raiz focar e as métricas absolutas (ex: 5000/min).
* **`options.tileable_block`:** Se `true`, a Engine vai focar em manter proporções simétricas para que, se você der CTRL+C e CTRL+V um blueprint colado ao lado do outro, cinturões e trilhos conectem perfeitamente.
* **`tech_tier`:** Filtro rígido temporal. Em early game injete `"belt": "transport-belt"`, e em late game injecte express (azul). Nosso Pydantic validará a entidade contra compatibilidade *Vanilla*.
* **`modules.beaconized`:** Se "true", ativa o script `overlays/beacons.py` calculando sobreposições para não desperdiçar energia empilhando sinais máximos (`speed-module-3`) ao mesmo tempo em que espeta (`productivity-module-3`) nas pontas ativas.

### 🛠 Modo Avançado (Override de Grafos)
Se enviado `"mode": "advanced"`, o *Rate Solver* é sumariamente ignorado e pulado. O payload DEVE prover o mapeamento topográfico hardcoded na key `nodes`. Ideal para quando o jogador fez a matemática no Factorio Calculator / Helmod e quer apenas que organizemos e retangulizemos a geometria!

---
> Baseado no *Documento de Especificação de Software, Arquitetura e Contratos* (04-2026).
> Todo o motor foi edificado num VirtualEnv puro e segue as normas *Separation of Concerns* garantido densidade máxima.
