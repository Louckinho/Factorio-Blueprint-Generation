# 🏗️ FBG-Django: Arquitetura do Sistema

A arquitetura do **Factorio Blueprint Generator** é totalmente desacoplada, utilizando **Django REST Framework (DRF)** no Backend e **React (Vite) + TypeScript** no Frontend.

---

## 🛰️ Fluxo de Dados (Data Flow)

1.  **User Input:** O usuário seleciona um item na lista de busca (Combobox) ou digita um prompt para a IA.
2.  **API Request:** 
    - `/api/generate/`: Pipeline Procedural (A* + Heurísticas).
    - `/api/generate-ai/`: Pipeline Neural (Projeto ADAM).
3.  **Validation:** O Django usa **Pydantic** para validar se o prompt ou os parâmetros técnicos são aceitáveis.
4.  **Pipeline Execute (ADAM Flow):**
    - **AI Bridge:** Envio do prompt para o Ollama (Local LLM).
    - **ADAM DSL Parser:** Tradução da resposta comprimida (`M|X|Y|D`) para objetos de entidades.
    - **Draftsman Compiler:** Geração final da Blueprint String.
5.  **Draftsman Compiler (Procedural Flow):** (Legado) Uso de Solver e Bin Packing para layouts matemáticos.

---

## 📡 Detalhes da API

### `GET /api/items/`
- **Fonte:** `draftsman.data.recipes.raw`
- **Função:** Fornece a lista de todas as receitas oficiais do Factorio Vanilla filtradas e prettificadas.

### `POST /api/generate-ai/`
- **Entrada:** `{"mode": "adam", "prompt": "30 red-science/min"}`
- **Saída:** 
  - `blueprint_string`: String oficial gerada pela IA.
  - `entities_map`: Para renderização no front.
  - `raw_dsl`: O código fonte geométrico que a IA gerou.

---

## 🛠️ A Revolução ADAM: AI-Gateway
A transição para I.A permite que o sistema abandone algoritmos de pathfinding pesados que frequentemente geravam "espaguete". A IA, treinada em layouts de especialistas, gera geometrias perfeitas via **DSL comprimida**, que o Django apenas compila usando o `draftsman`.
O **Roteamento de Fluidos** trará novas restrições ao sistema:
- **Camada de Pipes:** Diferente das esteiras, os canos não têm "lanes". Um cano de Gás de Petróleo ocupa o tile inteiro.
- **Evitar Contaminação:** O algoritmo A* deverá ter um peso de custo infinito quando tentar cruzar um tile ocupado por outro fluido.
- **Underground Pipes:** Usar saltos de 10 tiles para cruzar áreas densas de esteiras.

---

## 🧪 Estrutura de Arquivos
- `backend/api/`: Camada de interface REST e validação.
- `backend/engine/`: O "cérebro" matemático e geométrico.
- `frontend/src/`: Interface reativa de alta densidade.
