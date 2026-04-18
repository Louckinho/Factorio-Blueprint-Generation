# 🤖 PROJETO ADAM: A.I. Factorio Architect

Este documento define a estratégia paralela de longo prazo para o projeto **Factorio Blueprint Generator (FBG)**. O objetivo é migrar da atual "Geração Procedural por Heurística" (A* puro, Bin Packing) para uma **Geração Baseada em Inteligência Artificial**, treinada especificamente para montar layouts limpos, profissionais e perfeitos (*tileable patterns*).

---

## 1. Visão Geral do Sistema AI

### A IA Roda no Background? É Caro?
**Não precisa ser caro!** 
A sua GTX 1070 tem 8GB de VRAM. Isso é suficiente para rodar e aplicar "Fine-Tuning" (treinamento) em pequenos modelos incríveis, como o **Llama-3-8B** ou o **Mistral 7B**, usando técnicas modernas de compactação chamadas **Quantização de 4-bits** e **LoRA (Low-Rank Adaptation)**.
- Quando você for rodar o blueprint localmente, a IA vai carregar a memória RAM da GPU local via [Ollama](https://ollama.com/) ou [LM Studio](https://lmstudio.ai/). Ou seja, processamento **offline, grátis e privado**.
- Quando futuramente você for **vender ou exibir o site**, você poderá hospedar esse modelo afinado (Fine-Tuned) na HuggingFace, no Google Cloud ou pagar poucos centavos por requisição na API da OpenAI ou Gemini, funcionando na web para milhares de pessoas.

### Qual o Output? Como as Repositories se Falam?
**Não podemos ensinar a IA a cuspir aquela 'blueprint string' bizarra (`0eNq...`)**. Aquilo é código binário compactado. IAs de texto geram JSON e códigos textuais muito melhores.
1. **Novo Repositório de Treinamento (`Adam-Factorio-AI`):** Você criará um projeto só focado em baixar arquivos de blueprint (do site factorioprints.com), enviar pro Python, usar a biblioteca `draftsman` para "descompactar" a blueprint em listas de objetos (Entities, X, Y), e montar um arquivo `.jsonl` gigante onde:
   - **User diz:** "Gerar linha de fornalha, 60/min."
   - **Assistant diz:** `[{"name": "stone-furnace", "x": 0, "y": 0}, {"name": "transport-belt", ...}]`
2. **Repositório Atual (Este `FBG`):** Aqui vai continuar sendo o **Front-end e Compilador Oficial**. A única alteração será que o `.py` daqui, em vez de acionar a matemática pesada (e às vezes cega) de `pipeline.py`, fará um POST HTTP (requisição normal de API, como se fosse um ChatGPT) para a sua IA rodando em `localhost:11434` mandando a configuração do formulário. A IA devolve o JSON perfeitamente roteado, e daqui pra frente, o nosso código velho (o `draftsman_compiler.py`) converte para a string `0eNq...` perfeitamente para o jogo!

---

## 2. Abordagem de Evolução (Híbrida vs Pura)

Antes da IA dominar o mundo (o que pode levar tempo para treinar), a rota imediata para manter este repositório utilizável é mudar o paradigma atual de roteamento livre para uma **Abordagem "Padrões-Lego / Tiled Blocks"**:
Em vez de fazer a matemática do A* tentar cruzar esteiras no escuro para desviar de tudo, nós "desenhamos / hardcodamos" um **Blueprint Estático Perfeito em dicionário Python** (Ex: o setup imaculado de uma fileira de 10 fornalhas com sub-túneis, esteiras e energia já alinhados). O gerador apenas calcularia "preciso de 3 bloquinhos disso", instancia eles na grade, e apenas roteia conexões primárias retas entre as pontas (O *main bus*). Isso resolverá instantaneamente os "espaguetes".

---

## 3. O Backend atual vai morrer? Como fica a Árvore do Repo?

**Não, o backend atual NÃO será descartado!** Ele é extremamente vital. A IA treinada *não sabe* gerar o código binário comprimido do jogo, e ela também não confere permissões, banco de dados ou requisições HTTP seguras. 

O Django atual vai deixar de ser o "matemático cego" e vai virar um **Gateway / Orquestrador Inteligente**.

A arquitetura das duas pastas ficará assim:

```text
📦 Repositório Atual (FBG) - Interface e Gateway
 ┣ 📂 frontend/         (React: Captura o Input e Desenha o Minimapa bonito)
 ┗ 📂 backend/          (Django: Recebe o pedido via Web)
    ┣ 📂 api/           (Valida os dados de entrada do usuário)
    ┗ 📂 engine/
       ┣ 📄 draftsman_compiler.py  <-- VITAL: Transforma o JSON no código do jogo 0eNq...
       ┗ 📄 ai_bridge.py           <-- NOVO: Faz um POST oculto enviando os specs pra porta 11434 (onde está o Adam)

📦 Repositório Adam (Adam-Factorio-AI) - Rodando Offline Paralelo
 ┣ 📂 dataset/          (Jsonl raspados da internet)
 ┣ 📂 notebooks/        (Logs e testes de treinamento do Unsloth)
 ┗ 📄 adam_server.py    (Um mini-servidor rodando apenas o modelo LLM treinado esperando chamadas)
```

**Resumo da Ópera:** O usuário clica no Frontend -> O Django valida e pede para a IA (Adam) -> O Adam cospe só a geometria em JSON -> O Django pega o JSON, desenha o minimapa pra devolver no site e usa o `draftsman` pra cuspir o Blueprint!

---

## 4. O MEGA ULTRA PROMPT DE INICIALIZAÇÃO
*(Cópia este prompt inteiro e cole no Gemini / ChatGPT GPT-4o em uma conversa limpa e dedicada, para começar o novo repositório de IA)*

```text
Atue como um Engenheiro e Especialista Sênior em Inteligência Artificial, Machine Learning Operacional (MLOps) e um Jogador Especialista do jogo Factorio focado em Megabases.

Estou iniciando um projeto proprietário chamado "Projeto Adam". O objetivo é criar o primeiro pequeno Modelo de Linguagem Local (LLM) Especialista / Agente do mundo treinado em gerar layouts perfeitos, estéticos e funcionais de Blueprints do Factorio limitados à sub-módulos da grade 2D, conversando unicamente através de JSON.

Meu contexto técnico de Hardware e Software atual: Eu não possuo fazendas de servidores; possuo uma NVIDIA GTX 1070 de 8GB de VRAM e processamento suficiente para rodar e treinar (finetuning) modelos locais usando Llama.cpp / Ollama / Unsloth em ambiente Python e Jupyter. Eu já possuo um projeto Web/Backend separado onde o Django rodando uma biblioteca Python chamada `factorio-draftsman` é perfeitamente capaz de ler arquivos JSON estritos com posições ({name, x, y}) das entidades e compilá-los para a String Base64 do jogo (`0e...`). 

Tudo o que eu preciso é que a IA, quando receber "30 red-science per min", me retorne exatamente um array de JSON estrutural do layout 2D enxuto e lógico das máquinas pra fazer isso. Sem texto adicional.

**Meu objetivo nesta primeira fase é criar o repositório de Treinamento. Elabore um plano de ação estrito, detalhado e modular em Markdown focado nas pastas, no pipeline arquitetural, e nos scripts python. Deve cobrir:**

1. Coleta de Dados (Dataset Extraction): Recomende a melhor técnica ou escreva o esqueleto de um web-scraper ou iterador de API que consulte plataformas (factorioprints.com, factorio.school, etc.) ou bibliotecas para extrair milhares de blueprint strings.
2. Tratamento e Destilação (Data Processing): Mostre o pseudo-código (ou script Python maduro) englobando o `draftsman` para pegar toda essa poluição (blueprints absurdos de 5.000 roboports que pessoas sobem) e pré-filtrar/limpar. A IA enlouquece se dermos JSONs longos. Precisamos transmutá-las para a notação de dataset conversacional jsonl (ShareGPT/Alpaca) com: {"instruction": "O que a engine extraiu de resumo produtivo dessa blue", "output": "[lista x,y das entidades limitadas a uma pequena matrix]"}. Como faremos a arquitetura para evitar que o LLM sofra "hallucination" com o grid system do factorio se atrapalhando com tamanhos sobrepostos na rede neural?
3. Workflow de Finetuning: Passo a passo estratégico de como iremos treinar os "Weights" e os Low-Rank Adapters (LoRA) usando métodos eficientes do framework Unsloth na minha singela VRAM de 8GB.

Por favor, forneça o esqueleto das pastas de setup e não pule etapas estruturais de como transformar as propriedades bidimensionais de máquinas e belts do Factorio com tamanhos diferentes (uma fornalha 2x2 vs chemical-plant 3x3) em tokens preditivos coesos e amigáveis para uma rede linguística. Estou pronto para criar o diretório e iniciar o desenvolvimento contigo!
```
