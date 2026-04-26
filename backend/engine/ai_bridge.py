import os
import torch
import json
import asyncio
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

class AIBridge:
    """
    Interface de comunicação com o cérebro ADAM local.
    Agora carrega o modelo LoRA diretamente na GPU para máxima velocidade.
    """
    
    _model = None
    _tokenizer = None
    
    # Caminho base para as memórias (Caminho do WSL)
    MODELS_BASE_PATH = os.getenv("ADAM_MODELS_PATH", "/mnt/c/Code/Pessoal/Projeto_ADAM_Factorio/models")
    DEFAULT_LORA = "lora_hybrid_v1" # Nosso novo cérebro híbrido

    @classmethod
    def _initialize_model(cls):
        """
        Carrega o modelo base e os pesos LoRA uma única vez.
        """
        if cls._model is not None:
            return

        print(f"\n[ADAM] Iniciando cérebro local...")
        lora_path = os.path.join(cls.MODELS_BASE_PATH, cls.DEFAULT_LORA)
        
        # 1. Detectar modelo base do adapter_config.json
        adapter_cfg_path = os.path.join(lora_path, "adapter_config.json")
        with open(adapter_cfg_path, "r") as f:
            adapter_cfg = json.load(f)
        base_model_name = adapter_cfg.get("base_model_name_or_path", "unsloth/Llama-3.2-3B-bnb-4bit")
        
        print(f"[ADAM] Modelo Base: {base_model_name}")
        print(f"[ADAM] Memoria LoRA: {cls.DEFAULT_LORA}")

        # 2. Carregar Tokenizer
        cls._tokenizer = AutoTokenizer.from_pretrained(base_model_name)

        # 3. Carregar Modelo Base em 4-bit
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
        )
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            device_map="cuda",
            quantization_config=bnb_config,
            torch_dtype=torch.float16,
        )

        # 4. Aplicar LoRA
        cls._model = PeftModel.from_pretrained(base_model, lora_path)
        cls._model.eval()
        print("[ADAM] Cérebro carregado e pronto para ordens.\n")

    @classmethod
    async def call_adam(cls, work_order: str, max_retries: int = 1):
        """
        Envia a Ordem de Serviço para a IA e retorna a string DSL.
        """
        # Garantir que o modelo está carregado
        if cls._model is None:
            await asyncio.to_thread(cls._initialize_model)

        # Template Alpaca EXATO do colab_train.py (Linha 53)
        prompt = (
            "### Instruction:\n"
            f"{work_order}\n\n"
            "### Input:\n\n\n"
            "### Response:\n"
        )

        print(f"[AI BRIDGE] Gerando para: {work_order}...", flush=True)

        try:
            inputs = cls._tokenizer(prompt, return_tensors="pt").to("cuda")
            
            with torch.no_grad():
                outputs = await asyncio.to_thread(
                    cls._model.generate,
                    **inputs,
                    max_new_tokens=1024,
                    do_sample=True,
                    temperature=0.3,
                    top_p=0.9,
                    repetition_penalty=1.15, # Balanceado para evitar loops e permitir padroes
                    pad_token_id=cls._tokenizer.eos_token_id
                )

            result = cls._tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Debug: Ver exatamente o que saiu do modelo antes de qualquer corte
            print(f"[AI BRIDGE] RAW OUTPUT:\n{result}\n[END RAW OUTPUT]", flush=True)

            if "### Response:" in result:
                dsl = result.split("### Response:")[-1].strip()
            else:
                dsl = result.strip()

            if dsl and dsl.startswith("S "):
                print(f"[AI BRIDGE] Sucesso: DSL gerada ({len(dsl)} caracteres)")
                return dsl
            
            print(f"[AVISO] IA gerou resposta inválida.")
            return None

        except Exception as e:
            print(f"[ERRO] Falha na inferência local: {e}")
            return None
