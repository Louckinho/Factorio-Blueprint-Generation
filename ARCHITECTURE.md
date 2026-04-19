# 🏗️ FBG-Django: Arquitetura Híbrida (ADAM Project)

A arquitetura do **Factorio Blueprint Generator** evoluiu para um modelo híbrido, utilizando o **Django** como motor matemático e a **IA ADAM** como arquiteta de layouts.

---

## 🛰️ Novo Fluxo de Dados (Hybrid Flow)

1.  **User Input:** O usuário define o item, a taxa de produção e configurações de IA (tamanho do bloco, instruções personalizadas) no Frontend React.
2.  **Mathematical Calculation (Django):** 
    - O backend utiliza o `RateSolver` (baseado nas receitas oficiais do Factorio via `draftsman`) para calcular a quantidade exata de máquinas e insumos necessários.
3.  **Work Order:** O Django formata uma "Ordem de Serviço" JSON contendo os requisitos matemáticos e o contexto da IA.
4.  **Neural Generation (ADAM AI):**
    - A Ordem de Serviço é enviada via **AIBridge** (httpx assíncrono) para o motor local do Projeto ADAM (Ollama/Llama.cpp).
    - A IA gera o layout geométrico ideal e responde via **DSL comprimida**.
5.  **Reverse Translation (O Decodificador):**
    - O módulo `ReverseTranslator` interpreta a DSL, extrai metadados (`META|SIZE`) e normaliza coordenadas.
6.  **Tiling & Compilation (Django Control):**
    - O Django realiza o **"Carimbo" (Tiling)** horizontal caso a demanda produtiva exija múltiplos blocos da IA.
    - O `DraftsmanCompiler` gera a string final do blueprint.

---

## 📡 Detalhes da API Principal

### `POST /api/generate/`
- **Flexibilidade:** Suporta modos `simple` e `adam`.
- **Async Inside:** Utiliza Django Async Views para evitar bloqueio durante a inferência da IA.

---

## 🛠️ Tecnologias Utilizadas
- **Backend:** Django 5.x, DRF, Pydantic (Validação).
- **Engine:** factorio-draftsman (Vanilla Data), NetworkX (Graph Solver), httpx (AI I/O).
- **Frontend:** React, Vite, TypeScript, Premium CSS (Dynamic Themes).
- **AI Local:** Projeto ADAM (Série Llama-3 Fine-tuned via Unsloth).

---

## 🧪 Estrutura de Arquivos Atualizada
- `backend/api/`: Interfaces REST e Schemas Pydantic.
- `backend/engine/`: 
    - `solver.py`: Cérebro matemático.
    - `translator.py`: Decodificador DSL da IA.
    - `ai_bridge.py`: Ponte assíncrona com o Ollama.
    - `pipeline.py`: Orquestrador do fluxo híbrido.
    - `draftsman_compiler.py`: Compilador para blueprint strings.
- `frontend/src/`: Interface reativa com tema dinâmico ADAM.
