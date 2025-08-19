"""
Testes específicos para o state store
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.state_store import JSONStateStore
from app.models.schemas import ProjectConfig, Task, UserSession, TaskStatus

class TestJSONStateStore:
    """Testes para JSONStateStore"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Cria diretório temporário para dados de teste"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def state_store(self, temp_data_dir):
        """Cria instância do state store para teste"""
        return JSONStateStore(temp_data_dir)
    
    def test_init_files(self, state_store):
        """Testa inicialização dos arquivos"""
        assert state_store.tasks_file.exists()
        assert state_store.projects_file.exists()
        assert state_store.sessions_file.exists()
    
    def test_save_and_get_project(self, state_store):
        """Testa salvar e recuperar projeto"""
        project = ProjectConfig(
            name="test-project",
            repo_url="https://github.com/test/repo",
            default_branch="main",
            test_command="pytest"
        )
        
        # Salvar
        assert state_store.save_project(project)
        
        # Recuperar
        retrieved = state_store.get_project("test-project")
        assert retrieved is not None
        assert retrieved.name == "test-project"
        assert retrieved.repo_url == "https://github.com/test/repo"
        assert retrieved.default_branch == "main"
        assert retrieved.test_command == "pytest"
    
    def test_save_and_get_task(self, state_store):
        """Testa salvar e recuperar task"""
        task = Task(
            project="test-project",
            raw_request="Adicionar função de login",
            objective="Implementar autenticação JWT",
            context="Sistema de usuários"
        )
        
        # Salvar
        assert state_store.save_task(task)
        
        # Recuperar
        retrieved = state_store.get_task(task.id)
        assert retrieved is not None
        assert retrieved.project == "test-project"
        assert retrieved.raw_request == "Adicionar função de login"
        assert retrieved.objective == "Implementar autenticação JWT"
        assert retrieved.status == TaskStatus.PENDING
    
    def test_get_tasks_by_project(self, state_store):
        """Testa recuperar tasks por projeto"""
        # Criar tasks para diferentes projetos
        task1 = Task(project="project-a", raw_request="Task 1", objective="Obj 1")
        task2 = Task(project="project-a", raw_request="Task 2", objective="Obj 2")
        task3 = Task(project="project-b", raw_request="Task 3", objective="Obj 3")
        
        state_store.save_task(task1)
        state_store.save_task(task2)
        state_store.save_task(task3)
        
        # Recuperar tasks do project-a
        project_a_tasks = state_store.get_tasks_by_project("project-a")
        assert len(project_a_tasks) == 2
        assert all(task.project == "project-a" for task in project_a_tasks)
        
        # Recuperar tasks do project-b
        project_b_tasks = state_store.get_tasks_by_project("project-b")
        assert len(project_b_tasks) == 1
        assert project_b_tasks[0].project == "project-b"
    
    def test_update_task_status(self, state_store):
        """Testa atualização de status de task"""
        task = Task(project="test-project", raw_request="Test", objective="Test")
        state_store.save_task(task)
        
        # Atualizar status
        assert state_store.update_task_status(task.id, TaskStatus.IN_PROGRESS)
        
        # Verificar se foi atualizado
        retrieved = state_store.get_task(task.id)
        assert retrieved.status == TaskStatus.IN_PROGRESS
    
    def test_save_and_get_session(self, state_store):
        """Testa salvar e recuperar sessão"""
        session = UserSession(
            user_id=12345,
            current_project="test-project"
        )
        
        # Salvar
        assert state_store.save_session(session)
        
        # Recuperar
        retrieved = state_store.get_session(12345)
        assert retrieved is not None
        assert retrieved.user_id == 12345
        assert retrieved.current_project == "test-project"
    
    def test_update_session_project(self, state_store):
        """Testa atualização de projeto da sessão"""
        user_id = 12345
        
        # Atualizar projeto (cria sessão se não existir)
        assert state_store.update_session_project(user_id, "new-project")
        
        # Verificar se foi atualizado
        session = state_store.get_session(user_id)
        assert session is not None
        assert session.current_project == "new-project"
        
        # Atualizar novamente
        assert state_store.update_session_project(user_id, "another-project")
        session = state_store.get_session(user_id)
        assert session.current_project == "another-project"
    
    def test_list_projects(self, state_store):
        """Testa listagem de projetos"""
        # Criar projetos
        project1 = ProjectConfig(name="project-1", repo_url="https://github.com/test/repo1")
        project2 = ProjectConfig(name="project-2", repo_url="https://github.com/test/repo2")
        
        state_store.save_project(project1)
        state_store.save_project(project2)
        
        # Listar projetos
        projects = state_store.list_projects()
        assert "project-1" in projects
        assert "project-2" in projects
        assert len(projects) == 2
    
    def test_get_nonexistent_task(self, state_store):
        """Testa recuperar task que não existe"""
        task = state_store.get_task("nonexistent-id")
        assert task is None
    
    def test_get_nonexistent_project(self, state_store):
        """Testa recuperar projeto que não existe"""
        project = state_store.get_project("nonexistent-project")
        assert project is None
    
    def test_get_nonexistent_session(self, state_store):
        """Testa recuperar sessão que não existe"""
        session = state_store.get_session(99999)
        assert session is None
