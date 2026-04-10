<div align="center">
  <h1>🏭 Factorio Blueprint Generator Django</h1>
  <p><b>Algorithmic Blueprint Generator (High-Density Edition) - v4.0</b></p>
</div>

<p align="center">
  Uma API RESTful acoplada a um Frontend em Vite projetada para gerar Blueprint Strings para o Factorio (Vanilla 1.1+) com níveis extremos de densidade e layout de <i>Megabase</i>.
</p>

---

## 🎯 Visão Geral

Diferente de geradores clássicos que apenas empilham fornalhas em linhas infinitas, o **FBG-Django v4.0** utiliza um *Motor de Roteamento Heurístico de Alta Densidade*. Ele agrupa logicamente máquinas (Clustering) combinando-as numa geometria retangular perfeita através de empacotamento em duas dimensões (Bin Packing 2D - MaxRects), traçando e resolvendo o *belt weaving* utilizando algoritmos avançados de *Pathfinding (A\*)* baseados em rotas ortogonais.

Tudo é rigorosamente envolto por um ***Input Bus*** e um ***Output Bus*** devidamente balanceado, provido de *Constant Combinators* que mapeiam em tempo-real exatamente as taxas de produção versus insumo, garantindo *tiling* perfeito em malhas de trens (City Blocks).

## 🧰 Stack Tecnológica

O sistema segue a filosofia *Separation of Concerns* debaixo das seguintes ferramentas:

### Backend (The Engine)
- **Linguagem**: Python 3.12+
- **Framework Ouro**: Django 5.x + Django Rest Framework (DRF)
- **Validação de Payload**: Pydantic v2 (Segurança de tipagem estrita de API)
- **Matemática do Motor**: `networkx` para Topologia de Nós, empacotamento matricial com MaxRects/Guillotine.
- **Factory Encoding**: `factorio-draftsman` para materializar a lógica em um Blueprint em Base64.

### Frontend
- **Framework**: React 19 construído com Vite
- **Tipagem**: TypeScript
- **Estética**: CSS3 Vanilla (Glassmorphism + Dark Mode), sem dependências pesadas de Frameworks de UI (No Tailwind), almejando estética Premium.

---

## 🧠 Arquitetura do Motor Lógico do FBG-Django

Toda vez que a API recebe uma requisição POST de `/api/generate/`, o *pipeline arquitetural cego* (onde toda a saída da camada vira entrada restritiva para a seguinte) se inicia:

1. **Rate Solver (`solver.py`)**: Valida `recipes.json`, traça *Topological sort* (tratando ciclos) limitando a fabricação das máquinas pelo *rate_per_minute* estrito.
2. **Clustering (`clustering.py`)**: Minimiza esteiras conectando componentes que funcionam em proporção compatível fisicamente de inserção direta (ex: 3 Fios de Cobre colados diretos em 2 Máquinas de Verde).
3. **Bin Packing (`bin_packing.py`)**: Posiciona retângulos espaciais brutos com algoritmos geométricos visando 1:1 de Aspect Ratio.
4. **Bus Designer (`bus_designer.py`)**: Configura as bordas e define Constant Combinators com lógicas estritas de leitura estatística.
5. **Lane Mapper (`lane_mapper.py`)**: Resolve restrições Multiplexadas, decidindo quando as pistas esquerdas ou direitas de um mesmo belt serão misturadas ou purgadas.
6. **Pathfinding (`pathfinding.py`)**: A* (A-Star) direcionado em grade contínua conectando os clusters de máquinas e Bus de IOs de forma orgânica e cruzada (privilegia *underground*).
7. **Overlays**: Rotinas finais que impõem postes de energia (`electrical.py`), pumps na divisão de fluidos paraleis (`fluids.py`) e *Overlap placement* para sinalizadores (`beacons.py`).
8. **Draftsman Compiler**: Encapsulamento de tudo na API do Draftsman, exportando e decodificando o arquivo final.

---

## 🛠 Como Instalar Localmente

### 1️⃣ Inicializando o Backend
O Backend serve a API nos portais na porta 8000 do Django via SQLite puramente.

```bash
# Navegue até o módulo do backend
cd backend/

# Crie e inicie o ambiente virtual (venv)
python -m venv venv
.\venv\Scripts\Activate.ps1    # No Windows (use source venv/bin/activate no Linux/Mac)

# Instalar dependências estritas v4
pip install -r requirements.txt

# Aplicar migrações do DRF
python manage.py migrate

# Subir a API
python manage.py runserver
```

### 2️⃣ Inicializando o Frontend
O frontend fica apartado para facilitar desacoplamento visual/escalabilidade. 

```bash
# Abra um novo terminal e navegue para o Frontend
cd frontend/

# Instalar dependências do ecossistema JS
npm install

# Subir e compilar local server
npm run dev
```

---

## 📄 Contrato da API (Exemplo / Modo Simples)

Mande via `POST` em `/api/generate/`:

```json
{
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
}
```

---
Criado para escalar City Blocks!
