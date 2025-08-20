# 🛡️ ChainGuard AI — Smart Contract Analysis & Security Auditor

> Catch critical bugs before mainnet. Explain risks in plain English. Ship with confidence.

ChainGuard AI is a full-stack security workbench for EVM smart contracts. It ingests Solidity code (or an on-chain address), runs static analysis, fuzzing, symbolic execution, formal checks, and gas profiling in a deterministic pipeline, then produces a ranked findings report with proof of vulnerability artifacts, exploit repro snippets, and auto-generated patches—all mapped to SWC IDs and best practices.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+

### Development Setup

1. **Clone and Install Dependencies**
```bash
git clone <repository-url>
cd ai-smart-contract-analysis-and-security-auditor

# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
# Copy environment templates
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env

# Configure your environment variables
# See .env.example files for required variables
```

3. **Database Setup**
```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run database migrations
cd backend
alembic upgrade head
```

4. **Start Development Servers**
```bash
# Terminal 1: Frontend
cd frontend
npm run dev

# Terminal 2: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 3: Celery Workers
cd backend
celery -A app.celery_app worker --loglevel=info
```

## 🏗️ Architecture

### Frontend (Next.js 14)
- **Framework**: Next.js 14 with App Router
- **UI**: React 18, TypeScript, Tailwind CSS, shadcn/ui
- **State Management**: React Query, Zustand
- **Real-time**: WebSocket connections for live updates
- **Authentication**: JWT with refresh tokens

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.11+
- **Database**: SQLAlchemy 2.0 (async) with PostgreSQL
- **Validation**: Pydantic v2
- **Authentication**: JWT (access/refresh)
- **Caching**: Redis for queues and cache
- **Background Tasks**: Celery/Arq for tool runs

### AI/ML Infrastructure
- **Orchestration**: LangGraph for workflow management
- **LLM Integration**: OpenAI + Anthropic via LangChain
- **Tracing**: LangSmith for monitoring and evaluation
- **RAG**: Vector search over SWC + OpenZeppelin docs

### Security Tools Integration
- **Static Analysis**: Slither, custom detectors
- **Fuzzing**: Foundry fuzz/invariant tests, Echidna
- **Symbolic Execution**: Mythril/Manticore
- **Gas Analysis**: Forge snapshot, Hardhat gas reporter
- **On-chain**: Etherscan API, RPC providers, Tenderly

## 📁 Project Structure

```
├── frontend/                 # Next.js 14 frontend application
│   ├── app/                 # App Router pages and layouts
│   ├── components/          # Reusable UI components
│   ├── lib/                 # Utilities and configurations
│   ├── hooks/               # Custom React hooks
│   └── types/               # TypeScript type definitions
├── backend/                 # FastAPI backend application
│   ├── app/                 # Main application code
│   │   ├── api/            # API routes and endpoints
│   │   ├── core/           # Core configurations
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic services
│   │   └── workers/        # Background task workers
│   ├── alembic/            # Database migrations
│   └── tests/              # Backend tests
├── ai/                      # AI/ML infrastructure
│   ├── langgraph/          # LangGraph workflow definitions
│   ├── chains/             # LangChain integrations
│   └── embeddings/         # Vector embeddings and RAG
├── tools/                   # Security analysis tools
│   ├── containers/         # Docker containers for tools
│   ├── slither/            # Custom Slither rules
│   └── scripts/            # Analysis scripts
├── infrastructure/          # DevOps and deployment
│   ├── docker/             # Docker configurations
│   ├── k8s/                # Kubernetes manifests
│   └── monitoring/         # Monitoring and alerting
└── docs/                   # Documentation
```

## 🔧 Key Features

### Project Management
- Import via Git (Hardhat/Foundry), ZIP, or contract address
- Auto-detect compiler versions, libraries, and upgradeability patterns
- Multi-repo organization support with RBAC

### Analysis Pipeline
- **Static Analysis**: Rule engine + linters for common vulnerabilities
- **Fuzzing**: Property-based testing with invariant verification
- **Symbolic Execution**: Path exploration for edge cases
- **Economic Risk Analysis**: Oracle drift, MEV vectors, liquidation scenarios
- **Gas Profiling**: Function-level gas reports and optimization suggestions

### Security Copilot
- Plain English explanations for each finding
- Auto-generated patches with minimal diffs
- Context-aware suggestions based on your codebase
- SWC and OWASP mapping

### Reporting & Evidence
- Reproducible PoC scripts (Foundry/Hardhat)
- Signed audit reports (HTML/PDF)
- Tamper-evident artifacts with provenance
- Semantic search across code and findings

## 🛡️ Security Features

- **Tenant Isolation**: Complete data separation between organizations
- **Sandboxed Execution**: All tools run in isolated containers
- **Signed Artifacts**: Cryptographic verification of all outputs
- **Audit Trail**: Complete logging of all actions and decisions
- **RBAC**: Role-based access control with fine-grained permissions

## 📊 Performance & Reliability

- **SLOs**: 99.9% uptime, P95 API reads < 300ms
- **Deterministic Pipelines**: Same input → same findings ordering
- **Checkpointing**: Resume analysis from any point
- **Resource Limits**: CPU/memory/time quotas for all tools
- **Monitoring**: Comprehensive observability and alerting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.chainguard.ai](https://docs.chainguard.ai)
- **Discord**: [Join our community](https://discord.gg/chainguard)
- **Email**: support@chainguard.ai

---

**Built with ❤️ for the Web3 security community**
