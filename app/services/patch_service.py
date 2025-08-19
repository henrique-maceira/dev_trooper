import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, Optional
import unidiff
import structlog

logger = structlog.get_logger(__name__)

class PatchService:
    """Serviço para aplicar patches"""
    
    def apply_unified_diff(self, diff_content: str, repo_path: Path) -> Tuple[bool, str]:
        """Aplica um diff unificado usando binário patch ou unidiff"""
        
        # Primeiro tenta com binário patch
        success, error = self._apply_with_binary_patch(diff_content, repo_path)
        if success:
            return True, "Patch aplicado com sucesso usando binário patch"
        
        # Fallback para unidiff
        logger.warning(f"Binário patch falhou: {error}. Tentando com unidiff...")
        success, error = self._apply_with_unidiff(diff_content, repo_path)
        
        if success:
            return True, "Patch aplicado com sucesso usando unidiff"
        else:
            return False, f"Falha ao aplicar patch: {error}"
    
    def _apply_with_binary_patch(self, diff_content: str, repo_path: Path) -> Tuple[bool, str]:
        """Aplica patch usando binário patch do sistema"""
        try:
            # Criar arquivo temporário com o diff
            with tempfile.NamedTemporaryFile(mode='w', suffix='.diff', delete=False) as f:
                f.write(diff_content)
                diff_file = f.name
            
            try:
                # Executar comando patch
                result = subprocess.run(
                    ['patch', '-p0', '-i', diff_file],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    return True, ""
                else:
                    return False, f"patch retornou código {result.returncode}: {result.stderr}"
                    
            finally:
                # Limpar arquivo temporário
                Path(diff_file).unlink(missing_ok=True)
                
        except FileNotFoundError:
            return False, "Binário patch não encontrado no sistema"
        except subprocess.TimeoutExpired:
            return False, "Timeout ao aplicar patch"
        except Exception as e:
            return False, f"Erro ao aplicar patch: {str(e)}"
    
    def _apply_with_unidiff(self, diff_content: str, repo_path: Path) -> Tuple[bool, str]:
        """Aplica patch usando biblioteca unidiff (fallback)"""
        try:
            # Parse do diff
            patch_set = unidiff.PatchSet.from_string(diff_content)
            
            for patched_file in patch_set:
                file_path = repo_path / patched_file.path
                
                # Criar diretório se não existir
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Ler arquivo original se existir
                original_content = ""
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                
                # Aplicar patches
                lines = original_content.splitlines(True)
                
                for hunk in patched_file:
                    # Aplicar hunk
                    lines = self._apply_hunk(lines, hunk)
                
                # Escrever arquivo modificado
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
            
            return True, ""
            
        except Exception as e:
            return False, f"Erro ao aplicar patch com unidiff: {str(e)}"
    
    def _apply_hunk(self, lines: list, hunk) -> list:
        """Aplica um hunk específico às linhas"""
        # Converter para lista se necessário
        if isinstance(lines, str):
            lines = lines.splitlines(True)
        
        # Calcular posições
        start_line = hunk.source_start - 1  # 0-based
        end_line = start_line + hunk.source_length
        
        # Aplicar mudanças
        new_lines = lines[:start_line]
        
        for line in hunk:
            if line.line_type == unidiff.LINE_TYPE_EMPTY:
                continue
            elif line.line_type == unidiff.LINE_TYPE_ADDED:
                new_lines.append(line.value)
            elif line.line_type == unidiff.LINE_TYPE_REMOVED:
                continue  # Pular linha removida
            elif line.line_type == unidiff.LINE_TYPE_CONTEXT:
                new_lines.append(line.value)
        
        new_lines.extend(lines[end_line:])
        return new_lines
    
    def validate_diff(self, diff_content: str) -> Tuple[bool, str]:
        """Valida se um diff é válido"""
        try:
            # Tentar parse com unidiff
            unidiff.PatchSet.from_string(diff_content)
            return True, "Diff válido"
        except Exception as e:
            return False, f"Diff inválido: {str(e)}"
    
    def create_diff_backup(self, diff_content: str, task_id: str) -> Optional[Path]:
        """Cria backup do diff aplicado"""
        try:
            from ..config import config
            
            backup_dir = config.ARTIFACTS_DIR / "diffs"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_file = backup_dir / f"diff_{task_id}.patch"
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(diff_content)
            
            logger.info(f"Backup do diff salvo em: {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"Erro ao criar backup do diff: {e}")
            return None

# Instância global
patch_service = PatchService()
