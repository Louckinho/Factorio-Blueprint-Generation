from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .schemas import SimpleModeRequest, AdvancedModeRequest
from engine.pipeline import execute_generation_pipeline
from pydantic import ValidationError
from draftsman.data import recipes
import json

class BlueprintGenerateView(APIView):
    def post(self, request):
        try:
            # We explicitly check the mode to parse with the correct Pydantic schema
            mode = request.data.get('mode', 'simple')
            
            if mode == 'simple':
                parsed_data = SimpleModeRequest(**request.data)
            elif mode == 'advanced':
                parsed_data = AdvancedModeRequest(**request.data)
            else:
                return Response(
                    {"error": "Invalid mode. Use 'simple' or 'advanced'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Chama o motor passando o dicionário limpo validado pelo Pydantic
            blueprint_string, entities = execute_generation_pipeline(parsed_data.model_dump())
            
            # Retorna com a resposta validada
            return Response({
                "status": "success",
                "blueprint_string": blueprint_string,
                "entities_map": entities,
                "metadata": {
                    "item": getattr(parsed_data, 'target', 'custom-nodes')
                }
            }, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": "Payload validation failed", "details": e.errors()}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RecipeListView(APIView):
    def get(self, request):
        """
        Retorna todos os itens baseados nas chaves das receitas do Factorio.
        """
        try:
            items_list = []
            for item_id, data in recipes.raw.items():
                # Formata o nome para exibição (ex: advanced-circuit -> Advanced Circuit)
                display_name = item_id.replace('-', ' ').title()
                items_list.append({
                    "id": item_id,
                    "name": display_name
                })
            
            # Ordenar alfabeticamente
            items_list.sort(key=lambda x: x["name"])
            
            return Response(items_list, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

