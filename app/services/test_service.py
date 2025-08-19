import subprocess
import time
from pathlib import Path
from typing import Tuple, Optional
import structlog

logger = structlog.get_logger(__name__)

class TestService:
    """Serviço para executar testes"""
    
    def run_tests(self, repo_root: Path, test_command: str, timeout: int = 300) -> Tuple[bool, str]:
        """Executa testes com timeout e captura de output"""
        try:
            logger.info(f"Executando testes: {test_command} em {repo_root}")
            
            # Verificar se o diretório existe
            if not repo_root.exists():
                return False, f"Diretório {repo_root} não existe"
            
            # Executar comando de teste
            result = subprocess.run(
                test_command.split(),
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Capturar output
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            combined_output = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
            
            # Verificar resultado
            if result.returncode == 0:
                logger.info("Testes executados com sucesso")
                return True, combined_output
            else:
                logger.warning(f"Testes falharam com código {result.returncode}")
                return False, combined_output
                
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout de {timeout}s excedido ao executar testes"
            logger.error(error_msg)
            return False, error_msg
            
        except FileNotFoundError as e:
            error_msg = f"Comando não encontrado: {e}"
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Erro ao executar testes: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def run_specific_test(self, repo_root: Path, test_file: str, test_function: Optional[str] = None) -> Tuple[bool, str]:
        """Executa um teste específico"""
        try:
            test_path = repo_root / test_file
            
            if not test_path.exists():
                return False, f"Arquivo de teste {test_file} não encontrado"
            
            # Construir comando
            if test_function:
                cmd = f"pytest -xvs {test_file}::{test_function}"
            else:
                cmd = f"pytest -xvs {test_file}"
            
            return self.run_tests(repo_root, cmd)
            
        except Exception as e:
            error_msg = f"Erro ao executar teste específico: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def check_test_environment(self, repo_root: Path) -> Tuple[bool, str]:
        """Verifica se o ambiente de testes está configurado"""
        try:
            # Verificar se existe requirements.txt ou pyproject.toml
            requirements_files = ['requirements.txt', 'pyproject.toml', 'setup.py']
            found_files = []
            
            for file_name in requirements_files:
                if (repo_root / file_name).exists():
                    found_files.append(file_name)
            
            if not found_files:
                return False, "Nenhum arquivo de dependências encontrado"
            
            # Verificar se pytest está disponível
            try:
                result = subprocess.run(
                    ['pytest', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return True, f"Ambiente de testes OK. Arquivos encontrados: {', '.join(found_files)}"
                else:
                    return False, "pytest não está disponível"
                    
            except FileNotFoundError:
                return False, "pytest não está instalado"
                
        except Exception as e:
            return False, f"Erro ao verificar ambiente: {str(e)}"
    
    def install_dependencies(self, repo_root: Path) -> Tuple[bool, str]:
        """Instala dependências do projeto"""
        try:
            # Verificar se existe requirements.txt
            requirements_file = repo_root / "requirements.txt"
            if requirements_file.exists():
                logger.info("Instalando dependências do requirements.txt")
                
                result = subprocess.run(
                    ['pip', 'install', '-r', 'requirements.txt'],
                    cwd=repo_root,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    return True, "Dependências instaladas com sucesso"
                else:
                    return False, f"Erro ao instalar dependências: {result.stderr}"
            
            # Verificar se existe pyproject.toml
            pyproject_file = repo_root / "pyproject.toml"
            if pyproject_file.exists():
                logger.info("Instalando dependências do pyproject.toml")
                
                result = subprocess.run(
                    ['pip', 'install', '-e', '.'],
                    cwd=repo_root,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    return True, "Dependências instaladas com sucesso"
                else:
                    return False, f"Erro ao instalar dependências: {result.stderr}"
            
            return False, "Nenhum arquivo de dependências encontrado"
            
        except Exception as e:
            return False, f"Erro ao instalar dependências: {str(e)}"

# Instância global
test_service = TestService()
