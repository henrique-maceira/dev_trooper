import json
import re
from typing import Dict, Any, Optional
import openai
import structlog

from ..config import config
from ..utils.prompts import MANAGER_SPEC_PROMPT, PROGRAMMER_DIFF_PROMPT, REVIEW_PROMPT
from ..models.schemas import LLMSpecification, ReviewResult

logger = structlog.get_logger(__name__)

class LLMService:
    """Serviço para interação com LLM via OpenAI"""
    
    def __init__(self):
        openai.api_key = config.OPENAI_API_KEY
        self.model = config.DEFAULT_MODEL
    
    def json_spec(self, user_input: str, project_config: Dict[str, Any]) -> LLMSpecification:
        """Gera especificação técnica a partir da entrada do usuário"""
        try:
            prompt = MANAGER_SPEC_PROMPT.format(
                user_input=user_input,
                project_name=project_config.get('name', ''),
                repo_url=project_config.get('repo_url', ''),
                default_branch=project_config.get('default_branch', 'main'),
                test_command=project_config.get('test_command', 'pytest -q')
            )
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um gerente de projeto técnico experiente."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extrair JSON da resposta
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                spec_data = json.loads(json_match.group())
                return LLMSpecification(**spec_data)
            else:
                raise ValueError("Resposta do LLM não contém JSON válido")
                
        except Exception as e:
            logger.error(f"Erro ao gerar especificação: {e}")
            raise
    
    def generate_patch(self, spec_json: Dict[str, Any], repo_map: str, feedback: Optional[str] = None) -> str:
        """Gera patch unificado baseado na especificação"""
        try:
            feedback_text = feedback if feedback else "Nenhum feedback anterior"
            
            prompt = PROGRAMMER_DIFF_PROMPT.format(
                spec_json=json.dumps(spec_json, indent=2),
                repo_map=repo_map,
                feedback=feedback_text
            )
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um programador experiente."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Validar se é um diff válido
            if not content.startswith('--- a/') and not content.startswith('diff --git'):
                raise ValueError("Resposta não é um diff válido")
            
            return content
            
        except Exception as e:
            logger.error(f"Erro ao gerar patch: {e}")
            raise
    
    def review(self, spec_json: Dict[str, Any], test_output: str, git_log: str, diff_applied: str) -> ReviewResult:
        """Revisa a implementação e retorna resultado"""
        try:
            acceptance_criteria = spec_json.get('acceptance_criteria', [])
            
            prompt = REVIEW_PROMPT.format(
                spec_json=json.dumps(spec_json, indent=2),
                test_output=test_output,
                git_log=git_log,
                diff_applied=diff_applied,
                acceptance_criteria=json.dumps(acceptance_criteria, indent=2)
            )
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um revisor técnico experiente."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extrair JSON da resposta
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                review_data = json.loads(json_match.group())
                return ReviewResult(**review_data)
            else:
                raise ValueError("Resposta do LLM não contém JSON válido")
                
        except Exception as e:
            logger.error(f"Erro ao revisar implementação: {e}")
            raise

# Instância global
llm_service = LLMService()
