# 🏗️ FBG-Django: Arquitetura do Sistema

A arquitetura do **Factorio Blueprint Generator** é totalmente desacoplada, utilizando **Django REST Framework (DRF)** no Backend e **React (Vite) + TypeScript** no Frontend.

---

## 🛰️ Fluxo de Dados (Data Flow)

1.  **User Input:** O usuário seleciona um item na lista de busca (Combobox) no React.
2.  **API Request:** O Frontend envia um payload JSON para o `/api/generate/`.
3.  **Validation:** O Django usa **Pydantic** para validar se o item e a tecnologia (Cintas, Inserters) são compatíveis.
4.  **Pipeline Execute:** O `engine/pipeline.py` orquestra a sequência:
    - **Solver:** Calcula a matemática de produção.
    - **Clustering:** Agrupa máquinas.
    - **Bin Packing:** Define o layout 2D.
    - **Bus Designer:** Posiciona os barramentos e combinadores.
    - **Pathfinding (A\*):** Traça as esteiras e aloca os Inserters.
5.  **Draftsman Compiler:** Transforma o layout em uma **Blueprint String** e um **Mapa de Entidades**.
6.  **Visualization Render:** O React recebe a planta e desenha o minimapa via CSS Absoluto.

---

## 📡 Detalhes da API

### `GET /api/items/`
- **Fonte:** `draftsman.data.recipes.raw`
- **Função:** Fornece a lista de todas as receitas oficiais do Factorio Vanilla filtradas e prettificadas.

### `POST /api/generate/`
- **Entrada:** `SimpleModeRequest` (Tech Tier, Target, Rate).
- **Saída:** 
  - `blueprint_string`: String Base64 oficial.
  - `entities_map`: Array de objetos `{ name, position: {x, y} }` para o visualizador.

---

## 🛠️ O Próximo Nível: Roteamento de Fluidos
O **Roteamento de Fluidos** trará novas restrições ao sistema:
- **Camada de Pipes:** Diferente das esteiras, os canos não têm "lanes". Um cano de Gás de Petróleo ocupa o tile inteiro.
- **Evitar Contaminação:** O algoritmo A* deverá ter um peso de custo infinito quando tentar cruzar um tile ocupado por outro fluido.
- **Underground Pipes:** Usar saltos de 10 tiles para cruzar áreas densas de esteiras.

---

## 🧪 Estrutura de Arquivos
- `backend/api/`: Camada de interface REST e validação.
- `backend/engine/`: O "cérebro" matemático e geométrico.
- `frontend/src/`: Interface reativa de alta densidade.
