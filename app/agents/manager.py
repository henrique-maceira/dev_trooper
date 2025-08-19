import re
import uuid
from typing import Optional, Tuple
import structlog

from ..models.schemas import Task, ProjectConfig, TaskStatus
from ..models.state_store import state_store
try:
    from ..services.llm_service import llm_service
except ImportError:
    from ..services.llm_service_mock import llm_service
try:
    from ..services.github_service import github_service
except ImportError:
    from ..services.github_service_simple import github_service
from ..services.logging_service import log_agent_action, log_task_event

logger = structlog.get_logger(__name__)

class ManagerAgent:
    """Agente gerente que coordena o processo de desenvolvimento"""
    
    def __init__(self):
        self.programmer_agent = None  # Será injetado
    
    def set_programmer_agent(self, programmer_agent):
        """Define o agente programador"""
        self.programmer_agent = programmer_agent
    
    def create_task(self, project_config: ProjectConfig, user_text: str) -> Task:
        """Cria uma nova task baseada na solicitação do usuário"""
        try:
            log_agent_action("manager", "create_task", {"user_text": user_text})
            
            # Gerar especificação técnica
            spec = llm_service.json_spec(user_text, project_config.model_dump())
            
            # Criar task
            task = Task(
                project=project_config.name,
                raw_request=user_text,
                objective=spec.objective,
                context=f"Complexidade: {spec.estimated_complexity}"
            )
            
            # Gerar nome da branch
            slug = self._create_slug(spec.objective)
            task.branch_name = f"feat/{slug}-{task.id[:8]}"
            
            # Salvar task
            state_store.save_task(task)
            
            # Adicionar evento
            task.add_event("created", f"Task criada com objetivo: {spec.objective}")
            state_store.save_task(task)
            
            log_task_event(task.id, "task_created", f"Task {task.id} criada")
            
            return task
            
        except Exception as e:
            logger.error(f"Erro ao criar task: {e}")
            raise
    
    def review_and_iterate(self, task_id: str) -> Tuple[bool, str, Optional[str]]:
        """Revisa e itera sobre uma task"""
        try:
            log_agent_action("manager", "review_and_iterate", {"task_id": task_id})
            
            # Recuperar task
            task = state_store.get_task(task_id)
            if not task:
                return False, "Task não encontrada", None
            
            # Recuperar configuração do projeto
            project_config = state_store.get_project(task.project)
            if not project_config:
                return False, "Configuração do projeto não encontrada", None
            
            # Atualizar status
            task.status = TaskStatus.IN_PROGRESS
            task.add_event("started", "Iniciando implementação")
            state_store.save_task(task)
            
            # Implementar via agente programador
            if not self.programmer_agent:
                return False, "Agente programador não configurado", None
            
            success, test_output, repo_path, diff = self.programmer_agent.implement(
                task, project_config, task.branch_name
            )
            
            if not success:
                task.status = TaskStatus.FAILED
                task.add_event("failed", f"Implementação falhou: {test_output}")
                state_store.save_task(task)
                return False, f"Implementação falhou: {test_output}", None
            
            # Revisar implementação
            spec_data = {
                "objective": task.objective,
                "acceptance_criteria": project_config.acceptance_checks
            }
            
            # Obter log do git
            git_log = self._get_git_log(repo_path, task.branch_name)
            
            review_result = llm_service.review(
                spec_data, test_output, git_log, diff
            )
            
            # Atualizar task com resultado da revisão
            task.add_event("reviewed", f"Revisão: {'Aprovado' if review_result.approved else 'Reprovado'}")
            
            if review_result.approved:
                # Push e criar PR
                pr_url = self.programmer_agent.push_and_pr(task, project_config)
                
                task.status = TaskStatus.DONE
                task.add_event("completed", f"Task concluída. PR: {pr_url}")
                state_store.save_task(task)
                
                return True, f"Task aprovada! PR criado: {pr_url}", pr_url
            else:
                # Task reprovada - retornar feedback
                task.status = TaskStatus.REVIEW
                task.add_event("rejected", f"Revisão reprovada: {review_result.notes}")
                state_store.save_task(task)
                
                feedback = f"Revisão reprovada: {review_result.notes}"
                if review_result.next_actions:
                    feedback += f"\n\nPróximas ações: {review_result.next_actions}"
                
                return False, feedback, None
                
        except Exception as e:
            logger.error(f"Erro na revisão e iteração: {e}")
            return False, f"Erro interno: {str(e)}", None
    
    def _create_slug(self, text: str) -> str:
        """Cria um slug a partir do texto"""
        # Converter para minúsculas e substituir espaços por hífens
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:30]  # Limitar tamanho
    
    def _get_git_log(self, repo_path, branch_name: str) -> str:
        """Obtém log do git para a branch"""
        try:
            import git
            repo = git.Repo(repo_path)
            
            # Obter commits da branch
            commits = list(repo.iter_commits(branch_name, max_count=5))
            
            log_lines = []
            for commit in commits:
                log_lines.append(f"Commit: {commit.hexsha[:8]} - {commit.message.strip()}")
            
            return "\n".join(log_lines)
            
        except Exception as e:
            logger.warning(f"Erro ao obter git log: {e}")
            return "Git log não disponível"

# Instância global
manager_agent = ManagerAgent()
