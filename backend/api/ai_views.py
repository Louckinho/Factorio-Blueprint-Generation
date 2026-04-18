from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .schemas import ADAMRequest
from engine.ai_bridge import AIBridge
from engine.adam_dsl import AdamDSLParser
from engine.draftsman_compiler import DraftsmanCompiler
from pydantic import ValidationError

class ADAMGenerateView(APIView):
    """
    View responsável pela geração de Blueprints via I.A (Projeto ADAM).
    """
    def post(self, request):
        try:
            # 1. Validação do Payload
            parsed_data = ADAMRequest(**request.data)
            
            # 2. Chamada à Ponte de I.A (Ollama / ADAM)
            dsl_output = AIBridge.call_adam(parsed_data.prompt)
            
            if not dsl_output:
                return Response(
                    {"error": "A IA não retornou uma resposta válida."},
                    status=status.HTTP_502_BAD_GATEWAY
                )
            
            # 3. Parsing da DSL para lista de entidades
            entities_list = AdamDSLParser.parse_block(dsl_output)
            
            if not entities_list:
                return Response(
                    {"error": "Falha ao interpretar a DSL gerada pela IA.", "raw_dsl": dsl_output},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
            
            # 4. Compilação final via Draftsman
            compiler = DraftsmanCompiler(label=f"ADAM AI Generated")
            blueprint_string, entities = compiler.generate_from_entities(entities_list)
            
            return Response({
                "status": "success",
                "mode": "ADAM-AI",
                "blueprint_string": blueprint_string,
                "entities_map": entities,
                "raw_dsl": dsl_output
            }, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": "Payload validation failed", "details": e.errors()}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
