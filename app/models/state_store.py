import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog

from .schemas import Task, ProjectConfig, UserSession

logger = structlog.get_logger()

class JSONStateStore:
    """Store de estado usando JSON para persistência"""
    
    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        
        # Arquivos de dados
        self.tasks_file = self.data_dir / "tasks.json"
        self.projects_file = self.data_dir / "projects.json"
        self.sessions_file = self.data_dir / "sessions.json"
        
        # Inicializar arquivos se não existirem
        self._init_files()
    
    def _init_files(self):
        """Inicializa arquivos JSON se não existirem"""
        if not self.tasks_file.exists():
            self._save_json(self.tasks_file, {})
        
        if not self.projects_file.exists():
            self._save_json(self.projects_file, {})
        
        if not self.sessions_file.exists():
            self._save_json(self.sessions_file, {})
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Carrega dados de um arquivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning(f"Arquivo {file_path} não encontrado ou inválido, criando novo")
            return {}
    
    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Salva dados em um arquivo JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"Erro ao salvar {file_path}: {e}")
            raise
    
    # Métodos para Tasks
    def save_task(self, task: Task) -> bool:
        """Salva uma task"""
        try:
            tasks = self._load_json(self.tasks_file)
            tasks[task.id] = task.model_dump()
            self._save_json(self.tasks_file, tasks)
            logger.info(f"Task {task.id} salva com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar task {task.id}: {e}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Recupera uma task por ID"""
        try:
            tasks = self._load_json(self.tasks_file)
            if task_id in tasks:
                return Task(**tasks[task_id])
            return None
        except Exception as e:
            logger.error(f"Erro ao carregar task {task_id}: {e}")
            return None
    
    def get_tasks_by_project(self, project: str) -> List[Task]:
        """Recupera todas as tasks de um projeto"""
        try:
            tasks = self._load_json(self.tasks_file)
            project_tasks = []
            for task_data in tasks.values():
                if task_data.get('project') == project:
                    project_tasks.append(Task(**task_data))
            return project_tasks
        except Exception as e:
            logger.error(f"Erro ao carregar tasks do projeto {project}: {e}")
            return []
    
    def update_task_status(self, task_id: str, status: str) -> bool:
        """Atualiza o status de uma task"""
        try:
            tasks = self._load_json(self.tasks_file)
            if task_id in tasks:
                tasks[task_id]['status'] = status
                tasks[task_id]['updated_at'] = datetime.now().isoformat()
                self._save_json(self.tasks_file, tasks)
                logger.info(f"Status da task {task_id} atualizado para {status}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao atualizar status da task {task_id}: {e}")
            return False
    
    # Métodos para Projects
    def save_project(self, project: ProjectConfig) -> bool:
        """Salva uma configuração de projeto"""
        try:
            projects = self._load_json(self.projects_file)
            projects[project.name] = project.model_dump()
            self._save_json(self.projects_file, projects)
            logger.info(f"Projeto {project.name} salvo com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar projeto {project.name}: {e}")
            return False
    
    def get_project(self, project_name: str) -> Optional[ProjectConfig]:
        """Recupera uma configuração de projeto"""
        try:
            projects = self._load_json(self.projects_file)
            if project_name in projects:
                return ProjectConfig(**projects[project_name])
            return None
        except Exception as e:
            logger.error(f"Erro ao carregar projeto {project_name}: {e}")
            return None
    
    def list_projects(self) -> List[str]:
        """Lista todos os projetos"""
        try:
            projects = self._load_json(self.projects_file)
            return list(projects.keys())
        except Exception as e:
            logger.error(f"Erro ao listar projetos: {e}")
            return []
    
    # Métodos para Sessions
    def save_session(self, session: UserSession) -> bool:
        """Salva uma sessão de usuário"""
        try:
            sessions = self._load_json(self.sessions_file)
            sessions[str(session.user_id)] = session.model_dump()
            self._save_json(self.sessions_file, sessions)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar sessão do usuário {session.user_id}: {e}")
            return False
    
    def get_session(self, user_id: int) -> Optional[UserSession]:
        """Recupera uma sessão de usuário"""
        try:
            sessions = self._load_json(self.sessions_file)
            if str(user_id) in sessions:
                return UserSession(**sessions[str(user_id)])
            return None
        except Exception as e:
            logger.error(f"Erro ao carregar sessão do usuário {user_id}: {e}")
            return None
    
    def update_session_project(self, user_id: int, project_name: str) -> bool:
        """Atualiza o projeto atual de uma sessão"""
        try:
            sessions = self._load_json(self.sessions_file)
            user_key = str(user_id)
            
            if user_key in sessions:
                sessions[user_key]['current_project'] = project_name
                sessions[user_key]['last_activity'] = datetime.now().isoformat()
            else:
                sessions[user_key] = UserSession(
                    user_id=user_id,
                    current_project=project_name
                ).model_dump()
            
            self._save_json(self.sessions_file, sessions)
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar projeto da sessão do usuário {user_id}: {e}")
            return False

# Instância global
state_store = JSONStateStore()
