from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .schemas import SimpleModeRequest, AdvancedModeRequest, ADAMRequest
from engine.pipeline import execute_generation_pipeline
from pydantic import ValidationError
from draftsman.data import recipes
import json

from asgiref.sync import async_to_sync

class BlueprintGenerateView(APIView):
    def post(self, request):
        print("\n" + "="*50)
        print(f"[DEBUG] PAYLOAD: {request.data}")
        print("="*50)
        try:
            mode = request.data.get('mode', 'simple')
            
            if mode == 'simple':
                parsed_data = SimpleModeRequest(**request.data)
            elif mode == 'advanced':
                parsed_data = AdvancedModeRequest(**request.data)
            elif mode == 'adam':
                parsed_data = ADAMRequest(**request.data)
            else:
                return Response(
                    {"error": "Invalid mode. Use 'simple', 'advanced' or 'adam'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Chama o motor de forma sincronizada
            print("[DEBUG] Chamando pipeline...")
            pipeline_func = async_to_sync(execute_generation_pipeline)
            blueprint_string, entities = pipeline_func(parsed_data.model_dump())
            print("[DEBUG] Pipeline concluído com sucesso.")
            
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
            import traceback
            print(traceback.format_exc())
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

