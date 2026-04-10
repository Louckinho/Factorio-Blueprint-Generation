# FBG-Django Architecture

O sistema obedece um fluxo pipeline rigorosamente sequencial:

1. **API**: Recebe o payload (simples ou avançado). Valida com DRF + Pydantic.
2. **Solver**: Resolve o Grafo Topológico. Usa dados nativos para calcular quantidades baseadas no target e rate_per_minute.
3. **Clusterizer**: Avalia proporções das máquinas.
4. **BinPacking**: MaxRects para preenchimento.
5. **BusDesigner**: Constrói IO estáticos.
6. **LaneMapper**: Mapeamento e multiplexações.
7. **Pathfinding**: A* para conectar todo mundo com menor uso de cintas em superfície.
8. **Overlays**: Ajustes finos (elétrica, balanço local).
9. **Draftsman**: Codificação na String base64 de blueprints do Factorio.
