# ⚙️ Factorio Blueprint Generator (FBG) - v5.0 "Neural Era"

O FBG é uma plataforma web premium para geração de blueprints ultra-eficientes do jogo Factorio. O projeto utiliza uma **Arquitetura Híbrida** (Projeto ADAM), combinando o rigor matemático do Django com a criatividade geométrica de IAs locais (Ollama).

---

## 🚀 A Revolução: Projeto ADAM (A.I Powered)

O sistema abandonou algoritmos procedurais rígidos para adotar uma pipeline neural:
- **Cérebro Matemático (Django):** Resolve as taxas de produção e calcula a necessidade exata de máquinas usando a biblioteca `factorio-draftsman`.
- **Arquiteta Neural (ADAM AI):** Um modelo local (Llama-3 fine-tuned) gera o layout geométrico ideal via uma DSL (Domain Specific Language) comprimida.
- **Compilação Dinâmica:** O Django traduz a DSL e aplica lógica de **Tiling (Carimbo)** para escalar a produção horizontalmente, garantindo layouts limpos e expansíveis.

---

## 🛠️ Instalação Rápida

### 1. Requisitos
- **Python 3.10+** (Backend)
- **Node.js 18+** (Frontend)
- **Ollama** (Motor de IA local) com o modelo `adam-v1` instalado.

### 2. Configurar o Backend (O Cérebro)
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # No Windows
pip install -r requirements.txt
python manage.py runserver
```

### 3. Configurar o Frontend (A Interface)
```bash
cd frontend
npm install
npm run dev
```
> Acesse: `http://localhost:5173`

---

## 🏭 Experiência de Uso v5.0

No site, você encontrará a nova interface **ADAM-Ready**:

1.  **Modo de Geração:** Alterne entre "Classic" (Algoritmo v5) e "AI ADAM" para layouts neurais.
2.  **Configurações de IA:** Defina o tamanho dos blocos (ex: 15x15) e passe instruções customizadas (ex: *"Minimize tiles subterrâneos"*).
3.  **Visualização Premium:** Um preview em tempo real permite ver o layout gerado pela IA antes mesmo de copiar para o Factorio.
4.  **Copy & Paste:** Clique no código final, vá para o jogo e aperte `Ctrl + V`.

---

## 🏗️ Arquitetura do Sistema

O projeto é dividido em módulos desacoplados para fácil manutenção:

- **`backend/api/`**: Camada REST com validação via Pydantic e views assíncronas.
- **`backend/engine/solver.py`**: O motor que resolve as cadeias de suprimentos e máquinas.
- **`backend/engine/translator.py`**: Traduz os tokens geométricos da IA (`M|X|Y`) em entidades do jogo.
- **`backend/engine/pipeline.py`**: Orquestrador que une Matemática + IA.
- **`frontend/`**: Interface React com tema dinâmico que muda entre Âmbar (Clássico) e Neural Purple (ADAM).

---

## 🛠️ Guia de Variáveis de Ambiente (.env)
- `OLLAMA_URL`: URL do seu serviço de IA local (default: `http://localhost:11434`).
- `ADAM_MODEL`: Nome do modelo treinado (default: `adam-v1`).
- `USE_MOCK_AI`: Defina como `True` para testar o sistema sem um Ollama rodando.

---

*Divirta-se dominando o planeta com o poder da IA!* 🚀🏭
