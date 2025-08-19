from pathlib import Path
from typing import Tuple, Optional
import structlog

from ..models.schemas import Task, ProjectConfig
from ..config import config
try:
    from ..services.llm_service import llm_service
except ImportError:
    from ..services.llm_service_mock import llm_service
try:
    from ..services.github_service import github_service
except ImportError:
    from ..services.github_service_simple import github_service
from ..services.patch_service import patch_service
from ..services.test_service import test_service
from ..services.logging_service import log_agent_action, log_task_event

logger = structlog.get_logger(__name__)

class ProgrammerAgent:
    """Agente programador que implementa mudanças no código"""
    
    def implement(self, task: Task, project_config: ProjectConfig, branch_name: str) -> Tuple[bool, str, Path, str]:
        """Implementa as mudanças para uma task"""
        try:
            log_agent_action("programmer", "implement", {"task_id": task.id, "branch": branch_name})
            
            # Clone ou pull do repositório
            repo_path = github_service.clone_or_pull(project_config.repo_url, project_config.name)
            
            # Criar branch
            if not github_service.create_branch(repo_path, project_config.default_branch, branch_name):
                return False, "Falha ao criar branch", repo_path, ""
            
            # Gerar mapa do repositório
            repo_map = github_service.get_repo_map(repo_path)
            
            # Gerar especificação para o LLM
            spec_data = {
                "objective": task.objective,
                "impacted_areas": ["código principal"],
                "acceptance_criteria": project_config.acceptance_checks,
                "step_plan": ["implementar mudanças", "testar funcionalidade"]
            }
            
            # Gerar patch via LLM
            diff = llm_service.generate_patch(spec_data, repo_map)
            
            # Validar diff
            is_valid, validation_msg = patch_service.validate_diff(diff)
            if not is_valid:
                return False, f"Diff inválido: {validation_msg}", repo_path, diff
            
            # Aplicar patch
            success, patch_msg = patch_service.apply_unified_diff(diff, repo_path)
            if not success:
                return False, f"Falha ao aplicar patch: {patch_msg}", repo_path, diff
            
            # Criar backup do diff
            patch_service.create_diff_backup(diff, task.id)
            
            # Fazer commit das mudanças
            commit_message = f"feat: {task.objective}\n\nTask ID: {task.id}"
            if not github_service.commit_all(repo_path, commit_message):
                return False, "Falha ao fazer commit", repo_path, diff
            
            # Executar testes
            tests_ok, test_output = test_service.run_tests(repo_path, project_config.test_command)
            
            if not tests_ok:
                return False, f"Testes falharam: {test_output}", repo_path, diff
            
            log_task_event(task.id, "implementation_success", "Implementação concluída com sucesso")
            
            return True, test_output, repo_path, diff
            
        except Exception as e:
            logger.error(f"Erro na implementação: {e}")
            return False, f"Erro interno: {str(e)}", Path(), ""
    
    def push_and_pr(self, task: Task, project_config: ProjectConfig) -> Optional[str]:
        """Faz push da branch e cria Pull Request"""
        try:
            log_agent_action("programmer", "push_and_pr", {"task_id": task.id})
            
            repo_path = config.WORKDIR_BASE / project_config.name
            
            # Push da branch
            if not github_service.push_branch(repo_path, task.branch_name):
                return None
            
            # Extrair nome completo do repositório
            full_repo_name = github_service._extract_repo_name(project_config.repo_url)
            
            # Criar PR
            pr_title = f"feat: {task.objective}"
            pr_body = f"""
## Objetivo
{task.objective}

## Contexto
{task.context or 'Nenhum contexto adicional'}

## Task ID
{task.id}

## Branch
{task.branch_name}

---
*Implementado automaticamente pelo Dev Trooper*
"""
            
            pr_url = github_service.open_pr(
                full_repo_name=full_repo_name,
                title=pr_title,
                head_branch=task.branch_name,
                base=project_config.default_branch,
                body=pr_body
            )
            
            if pr_url:
                log_task_event(task.id, "pr_created", f"PR criado: {pr_url}")
            
            return pr_url
            
        except Exception as e:
            logger.error(f"Erro ao criar PR: {e}")
            return None

# Instância global
programmer_agent = ProgrammerAgent()
