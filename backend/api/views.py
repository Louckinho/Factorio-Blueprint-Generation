from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .schemas import SimpleModeRequest, AdvancedModeRequest
from engine.pipeline import execute_generation_pipeline
from pydantic import ValidationError
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
            blueprint_string = execute_generation_pipeline(parsed_data.model_dump())
            
            # Retorna com a resposta validada
            return Response({
                "status": "success",
                "blueprint_string": blueprint_string,
                "metadata": {
                    "item": getattr(parsed_data, 'target', 'custom-nodes')
                }
            }, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": "Payload validation failed", "details": e.errors()}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
