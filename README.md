# ⚙️ Factorio Blueprint Generator (FBG) - AI Powered

O FBG é uma plataforma web para geração de blueprints ultra-eficientes do jogo Factorio. O projeto está evoluindo de uma engine procedural baseada em algoritmos clássicos para um sistema neural chamado **Projeto ADAM**, que utiliza LLMs locais (Ollama) para desenhar layouts perfeitos e estéticos.

---

## 🚀 Novidade: Integração com Projeto ADAM (A.I)

O backend agora conta com um **AI-Gateway** pronto para se conectar ao seu modelo ADAM local. 
- **Entrada Agnóstica:** Peça o que quiser via prompt (Ex: "Fábrica de Ciência Vermelha 30/min").
- **Geometria via DSL:** A IA retorna uma linguagem geométrica comprimida de tokens (DSL).
- **Compilação Nativa:** O Django traduz a DSL e usa a biblioteca `factorio-draftsman` para gerar a string oficial `0e...` pronta para o jogo.

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

No site, use a nova interface premium:

1.  **Sidebar de Itens:** Navegue pela barra lateral esquerda para explorar os itens por categoria (Logística, Produção, Energia, etc.). Use o campo de busca para encontrar itens instantaneamente.
2.  **Seleção Inteligente:** Ao selecionar um item, ele aparecerá no painel central com seu ícone e ID formatado.
3.  **Taxa de Produção:** Defina quantos itens por minuto você deseja (ex: `60`).
4.  **Configuração de Esteiras:** Escolha entre Cintas Amarelas, Vermelhas ou Azuis.
5.  **Botão Mágico:** Clique em **"GENERATE BLUEPRINT"**.

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
- **Ícones Locais:** O projeto agora conta com um sistema de **Cache de Assets**. Mais de 500 ícones do Factorio são servidos localmente para garantir performance e funcionamento offline.
- **Tiers:** Você pode trocar entre esteiras amarelas, vermelhas ou azuis no painel; o engine ajustará todos os componentes (splitters, undergrounds) automaticamente.

---

## 🛠️ Guia de Manutenção e Arquitetura

O core do **FBG v4.5** é dividido em módulos independentes (Separation of Concerns). Se você quiser modificar algo, aqui está o mapa:

### 1. O Pipeline Principal (`backend/engine/pipeline.py`)
É aqui que a mágica é coordenada. Ele chama os componentes na ordem: Solver (Topológico) -> Clustering -> Packing -> Routing -> Polishing. Se quiser adicionar uma nova etapa global, comece por aqui. A inteligência de ordem (Fornos antes de Montadoras) é garantida no RateSolver usando `networkx`.

### 2. Algoritmos de Roteamento (A Pasta `routers/`)
Agora o roteamento não é mais um arquivo gigante. Ele está dividido:
- **`belt_router.py`**: Aqui reside a inteligência das **Esteiras** e **Inserters**. As máquinas são alocadas em "Lanes" limpas por coluna para evitar espaguete e balanceadas para evitar super-lotação num único belt.
- **`pipe_router.py`**: Cuida exclusivamente dos **Canos** e fluidos, garantindo varredura real nas receitas para evitar canos vazios.
- **`pathfinding.py`**: Contém o mapa de grid geral (`GridMap`) e o algoritmo **A*** puro. 

### 3. Lógica Astronômica e Inteligência Artificial Avançada
Se perceber que as heurísticas e o pathfinding puro não são suficientes, consulte o arquivo oficial de estratégia de Inteligência Artificial: **[PROJETO-ADAM-FACTORIO.md](./PROJETO-ADAM-FACTORIO.md)**. O repositório atual foi planejado e concebido para servir ativamente de Compilador Python (Draftsman) para inputs preditivos de IAs treinadas locais.

### 4. Compilação Visual (`backend/engine/draftsman_compiler.py`)
Este arquivo transforma as coordenadas matemáticas em objetos reais do jogo. As **Tiers** viajam limpas pelo backend, garantindo que se o formulário pedir amarelo, você consiga esteiras amarelas. Sem gambiarras no código.

### 5. Frontend (React + Vite)
Localizado na pasta `/frontend`. Usa **Vanilla CSS** customizado para uma estética "Premium Dark Mode". Um sistema inteligente de mapeamento de IDs resolve automaticamente os ícones para receitas complexas (como reciclagem).

---

## 📝 Dicas de Expert (Pro-Tips)
- **Erros:** Se algo não carregar, verifique se o terminal do Backend (Django) não mostrou nenhum erro em vermelho.
- **Tokens:** A divisão em arquivos menores facilita para que IAs (como eu) consigam ler apenas o necessário, economizando processamento e evitando erros de contexto.

---
*Divirta-se dominando o planeta!* 🚀🏭
