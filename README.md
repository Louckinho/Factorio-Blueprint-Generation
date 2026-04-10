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
- **Fluidos:** Em receitas químicas (como Plástico), o sistema usa **Canos Subterrâneos** para que seu personagem possa andar por dentro da fábrica sem tropeçar.
- **Erros:** Se algo não carregar, verifique se o terminal do Backend (Django) não mostrou nenhum erro em vermelho.

---
*Divirta-se dominando o planeta!* 🚀🏭
