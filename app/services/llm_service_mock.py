import json
import re
from typing import Dict, Any, Optional
import structlog

from ..config import config
from ..utils.prompts import MANAGER_SPEC_PROMPT, PROGRAMMER_DIFF_PROMPT, REVIEW_PROMPT
from ..models.schemas import LLMSpecification, ReviewResult

logger = structlog.get_logger(__name__)

class MockLLMService:
    """Serviço mock para interação com LLM (para testes)"""
    
    def __init__(self):
        self.model = config.DEFAULT_MODEL
    
    def json_spec(self, user_input: str, project_config: Dict[str, Any]) -> LLMSpecification:
        """Gera especificação técnica mock"""
        try:
            logger.info(f"Gerando especificação mock para: {user_input}")
            
            # Especificação mock baseada no input
            spec_data = {
                "objective": f"Implementar: {user_input}",
                "impacted_areas": ["código principal", "testes"],
                "acceptance_criteria": [
                    "Funcionalidade implementada",
                    "Testes passando",
                    "Código limpo e documentado"
                ],
                "step_plan": [
                    "Analisar requisitos",
                    "Implementar funcionalidade",
                    "Adicionar testes",
                    "Documentar mudanças"
                ],
                "estimated_complexity": "medium"
            }
            
            return LLMSpecification(**spec_data)
                
        except Exception as e:
            logger.error(f"Erro ao gerar especificação mock: {e}")
            raise
    
    def generate_patch(self, spec_json: Dict[str, Any], repo_map: str, feedback: Optional[str] = None) -> str:
        """Gera patch mock"""
        try:
            logger.info(f"Gerando patch mock para: {spec_json.get('objective', '')}")
            
            # Patch mock simples
            mock_patch = """--- a/app/main.py
+++ b/app/main.py
@@ -1,3 +1,4 @@
 # Dev Trooper - Sistema Multi-Agentes
+print("Funcionalidade implementada com sucesso!")
 
 def main():
     print("Sistema funcionando!")
"""
            
            return mock_patch
            
        except Exception as e:
            logger.error(f"Erro ao gerar patch mock: {e}")
            raise
    
    def review(self, spec_json: Dict[str, Any], test_output: str, git_log: str, diff_applied: str) -> ReviewResult:
        """Revisa implementação mock"""
        try:
            logger.info("Executando revisão mock")
            
            # Revisão mock sempre aprovada
            review_data = {
                "approved": True,
                "notes": "Implementação aprovada - código limpo e funcional",
                "next_actions": None
            }
            
            return ReviewResult(**review_data)
                
        except Exception as e:
            logger.error(f"Erro ao revisar implementação mock: {e}")
            raise

# Instância global
llm_service = MockLLMService()
