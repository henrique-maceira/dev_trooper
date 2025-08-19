from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
import uuid

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    FAILED = "failed"

class ProjectConfig(BaseModel):
    """Configuração de um projeto"""
    name: str = Field(..., description="Nome do projeto")
    repo_url: str = Field(..., description="URL do repositório GitHub")
    default_branch: str = Field(default="main", description="Branch padrão")
    test_command: str = Field(default="pytest -q", description="Comando para executar testes")
    workdir: Optional[str] = Field(None, description="Diretório de trabalho")
    acceptance_checks: List[str] = Field(
        default=["tests_passed == True"], 
        description="Lista de expressões de aceitação"
    )

class TaskEvent(BaseModel):
    """Evento na história de uma task"""
    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: str = Field(..., description="Tipo do evento")
    message: str = Field(..., description="Mensagem do evento")
    data: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")

class Task(BaseModel):
    """Representa uma tarefa de desenvolvimento"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project: str = Field(..., description="Nome do projeto")
    raw_request: str = Field(..., description="Solicitação original do usuário")
    objective: str = Field(..., description="Objetivo da tarefa")
    context: Optional[str] = Field(None, description="Contexto adicional")
    branch_name: Optional[str] = Field(None, description="Nome da branch criada")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    history: List[TaskEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def add_event(self, event_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Adiciona um evento à história da task"""
        event = TaskEvent(event_type=event_type, message=message, data=data)
        self.history.append(event)
        self.updated_at = datetime.now()

class ReviewResult(BaseModel):
    """Resultado de uma revisão"""
    approved: bool = Field(..., description="Se a revisão foi aprovada")
    notes: str = Field(..., description="Notas da revisão")
    next_actions: Optional[str] = Field(None, description="Próximas ações sugeridas")

class LLMSpecification(BaseModel):
    """Especificação técnica gerada pelo LLM"""
    objective: str = Field(..., description="Objetivo claro da tarefa")
    impacted_areas: List[str] = Field(..., description="Áreas do código que serão impactadas")
    acceptance_criteria: List[str] = Field(..., description="Critérios de aceitação")
    step_plan: List[str] = Field(..., description="Plano de implementação")
    estimated_complexity: str = Field(default="medium", description="Complexidade estimada")

class UserSession(BaseModel):
    """Sessão do usuário no Telegram"""
    user_id: int = Field(..., description="ID do usuário no Telegram")
    current_project: Optional[str] = Field(None, description="Projeto atualmente selecionado")
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
