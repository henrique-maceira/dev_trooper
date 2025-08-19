# Dev Trooper - Sistema Multi-Agentes para Desenvolvimento Assistido por IA

🤖 Um orquestrador de agentes inteligentes que automatiza o processo de desenvolvimento de software, desde a análise de requisitos até a criação de Pull Requests.

## 🎯 Objetivo

O Dev Trooper é um sistema multi-agentes que recebe solicitações via Telegram e automaticamente:

1. **Analisa** a solicitação do usuário
2. **Gera** especificação técnica detalhada
3. **Implementa** as mudanças no código
4. **Executa** testes automatizados
5. **Revisa** a implementação
6. **Cria** Pull Request no GitHub

## 🏗️ Arquitetura

### Agentes

- **Agente Gerente**: Coordena o processo, gera especificações e revisa implementações
- **Agente Programador**: Implementa mudanças no código e gerencia operações Git

### Serviços

- **LLM Service**: Integração com OpenAI para geração de código e revisão
- **GitHub Service**: Operações Git e GitHub (clone, branch, commit, PR)
- **Patch Service**: Aplicação de patches usando binário `patch` ou `unidiff`
- **Test Service**: Execução de testes com timeout e captura de output
- **Logging Service**: Logging estruturado em JSON

## 🚀 Setup Rápido

### Pré-requisitos

- Python 3.11+
- Git
- Binário `patch` (instalado via `apt-get install patch` no Ubuntu/Debian)

### Instalação Local

1. **Clone o repositório**
```bash
git clone <seu-repo>
cd dev_trooper
```

2. **Instale as dependências**
```bash
make install
```

3. **Configure as variáveis de ambiente**
```bash
cp env.example .env
# Edite .env com suas credenciais
```

4. **Verifique o binário patch**
```bash
make patch-bin
```

5. **Execute os testes**
```bash
make test
```

6. **Inicie o bot**
```bash
make run
```

### Docker

1. **Build da imagem**
```bash
make docker-build
```

2. **Configure .env e inicie**
```bash
make docker-up
```

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=<seu-token-do-bot>

# OpenAI
OPENAI_API_KEY=<sua-chave-api-openai>
DEFAULT_MODEL=gpt-4o-mini

# GitHub
GITHUB_TOKEN=<seu-token-github>

# Diretórios
WORKDIR_BASE=/tmp/dev_trooper
DEFAULT_GIT_AUTHOR="Agent Bot <agent@example.com>"
```

### Tokens Necessários

#### Telegram Bot Token
1. Fale com [@BotFather](https://t.me/botfather) no Telegram
2. Use `/newbot` para criar um novo bot
3. Copie o token fornecido

#### OpenAI API Key
1. Acesse [OpenAI Platform](https://platform.openai.com/api-keys)
2. Crie uma nova chave de API
3. Copie a chave

#### GitHub Token
1. Acesse [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Crie um novo token com permissões:
   - `repo` (acesso completo aos repositórios)
   - `workflow` (opcional, para GitHub Actions)

## 📱 Como Usar

### Comandos do Bot

#### Configuração
- `/projeto <nome>` - Cria ou seleciona um projeto
- `/repo <url>` - Define URL do repositório GitHub

#### Tarefas
- `/tarefa <descrição>` - Cria e executa uma nova tarefa
- `/status <task_id>` - Verifica status de uma tarefa

#### Informações
- `/start` - Instruções iniciais
- `/ajuda` - Mostra ajuda completa

### Exemplo de Uso

```
1. /projeto meu-app
2. /repo https://github.com/usuario/meu-app
3. /tarefa Adicionar autenticação JWT com refresh token
4. /status abc12345-def6-7890-ghij-klmnopqrstuv
```

### Fluxo Completo

1. **Criação do Projeto**: Define nome e configurações
2. **Configuração do Repo**: Aponta para repositório GitHub
3. **Criação da Tarefa**: Descreve funcionalidade desejada
4. **Processamento Automático**:
   - Análise da solicitação
   - Geração de especificação técnica
   - Implementação das mudanças
   - Execução de testes
   - Revisão da implementação
   - Criação de Pull Request

## 🧪 Testes

### Executar Todos os Testes
```bash
make test
```

### Testes Específicos
```bash
# Teste smoke
pytest tests/test_smoke.py -v

# Teste do state store
pytest tests/test_state_store.py -v
```

### Repositório de Exemplo
O sistema inclui um repositório de exemplo em `tests/fixtures/sample_repo/` com:
- Aplicação Python simples
- Testes pytest funcionais
- Estrutura de projeto completa

## 📁 Estrutura do Projeto

```
dev_trooper/
├── app/
│   ├── main.py              # Aplicação principal
│   ├── config.py            # Configurações
│   ├── telegram_bot.py      # Bot do Telegram
│   ├── models/              # Modelos de dados
│   │   ├── schemas.py       # Schemas Pydantic
│   │   └── state_store.py   # Persistência JSON
│   ├── agents/              # Agentes
│   │   ├── manager.py       # Agente gerente
│   │   └── programmer.py    # Agente programador
│   ├── services/            # Serviços
│   │   ├── llm_service.py   # Integração OpenAI
│   │   ├── github_service.py # Operações Git/GitHub
│   │   ├── patch_service.py # Aplicação de patches
│   │   ├── test_service.py  # Execução de testes
│   │   └── logging_service.py # Logging estruturado
│   └── utils/
│       └── prompts.py       # Templates de prompts
├── tests/                   # Testes
│   ├── test_smoke.py        # Teste smoke
│   ├── test_state_store.py  # Teste do state store
│   └── fixtures/
│       └── sample_repo/     # Repositório de exemplo
├── data/                    # Dados persistentes (criado automaticamente)
├── artifacts/               # Artefatos (diffs, logs)
├── requirements.txt         # Dependências Python
├── Makefile                 # Automação
├── Dockerfile               # Container Docker
├── docker-compose.yml       # Orquestração Docker
└── env.example              # Exemplo de configuração
```

## 🔧 Automação

### Comandos Make

```bash
make install        # Instala dependências
make run           # Executa aplicação
make test          # Executa testes
make lint          # Linting (se ruff disponível)
make patch-bin     # Verifica binário patch
make docker-build  # Build Docker
make docker-up     # Inicia containers
make docker-down   # Para containers
make clean         # Limpa arquivos temporários
make setup         # Setup completo
```

## 🔒 Segurança

### Tokens e Credenciais
- **NUNCA** commite tokens no repositório
- Use sempre arquivo `.env` para configurações
- Configure `.gitignore` para excluir `.env`

### Permissões GitHub
- Use tokens com escopo mínimo necessário
- Considere usar GitHub Apps para projetos empresariais
- Revogue tokens não utilizados

### Arquivos Sensíveis
O sistema inclui proteções básicas:
- Bloqueia alterações em `.github/workflows/` sem flag especial
- Valida diffs antes da aplicação
- Cria backups de patches aplicados

## 🚧 Limitações do MVP

### Funcionalidades Atuais
- ✅ Processamento síncrono (MVP)
- ✅ Loop de revisão simples (1 iteração)
- ✅ Persistência JSON
- ✅ Integração OpenAI
- ✅ Operações Git básicas

### Próximos Passos
- 🔄 Processamento assíncrono com filas
- 🔄 Múltiplas iterações de revisão
- 🔄 Persistência SQLite/PostgreSQL
- 🔄 Suporte a múltiplos provedores LLM
- 🔄 Interface web para monitoramento
- 🔄 Políticas de arquivos protegidos
- 🔄 Integração com linters
- 🔄 Retry automático em falhas
- 🔄 Métricas e analytics

## 🔄 Migração para SQLite

Para trocar JSON por SQLite:

1. **Instalar dependências**
```bash
pip install sqlmodel sqlite3
```

2. **Criar novo store**
```python
# app/models/sqlite_store.py
from sqlmodel import SQLModel, create_engine, Session
from .schemas import Task, ProjectConfig, UserSession

class SQLiteStateStore:
    def __init__(self, db_url: str = "sqlite:///data/dev_trooper.db"):
        self.engine = create_engine(db_url)
        SQLModel.metadata.create_all(self.engine)
    
    # Implementar métodos CRUD...
```

3. **Atualizar imports**
```python
# Substituir em app/models/state_store.py
from .sqlite_store import SQLiteStateStore as StateStore
```

## 🐛 Troubleshooting

### Problemas Comuns

#### "Binário patch não encontrado"
```bash
# Ubuntu/Debian
sudo apt-get install patch

# macOS
brew install patch

# Windows
# Instalar via Git Bash ou WSL
```

#### "Erro de autenticação OpenAI"
- Verifique se `OPENAI_API_KEY` está correto
- Confirme se a chave tem créditos disponíveis
- Teste com `curl` ou Python direto

#### "Erro de autenticação GitHub"
- Verifique se `GITHUB_TOKEN` está correto
- Confirme se o token tem permissões `repo`
- Teste com `gh auth status`

#### "Testes falham"
- Verifique se `pytest` está instalado
- Confirme se o repositório de exemplo está correto
- Execute `make test` para diagnóstico

### Logs

O sistema usa logging estruturado em JSON. Logs importantes:
- `task_events`: Eventos de tasks
- `agent_actions`: Ações dos agentes
- `errors`: Erros da aplicação

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/dev_trooper/issues)
- **Documentação**: Este README
- **Telegram**: Use `/ajuda` no bot

---

**Dev Trooper** - Transformando ideias em código, automaticamente! 🚀
