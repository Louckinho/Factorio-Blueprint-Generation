# 📖 Guia Didático: Do Zero ao seu Blueprint

Bem-vindo ao **Factorio Blueprint Generator (FBG)**! Este guia foi feito para que você consiga rodar o projeto e gerar sua primeira planta industrial em menos de 5 minutos.

---

## 🛠️ Passo 1: Preparação do Ambiente

### 1.1 Clonar o Repositório
Abra seu terminal favorito (PowerShell ou Bash) e clone o projeto:
```bash
git clone https://github.com/Louckinho/Factorio-Blueprint-Generation.git
cd Factorio-Blueprint-Generator
```

### 1.2 Configurar o Backend (O Cérebro)
Navegue até a pasta `backend` e configure o Python:
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # No Windows
pip install -r requirements.txt
python manage.py runserver
```
> O servidor de API estará rodando em `http://127.0.0.1:8000`. Não feche este terminal!

### 1.3 Configurar o Frontend (A Interface)
Abra um **novo terminal** na pasta do projeto:
```bash
cd frontend
npm install
npm run dev
```
> Clique no link que aparecer (geralmente `http://localhost:5173`) para abrir o site.

---

## 🏭 Passo 2: Gerando sua Primeira Fábrica

No site, siga estas etapas:

1.  **Autocomplete de Itens:** Clique no campo "Target Item" e comece a digitar (ex: `Green Circuit` ou `Plastic`). A lista dinâmica filtrará os 650+ itens do jogo.
2.  **Taxa de Produção:** Defina quantos itens por minuto você deseja (ex: `60`).
3.  **Tecnologia:** Escolha se quer usar Cintas Azuis, Amarelas ou Vermelhas. O sistema calculará a velocidade real das máquinas.
4.  **Botão Mágico:** Clique em **"GENERATE BLUEPRINT"**.

---

## 🖼️ Passo 3: Visualização e Uso

1.  **Preview:** Abaixo do formulário, um "Minimapa" aparecerá. 
    - 🟧 **Laranja**: Suas máquinas.
    - 🟦 **Azul**: Esteiras conectadas ao barramento.
    - 🟩 **Verde**: Braços (Inserters) automáticos.
    - 🌊 **Ciano**: Canos de fluido (Roteamento A* inteligente).
2.  **Copiar:** Clique no código gigante (Blueprint String), copie e vá para o Factorio.
3.  **Colar:** No jogo, aperte `Ctrl + V` e pronto! Suas máquinas aparecerão perfeitamente alinhadas.

---

## 📝 Dicas de Expert (Pro-Tips)
- **Barramentos:** O sistema cria um "Input Bus" à esquerda com combinadores que dizem exatamente quanto material você precisa injetar.
- **Fluidos:** Em receitas químicas (como Plástico), o sistema usa **Canos Subterrâneos** via `PipeRouter` para manter o layout limpo.
- **Tiers:** Você pode trocar entre esteiras amarelas, vermelhas ou azuis no painel; o engine ajustará todos os componentes (splitters, undergrounds) automaticamente.

---

## 🛠️ Guia de Manutenção e Arquitetura

O core do **FBG v4.5** é dividido em módulos independentes (Separation of Concerns). Se você quiser modificar algo, aqui está o mapa:

### 1. O Pipeline Principal (`backend/engine/pipeline.py`)
É aqui que a mágica é coordenada. Ele chama os componentes na ordem: Solver -> Clustering -> Packing -> Routing -> Polishing. Se quiser adicionar uma nova etapa global, comece por aqui.

### 2. Algoritmos de Roteamento (A Pasta `routers/`)
Agora o roteamento não é mais um arquivo gigante. Ele está dividido:
- **`belt_router.py`**: Aqui reside a inteligência das **Esteiras** e **Inserters**. Se os braços estiverem pegando itens do lado errado ou as esteiras estiverem ziguezagueando muito, ajuste os pesos (penalidades) e a lógica de margem aqui.
- **`pipe_router.py`**: Cuida exclusivamente dos **Canos** e fluidos. Se quiser melhorar como os canos saltam por cima das esteiras, este é o lugar.
- **`pathfinding.py`**: Contém o mapa de grid geral (`GridMap`) e o algoritmo **A*** puro. Raramente precisa ser mexido, a menos que queira mudar a base matemática do sistema.

### 3. Lógica de Receitas e Máquinas (`backend/engine/solver.py`)
Se o sistema estiver calculando errado a quantidade de itens ou não reconhecendo uma máquina nova do jogo, o `RateSolver` é o responsável por consultar o banco de dados do Factorio (via Draftsman).

### 4. Compilação Visual (`backend/engine/draftsman_compiler.py`)
Este arquivo transforma as coordenadas matemáticas em objetos reais do jogo. Se as máquinas nascerem sem a "receita" (recipe) setada, ou se os braços estiverem apontando para o lado oposto do visual, ajuste a transposição de dados aqui.

### 5. Frontend (React + Vite)
Localizado na pasta `/frontend`. Usa Tailwind CSS para o estilo premium. A comunicação com o backend é feita via `fetch` para o endpoint `/api/generate/`.

---

## 📝 Dicas de Expert (Pro-Tips)
- **Erros:** Se algo não carregar, verifique se o terminal do Backend (Django) não mostrou nenhum erro em vermelho.
- **Tokens:** A divisão em arquivos menores facilita para que IAs (como eu) consigam ler apenas o necessário, economizando processamento e evitando erros de contexto.

---
*Divirta-se dominando o planeta!* 🚀🏭
