import os
import re
from pathlib import Path
from typing import Optional
import git
from github import Github
import structlog

from ..config import config

logger = structlog.get_logger(__name__)

class GitHubService:
    """Serviço para operações Git e GitHub"""
    
    def __init__(self):
        self.github = Github(config.GITHUB_TOKEN)
        self.default_author = config.DEFAULT_GIT_AUTHOR
    
    def _extract_repo_name(self, repo_url: str) -> str:
        """Extrai nome completo do repositório da URL"""
        # Padrões: https://github.com/org/repo.git ou https://github.com/org/repo
        patterns = [
            r'github\.com[:/]([^/]+/[^/]+?)(?:\.git)?/?$',
            r'github\.com[:/]([^/]+/[^/]+?)/?$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, repo_url)
            if match:
                return match.group(1)
        
        raise ValueError(f"Não foi possível extrair nome do repositório de: {repo_url}")
    
    def clone_or_pull(self, repo_url: str, name: str) -> Path:
        """Clona ou atualiza um repositório"""
        try:
            workdir = config.WORKDIR_BASE / name
            
            if workdir.exists():
                # Pull se já existe
                repo = git.Repo(workdir)
                origin = repo.remotes.origin
                origin.pull()
                logger.info(f"Repositório {name} atualizado via pull")
            else:
                # Clone se não existe
                git.Repo.clone_from(repo_url, workdir)
                logger.info(f"Repositório {name} clonado")
            
            return workdir
            
        except Exception as e:
            logger.error(f"Erro ao clonar/pull repositório {name}: {e}")
            raise
    
    def create_branch(self, repo_path: Path, base_branch: str, new_branch: str) -> bool:
        """Cria uma nova branch"""
        try:
            repo = git.Repo(repo_path)
            
            # Verificar se estamos na branch base
            if repo.active_branch.name != base_branch:
                repo.git.checkout(base_branch)
                repo.git.pull()
            
            # Criar nova branch
            new_branch_ref = repo.create_head(new_branch)
            new_branch_ref.checkout()
            
            logger.info(f"Branch {new_branch} criada a partir de {base_branch}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar branch {new_branch}: {e}")
            return False
    
    def commit_all(self, repo_path: Path, message: str, author: Optional[str] = None) -> bool:
        """Comita todas as mudanças"""
        try:
            repo = git.Repo(repo_path)
            
            # Adicionar todas as mudanças
            repo.git.add('.')
            
            # Verificar se há mudanças para commitar
            if not repo.index.diff('HEAD'):
                logger.info("Nenhuma mudança para commitar")
                return True
            
            # Configurar autor se fornecido
            if author:
                repo.config_writer().set_value("user", "name", author.split('<')[0].strip())
                repo.config_writer().set_value("user", "email", author.split('<')[1].rstrip('>'))
            
            # Fazer commit
            repo.index.commit(message)
            logger.info(f"Commit realizado: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao fazer commit: {e}")
            return False
    
    def push_branch(self, repo_path: Path, branch: str) -> bool:
        """Push da branch para o repositório remoto"""
        try:
            repo = git.Repo(repo_path)
            origin = repo.remotes.origin
            
            # Push da branch
            origin.push(branch)
            logger.info(f"Branch {branch} enviada para o remoto")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao fazer push da branch {branch}: {e}")
            return False
    
    def open_pr(self, full_repo_name: str, title: str, head_branch: str, base: str, body: str) -> Optional[str]:
        """Abre um Pull Request no GitHub"""
        try:
            repo = self.github.get_repo(full_repo_name)
            
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base
            )
            
            logger.info(f"PR criado: {pr.html_url}")
            return pr.html_url
            
        except Exception as e:
            logger.error(f"Erro ao criar PR: {e}")
            return None
    
    def get_repo_map(self, repo_path: Path, max_files: int = 20, max_size_kb: int = 100) -> str:
        """Gera mapa do repositório para o LLM"""
        try:
            repo_map = []
            
            for file_path in repo_path.rglob('*'):
                if file_path.is_file():
                    # Ignorar arquivos e diretórios específicos
                    if any(part.startswith('.') for part in file_path.parts):
                        continue
                    
                    if file_path.name in ['__pycache__', 'node_modules', '.git']:
                        continue
                    
                    # Verificar tamanho
                    if file_path.stat().st_size > max_size_kb * 1024:
                        continue
                    
                    # Ler conteúdo do arquivo
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        relative_path = file_path.relative_to(repo_path)
                        repo_map.append(f"=== {relative_path} ===\n{content}\n")
                        
                        if len(repo_map) >= max_files:
                            break
                            
                    except (UnicodeDecodeError, PermissionError):
                        continue
            
            return "\n".join(repo_map)
            
        except Exception as e:
            logger.error(f"Erro ao gerar mapa do repositório: {e}")
            return ""

# Instância global
github_service = GitHubService()
