# Como Atualizar as Receitas (recipes.json)

Este repositório delega os cálculos de taxa sobre o arquivo purista em `backend/engine/data/recipes.json`.

Esse json não deve conter mod data por padrão se o foco for Vanilla. Se o usuário alterar para, por exemplo, o mod Space Exploration ou Krastorio 2, um novo JSON deverá sobrescrever no diretório de engine.

Para extrair os tempos corretos de jogo (pois os dados cruos Lua variam), recomenda-se uso de:
- Draftsman Vanilla Data base dump.
- Mods de exportação in-game purificadas como `gvv` do Gopher.
