import logging
import sys
from typing import Any, Dict
import structlog
from structlog.stdlib import LoggerFactory

def setup_logging():
    """Configura logging estruturado com JSON"""
    
    # Configurar structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configurar logging padrão
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    
    # Configurar níveis específicos
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("git").setLevel(logging.WARNING)

def get_logger(name: str = None) -> structlog.BoundLogger:
    """Retorna um logger configurado"""
    return structlog.get_logger(name)

def log_task_event(task_id: str, event_type: str, message: str, data: Dict[str, Any] = None):
    """Log específico para eventos de task"""
    logger = get_logger("task_events")
    logger.info(
        "Task event",
        task_id=task_id,
        event_type=event_type,
        message=message,
        data=data or {}
    )

def log_agent_action(agent_name: str, action: str, details: Dict[str, Any] = None):
    """Log específico para ações de agentes"""
    logger = get_logger("agent_actions")
    logger.info(
        "Agent action",
        agent=agent_name,
        action=action,
        details=details or {}
    )

def log_error(error: Exception, context: Dict[str, Any] = None):
    """Log específico para erros"""
    logger = get_logger("errors")
    logger.error(
        "Application error",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {}
    )
