# 🤖 Claude Code Implementation Guide - ChainGuard AI

## 🎯 Mission Statement
You are tasked with completing the **remaining 20%** of the ChainGuard AI Smart Contract Analysis & Security Auditor. The infrastructure is **80% complete** and production-ready. Your focus should be on implementing the specific business logic, AI/ML integrations, and frontend components.

## 📋 Project Overview

### **Purpose & Goals**
ChainGuard AI is a **professional-grade smart contract security auditing platform** that combines AI/ML with traditional security tools to provide comprehensive vulnerability analysis. The platform targets **security auditors, development teams, and DeFi protocols** who need enterprise-level security analysis with evidence-based findings and professional reporting.

### **Tech Stack**
- **Backend**: FastAPI + Python 3.11 + PostgreSQL + Redis + Celery
- **Frontend**: Next.js 14 + React 18 + TypeScript + Tailwind CSS + shadcn/ui
- **AI/ML**: LangGraph + OpenAI/Anthropic + pgvector + RAG
- **Security Tools**: Slither + Mythril + Echidna + Foundry (containerized)
- **Infrastructure**: Docker + Nginx + Prometheus + Grafana

### **Target Users**
- **Security Auditors**: Professional audit firms and independent auditors
- **Development Teams**: Smart contract developers and DevOps engineers
- **DeFi Protocols**: Teams requiring continuous security monitoring
- **Compliance Officers**: Organizations needing audit trail and reporting

## 📁 Folder & File Structure

### **Root Directory Structure**
```
chainguard-ai/
├── 📁 backend/                 # FastAPI backend application
│   ├── 📁 app/                # Main application code
│   │   ├── 📁 api/v1/         # API routes (✅ COMPLETE - DO NOT MODIFY)
│   │   ├── 📁 core/           # Core configuration (✅ COMPLETE - DO NOT MODIFY)
│   │   ├── 📁 models/         # Database models (✅ COMPLETE - DO NOT MODIFY)
│   │   ├── 📁 schemas/        # Pydantic schemas (✅ COMPLETE - DO NOT MODIFY)
│   │   ├── 📁 services/       # Business logic (🔄 IMPLEMENT THESE)
│   │   └── 📁 tasks/          # Background tasks (🔄 IMPLEMENT THESE)
│   ├── 📁 alembic/            # Database migrations
│   ├── 📄 requirements.txt    # Python dependencies
│   ├── 📄 Dockerfile          # Development container
│   └── 📄 Dockerfile.prod     # Production container
├── 📁 frontend/               # Next.js frontend application
│   ├── 📁 app/                # Next.js app directory
│   ├── 📁 components/         # React components (🔄 IMPLEMENT THESE)
│   ├── 📁 hooks/              # Custom React hooks (🔄 IMPLEMENT THESE)
│   ├── 📁 lib/                # Utility libraries
│   ├── 📁 store/              # Zustand state management (🔄 IMPLEMENT THESE)
│   ├── 📁 types/              # TypeScript definitions (✅ COMPLETE - DO NOT MODIFY)
│   └── 📄 package.json        # Node.js dependencies
├── 📁 ai/                     # AI/ML modules (🔄 IMPLEMENT THESE)
│   ├── 📁 langgraph/          # LangGraph orchestration
│   ├── 📁 rag/                # RAG implementation
│   └── 📁 security_tools/     # Security tool integrations
├── 📁 monitoring/             # Prometheus/Grafana configs
├── 📁 nginx/                  # Nginx configuration
├── 📄 docker-compose.yml      # Development environment
├── 📄 docker-compose.prod.yml # Production environment
└── 📄 README.md               # Project documentation
```

### **File Categories**

#### **✅ Core Logic (DO NOT MODIFY)**
- `backend/app/models/*.py` - Database models and relationships
- `backend/app/schemas/*.py` - Pydantic request/response schemas
- `backend/app/api/v1/*.py` - API route definitions
- `backend/app/core/*.py` - Configuration, database, security utilities
- `frontend/types/index.ts` - TypeScript type definitions
- `frontend/app/globals.css` - Global styles and theme

#### **🔄 Business Logic (IMPLEMENT THESE)**
- `backend/app/services/*.py` - Business logic services
- `backend/app/tasks/*.py` - Background task implementations
- `ai/langgraph/graphs/*.py` - LangGraph workflow definitions
- `ai/security_tools/*/integration.py` - Security tool integrations
- `ai/rag/*.py` - RAG implementation

#### **🔄 UI Components (IMPLEMENT THESE)**
- `frontend/components/*.tsx` - React components
- `frontend/hooks/*.ts` - Custom React hooks
- `frontend/store/*.ts` - Zustand state management
- `frontend/lib/api.ts` - API client implementation

#### **📋 Configuration (DO NOT MODIFY)**
- `docker-compose*.yml` - Container orchestration
- `alembic.ini` - Database migration config
- `nginx/nginx.conf` - Web server configuration
- `monitoring/prometheus.yml` - Metrics collection

#### **📄 Documentation (REFERENCE ONLY)**
- `README.md` - Project overview
- `API_SPEC.md` - API documentation
- `REPO_MAP.md` - Repository structure
- `CLAUDE.md` - This implementation guide

### **"Do Not Touch" Files**
- All files in `backend/app/models/` - Database models are complete
- All files in `backend/app/schemas/` - API schemas are complete
- All files in `backend/app/api/v1/` - API routes are complete
- All files in `backend/app/core/` - Core utilities are complete
- `frontend/types/index.ts` - TypeScript definitions are complete
- `frontend/app/globals.css` - Global styles are complete
- All Docker and configuration files

## 📝 Coding Conventions

### **Languages & Frameworks**
- **Backend**: Python 3.11 with FastAPI, SQLAlchemy, Pydantic
- **Frontend**: TypeScript with React 18, Next.js 14
- **Styling**: Tailwind CSS with shadcn/ui components
- **Database**: PostgreSQL with pgvector extension

### **Style Guides**
- **Python**: PEP 8 with Black formatter (line length: 88)
- **TypeScript**: ESLint with Airbnb config + Prettier
- **SQL**: PostgreSQL conventions with snake_case
- **CSS**: Tailwind utility-first approach

### **Naming Conventions**

#### **Python (Backend)**
```python
# Files: snake_case
analysis_service.py
security_tools.py

# Classes: PascalCase
class AnalysisService:
class SecurityToolIntegration:

# Functions: snake_case
def run_security_analysis():
def parse_slither_output():

# Variables: snake_case
analysis_run = AnalysisRun()
finding_data = parse_findings()

# Constants: UPPER_SNAKE_CASE
MAX_EXECUTION_TIME = 3600
DEFAULT_TIMEOUT = 300
```

#### **TypeScript (Frontend)**
```typescript
// Files: PascalCase for components, camelCase for utilities
Dashboard.tsx
useWebSocket.ts

// Components: PascalCase
export const AnalysisRun: React.FC<AnalysisRunProps> = () => {
export function ProjectList() {

// Hooks: camelCase with 'use' prefix
export const useWebSocket = () => {
export const useAnalysis = () => {

// Variables: camelCase
const analysisRun = useAnalysis();
const projectList = useProjects();

// Constants: UPPER_SNAKE_CASE
const MAX_RETRY_ATTEMPTS = 3;
const DEFAULT_TIMEOUT = 5000;
```

#### **Database**
```sql
-- Tables: snake_case
analysis_runs
security_findings
project_artifacts

-- Columns: snake_case
created_at
updated_at
is_active

-- Indexes: idx_tablename_columnname
idx_analysis_runs_status
idx_findings_severity
```

### **Commenting Standards**

#### **Python Docstrings**
```python
def run_security_analysis(
    project_id: str,
    analysis_profile: AnalysisProfile
) -> AnalysisRun:
    """
    Execute comprehensive security analysis on a smart contract project.
    
    Args:
        project_id: UUID of the project to analyze
        analysis_profile: Analysis configuration (quick/standard/comprehensive)
        
    Returns:
        AnalysisRun: The created analysis run with initial status
        
    Raises:
        ProjectNotFoundError: If project doesn't exist
        AnalysisConfigError: If profile configuration is invalid
        
    Example:
        >>> run = run_security_analysis("123e4567", AnalysisProfile.STANDARD)
        >>> print(run.status)
        'pending'
    """
```

#### **TypeScript Comments**
```typescript
/**
 * Custom hook for managing WebSocket connections to analysis runs
 * 
 * @param runId - The analysis run ID to connect to
 * @param onMessage - Callback for incoming messages
 * @returns WebSocket connection state and controls
 * 
 * @example
 * ```tsx
 * const { isConnected, sendMessage } = useWebSocket(runId, handleMessage);
 * ```
 */
export const useWebSocket = (
  runId: string,
  onMessage: (message: WebSocketMessage) => void
): WebSocketState => {
```

### **Import Organization**

#### **Python Imports**
```python
# Standard library imports
import asyncio
from datetime import datetime
from typing import List, Optional

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

# Local imports
from app.core.database import get_db
from app.models.project import Project, AnalysisRun
from app.schemas.project import AnalysisRunCreate, AnalysisRunResponse
```

#### **TypeScript Imports**
```typescript
// React and Next.js
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

// Third-party libraries
import { useQuery, useMutation } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';

// Local components and utilities
import { Button } from '@/components/ui/button';
import { useAnalysis } from '@/hooks/use-analysis';
import { AnalysisRun } from '@/types';
```

## 🛠️ Workflow & Tools

### **Local Development Setup**

#### **Prerequisites**
```bash
# Required software
- Docker & Docker Compose
- Node.js 18+ and npm
- Python 3.11+ and pip
- Git

# Optional but recommended
- VS Code with extensions:
  - Python
  - TypeScript and JavaScript
  - Tailwind CSS IntelliSense
  - Docker
  - GitLens
```

#### **Quick Start**
```bash
# 1. Clone and setup
git clone <repository>
cd chainguard-ai

# 2. Start infrastructure
docker-compose up -d postgres redis

# 3. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head

# 4. Setup frontend
cd ../frontend
npm install
npm run dev

# 5. Start backend
cd ../backend
uvicorn app.main:app --reload --port 8000
```

#### **Development Workflow**
```bash
# Backend development
cd backend
# Edit Python files
# Run tests: python -m pytest
# Check formatting: black .
# Check linting: flake8

# Frontend development
cd frontend
# Edit TypeScript/React files
# Run tests: npm run test
# Check formatting: npm run format
# Check linting: npm run lint
```

### **Backend/Frontend Boundaries**

#### **Backend Responsibilities**
- **API Endpoints**: RESTful API with OpenAPI documentation
- **Database Operations**: CRUD operations with SQLAlchemy
- **Business Logic**: Analysis orchestration, security tool integration
- **Background Tasks**: Celery workers for long-running operations
- **Authentication**: JWT-based auth with RBAC
- **File Processing**: Upload handling, artifact management

#### **Frontend Responsibilities**
- **User Interface**: React components with TypeScript
- **State Management**: Zustand stores + React Query
- **Real-time Updates**: WebSocket connections
- **Code Display**: Monaco Editor integration
- **Reporting**: PDF/HTML report viewing
- **Search**: Semantic search interface

#### **Shared Responsibilities**
- **Type Safety**: Pydantic schemas ↔ TypeScript interfaces
- **Validation**: Backend validation + frontend form validation
- **Error Handling**: Consistent error responses and UI feedback

### **CI/CD Considerations**

#### **Development Workflow**
```bash
# Feature branch workflow
git checkout -b feature/analysis-orchestration
# Make changes
git add .
git commit -m "feat: implement LangGraph analysis orchestration"
git push origin feature/analysis-orchestration
# Create PR for review
```

#### **Testing Strategy**
```bash
# Backend testing
cd backend
python -m pytest tests/ -v --cov=app --cov-report=html

# Frontend testing
cd frontend
npm run test:coverage
npm run test:e2e  # End-to-end tests

# Integration testing
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

#### **Deployment Pipeline**
```bash
# Staging deployment
docker-compose -f docker-compose.staging.yml up -d

# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Health checks
curl http://localhost:8000/health
curl http://localhost:3000/api/health
```

## 📋 Examples

### **✅ Good Answer Example**

#### **Implementing a Service Class**
```python
"""
✅ GOOD: Well-structured service with proper error handling, logging, and type safety
"""

import structlog
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.project import AnalysisRun, Project
from app.schemas.project import AnalysisRunCreate, AnalysisRunResponse
from app.core.logging import log_analysis_event

logger = structlog.get_logger(__name__)

class AnalysisService:
    """Service for managing smart contract analysis operations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create_analysis_run(
        self, 
        project_id: str, 
        analysis_data: AnalysisRunCreate
    ) -> AnalysisRunResponse:
        """
        Create a new analysis run for a project.
        
        Args:
            project_id: UUID of the project
            analysis_data: Analysis configuration
            
        Returns:
            AnalysisRunResponse: Created analysis run
            
        Raises:
            HTTPException: If project not found or invalid configuration
        """
        try:
            # Validate project exists
            project = await self._get_project(project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project {project_id} not found"
                )
            
            # Create analysis run
            analysis_run = AnalysisRun(
                project_id=project_id,
                profile=analysis_data.profile,
                settings=analysis_data.settings,
                description=analysis_data.description,
                tags=analysis_data.tags
            )
            
            self.db.add(analysis_run)
            await self.db.commit()
            await self.db.refresh(analysis_run)
            
            # Log the event
            log_analysis_event(
                event_type="analysis_run_created",
                run_id=str(analysis_run.id),
                project_id=project_id,
                details={"profile": analysis_data.profile}
            )
            
            logger.info(
                "Analysis run created successfully",
                run_id=str(analysis_run.id),
                project_id=project_id,
                profile=analysis_data.profile
            )
            
            return AnalysisRunResponse.from_orm(analysis_run)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to create analysis run",
                project_id=project_id,
                error=str(e)
            )
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create analysis run"
            )
    
    async def _get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID."""
        result = await self.db.execute(
            "SELECT * FROM projects WHERE id = :project_id AND is_active = true",
            {"project_id": project_id}
        )
        return result.fetchone()
```

#### **Implementing a React Component**
```typescript
/**
 * ✅ GOOD: Well-structured React component with proper TypeScript, error handling, and accessibility
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { useAnalysis } from '@/hooks/use-analysis';
import { AnalysisRun, RunStatus } from '@/types';

interface AnalysisRunCardProps {
  runId: string;
  onStatusChange?: (status: RunStatus) => void;
}

export const AnalysisRunCard: React.FC<AnalysisRunCardProps> = ({
  runId,
  onStatusChange
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Use custom hook for data fetching
  const { data: analysisRun, isLoading, error } = useAnalysis(runId);
  
  // Handle status changes
  useEffect(() => {
    if (analysisRun?.status && onStatusChange) {
      onStatusChange(analysisRun.status);
    }
  }, [analysisRun?.status, onStatusChange]);
  
  // Handle errors
  useEffect(() => {
    if (error) {
      toast.error('Failed to load analysis run details');
    }
  }, [error]);
  
  if (isLoading) {
    return <AnalysisRunCardSkeleton />;
  }
  
  if (error || !analysisRun) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="p-4">
          <p className="text-red-600">Failed to load analysis run</p>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card className="transition-all hover:shadow-md">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">
            Analysis Run #{analysisRun.id.slice(0, 8)}
          </CardTitle>
          <StatusBadge status={analysisRun.status} />
        </div>
      </CardHeader>
      
      <CardContent className="space-y-3">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-600">Profile:</span>
            <span className="ml-2 capitalize">{analysisRun.profile}</span>
          </div>
          <div>
            <span className="font-medium text-gray-600">Progress:</span>
            <span className="ml-2">{Math.round(analysisRun.progress * 100)}%</span>
          </div>
        </div>
        
        {analysisRun.description && (
          <p className="text-sm text-gray-600">{analysisRun.description}</p>
        )}
        
        <div className="flex justify-between items-center">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            aria-expanded={isExpanded}
          >
            {isExpanded ? 'Show Less' : 'Show Details'}
          </Button>
          
          <span className="text-xs text-gray-500">
            Created {new Date(analysisRun.created_at).toLocaleDateString()}
          </span>
        </div>
      </CardContent>
    </Card>
  );
};

const StatusBadge: React.FC<{ status: RunStatus }> = ({ status }) => {
  const statusConfig = {
    pending: { color: 'bg-yellow-100 text-yellow-800', label: 'Pending' },
    running: { color: 'bg-blue-100 text-blue-800', label: 'Running' },
    completed: { color: 'bg-green-100 text-green-800', label: 'Completed' },
    failed: { color: 'bg-red-100 text-red-800', label: 'Failed' }
  };
  
  const config = statusConfig[status] || statusConfig.pending;
  
  return (
    <Badge className={config.color}>
      {config.label}
    </Badge>
  );
};

const AnalysisRunCardSkeleton: React.FC = () => (
  <Card>
    <CardHeader className="pb-3">
      <div className="flex items-center justify-between">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-6 w-20" />
      </div>
    </CardHeader>
    <CardContent className="space-y-3">
      <div className="grid grid-cols-2 gap-4">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-16" />
      </div>
      <Skeleton className="h-4 w-full" />
      <div className="flex justify-between">
        <Skeleton className="h-8 w-24" />
        <Skeleton className="h-4 w-20" />
      </div>
    </CardContent>
  </Card>
);
```

### **❌ Bad Answer Example**

#### **Poor Service Implementation**
```python
"""
❌ BAD: No error handling, no logging, no type hints, poor structure
"""

def create_run(project_id, data):
    # No validation
    run = AnalysisRun()
    run.project_id = project_id
    run.profile = data.profile
    # No error handling
    db.add(run)
    db.commit()
    return run
```

#### **Poor React Component**
```typescript
/**
 * ❌ BAD: No TypeScript, no error handling, no loading states, poor accessibility
 */

const AnalysisCard = ({ runId }) => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch(`/api/runs/${runId}`)
      .then(res => res.json())
      .then(setData);
  }, [runId]);
  
  return (
    <div>
      <h3>Run {data?.id}</h3>
      <p>Status: {data?.status}</p>
      <button onClick={() => console.log('clicked')}>
        View Details
      </button>
    </div>
  );
};
```

## 📋 Implementation Status

### **✅ Completed (80%) - DO NOT MODIFY**
- [x] **Database Models**: Complete SQLAlchemy models with relationships
- [x] **API Schemas**: Pydantic request/response models
- [x] **Authentication System**: JWT with RBAC and multi-tenancy
- [x] **Project Management**: CRUD operations and validation
- [x] **Analysis Framework**: Run management and status tracking
- [x] **Findings System**: Vulnerability tracking and metadata
- [x] **Security Infrastructure**: Rate limiting, validation, audit logs
- [x] **Frontend Foundation**: Next.js setup with security theme
- [x] **Type Safety**: Complete TypeScript definitions

### **🔄 Your Tasks (20%) - IMPLEMENT THESE**

## 🧠 AI/ML Integration Tasks

### **1. LangGraph Orchestration Setup**
**File**: `ai/langgraph/graphs/analysis_orchestrator.py`
```python
# Implement the main analysis orchestration graph
# Follow the pattern in the existing API routes
# Use the established database models and schemas
```

**Requirements**:
- Create LangGraph workflow for complete analysis pipeline
- Integrate with existing `AnalysisRun` model
- Use established checkpoint system for resumability
- Implement proper error handling and rollback

### **2. Security Tool Integration**
**Files**: 
- `ai/security_tools/slither/integration.py`
- `ai/security_tools/mythril/integration.py`
- `ai/security_tools/echidna/integration.py`
- `ai/security_tools/foundry/integration.py`

**Requirements**:
- Containerized execution for security
- Parse outputs to normalized finding schema
- Integrate with existing `Finding` model
- Handle tool failures gracefully

### **3. RAG Implementation**
**Files**:
- `ai/rag/embeddings/generator.py`
- `ai/rag/retrieval/vector_search.py`
- `ai/rag/knowledge_base/swc_docs.py`

**Requirements**:
- Use pgvector for embeddings storage
- Implement semantic search across findings
- Index SWC and OZ documentation
- Follow existing API patterns

## 🎨 Frontend Component Tasks

### **4. React Components**
**Files**:
- `frontend/components/dashboard/Dashboard.tsx`
- `frontend/components/projects/ProjectList.tsx`
- `frontend/components/analysis/AnalysisRun.tsx`
- `frontend/components/findings/FindingDetail.tsx`
- `frontend/components/reports/ReportViewer.tsx`

**Requirements**:
- Use established TypeScript types from `frontend/types/index.ts`
- Follow the security theme in `frontend/app/globals.css`
- Implement responsive design with Tailwind CSS
- Use shadcn/ui components for consistency

### **5. Monaco Editor Integration**
**File**: `frontend/components/code-editor/SolidityEditor.tsx`
```typescript
// Implement Monaco Editor wrapper for Solidity code viewing
// Include syntax highlighting, line numbers, and diff viewing
// Integrate with finding code spans
```

### **6. Real-time WebSocket Integration**
**File**: `frontend/hooks/use-websocket.ts`
```typescript
// Implement WebSocket hook for real-time updates
// Handle analysis progress, finding updates, and notifications
// Use established WebSocket message types
```

## 🔧 Backend Service Tasks

### **7. Analysis Service Implementation**
**File**: `backend/app/services/analysis_service.py`
```python
# Implement the business logic for analysis orchestration
# Integrate with LangGraph workflows
# Handle analysis state management
# Use existing database models and schemas
```

### **8. Report Generation Service**
**File**: `backend/app/services/report_service.py`
```python
# Implement PDF/HTML report generation
# Use existing artifact system
# Include findings, evidence, and patches
# Follow established patterns
```

### **9. Search Service Implementation**
**File**: `backend/app/services/search_service.py`
```python
# Implement semantic search using pgvector
# Search across code, findings, and reports
# Use existing API patterns and schemas
```

## 📊 Data & State Management

### **10. Zustand Store Implementation**
**Files**:
- `frontend/store/auth-store.ts`
- `frontend/store/project-store.ts`
- `frontend/store/analysis-store.ts`

**Requirements**:
- Use established TypeScript types
- Implement proper state management
- Handle loading states and errors
- Follow React Query patterns

### **11. React Query Integration**
**File**: `frontend/lib/api.ts`
```typescript
// Implement API client with React Query
// Use established API endpoints and schemas
// Handle authentication and error states
// Implement proper caching strategies
```

## 🚀 Implementation Guidelines

### **Code Quality Standards**
1. **Follow Existing Patterns**: Use the established code patterns and conventions
2. **Type Safety**: Maintain 100% TypeScript coverage
3. **Error Handling**: Implement comprehensive error handling
4. **Testing**: Write unit and integration tests
5. **Documentation**: Add clear docstrings and comments

### **Security Requirements**
1. **Input Validation**: Use existing Pydantic schemas
2. **Authentication**: Leverage established JWT system
3. **Authorization**: Use RBAC patterns
4. **Sanitization**: Follow existing security utilities
5. **Audit Logging**: Use established audit system

### **Performance Requirements**
1. **Async Operations**: Use async/await throughout
2. **Caching**: Implement Redis caching where appropriate
3. **Pagination**: Use existing pagination patterns
4. **Optimization**: Follow established performance patterns

### **UI/UX Standards**
1. **Security Theme**: Use established color scheme and components
2. **Responsive Design**: Mobile-first approach
3. **Accessibility**: WCAG 2.1 AA compliance
4. **Loading States**: Implement proper loading indicators
5. **Error States**: User-friendly error messages

## 🔒 Critical Security & Technical Considerations

### **Deterministic Pipeline Requirements**
- **Same Input → Same Output**: Analysis runs must be deterministic within tolerance
- **Checkpointing**: Implement resumable analysis with progress persistence
- **Tool Version Locking**: Pin exact versions of security tools (Slither, Mythril, etc.)
- **Seed Management**: Consistent random seeds for fuzzing and symbolic execution

### **Evidence & Reproducibility**
- **PoC Generation**: Every High/Critical finding must include reproducible proof-of-concept
- **Test Scaffolding**: Auto-generate failing tests that reproduce vulnerabilities
- **Trace Capture**: Store execution traces for complex vulnerabilities
- **Artifact Signing**: Cryptographic signatures for all analysis artifacts

### **Container Security**
- **Sandboxed Execution**: All security tools run in isolated Docker containers
- **Resource Limits**: CPU, memory, and time quotas for each tool
- **Network Isolation**: No external network access unless whitelisted
- **SBOM Tracking**: Software Bill of Materials for all tool images

### **Multi-Engine Consensus**
- **Tool Orchestration**: Coordinate Slither, Mythril, Echidna, Foundry for comprehensive coverage
- **Deduplication**: Merge findings from multiple engines with confidence scoring
- **False Positive Reduction**: Use consensus across tools to reduce noise
- **Severity Calibration**: Cross-reference with SWC database for accurate severity

### **Economic & Protocol Risk Analysis**
- **Oracle Manipulation**: Detect price oracle drift and manipulation vectors
- **MEV Analysis**: Identify sandwich attack and frontrunning opportunities
- **Liquidity Analysis**: Check for griefing and liquidation edge cases
- **Gas Optimization**: Function-level gas profiling and optimization suggestions

## 🎨 Advanced UI/UX Requirements

### **Security-First Design Language**
- **Severity Color Coding**: Critical (red), High (orange), Medium (yellow), Low (blue), Info (gray)
- **Code Visualization**: Syntax-highlighted Solidity with vulnerability overlays
- **Diff Viewing**: Side-by-side code comparison with patch suggestions
- **Trace Visualization**: Interactive execution traces for complex vulnerabilities

### **Real-Time Analysis Experience**
- **Live Progress**: WebSocket-driven real-time analysis progress updates
- **Intermediate Results**: Show findings as they're discovered, not just at completion
- **Pause/Resume**: Allow users to pause and resume long-running analyses
- **Resource Monitoring**: Show CPU, memory, and time usage during analysis

### **Evidence Presentation**
- **PoC Playground**: Interactive environment to run proof-of-concept exploits
- **Test Runner**: Built-in test execution for generated vulnerability tests
- **Trace Explorer**: Step-through execution traces with variable inspection
- **Screenshot Capture**: Automatic screenshots of failing test executions

### **Professional Reporting Interface**
- **Report Builder**: Drag-and-drop report section editor
- **Template System**: Pre-built templates for different audit types
- **Digital Signatures**: Cryptographic signing of audit reports
- **Version Control**: Track changes between audit versions

### **Advanced Search & Discovery**
- **Semantic Search**: Natural language queries across code and findings
- **Pattern Matching**: Find similar vulnerability patterns across projects
- **SWC Integration**: Direct links to SWC database with explanations
- **Historical Analysis**: Compare findings across project versions

## 🔧 Technical Architecture Deep Dive

### **LangGraph Orchestration Patterns**
- **State Management**: Persistent state across analysis stages
- **Error Recovery**: Graceful handling of tool failures with retry logic
- **Parallel Execution**: Concurrent tool execution where possible
- **Progress Tracking**: Granular progress updates for each analysis stage

### **Database Optimization**
- **Vector Embeddings**: Efficient storage and retrieval of code embeddings
- **JSONB Indexing**: Optimize storage layout and storage layout diff queries
- **Partitioning**: Partition large tables by tenant and date
- **Connection Pooling**: Optimize database connection management

### **Caching Strategy**
- **Multi-Level Caching**: Redis for sessions, PostgreSQL for persistent data
- **Tool Result Caching**: Cache analysis results to avoid re-computation
- **Embedding Cache**: Cache vector embeddings for similar code patterns
- **Report Cache**: Cache generated reports with TTL

### **File Storage Architecture**
- **Artifact Management**: Efficient storage of traces, PDFs, and binary artifacts
- **Version Control**: Track changes in uploaded contracts and dependencies
- **Compression**: Compress large artifacts (traces, coverage data)
- **CDN Integration**: Fast delivery of static assets and reports

## 🎯 Success Metrics & Quality Gates

### **Performance SLOs**
- **99.9% Uptime**: High availability for production deployments
- **P95 API Response < 300ms**: Fast API response times
- **Analysis Completion**: Typical project completes within configured time budget
- **Concurrent Runs**: Support multiple concurrent analysis runs per tenant

### **Quality Metrics**
- **False Positive Rate**: < 10% false positive rate on critical findings
- **False Negative Rate**: < 5% false negative rate on known vulnerabilities
- **Determinism**: 100% deterministic results for same input
- **Coverage**: > 95% code coverage for security-critical functions

### **User Experience Metrics**
- **Time to First Finding**: < 5 minutes for initial findings
- **Report Generation**: < 30 seconds for PDF/HTML report generation
- **Search Performance**: < 100ms for semantic search queries
- **UI Responsiveness**: < 16ms for UI interactions

## 🚨 Critical Implementation Notes

### **DO NOT COMPROMISE ON**
1. **Security**: All code must follow security best practices
2. **Determinism**: Analysis results must be reproducible
3. **Evidence**: Every finding must have concrete proof
4. **Performance**: Meet all specified SLOs
5. **Usability**: Professional-grade user experience

### **MUST IMPLEMENT**
1. **Container Security**: Sandboxed tool execution
2. **Evidence Generation**: PoC tests and execution traces
3. **Real-time Updates**: WebSocket progress tracking
4. **Professional UI**: Security industry-standard interface
5. **Comprehensive Testing**: Unit, integration, and chaos testing

## 🎯 Implementation Priority

### **Phase 1: Core Functionality (Week 1)**
1. **LangGraph Orchestration** - Main analysis pipeline
2. **Security Tool Integration** - Slither, Mythril, Echidna
3. **Basic Frontend Components** - Dashboard, Project List

### **Phase 2: Advanced Features (Week 2)**
1. **RAG Implementation** - Semantic search
2. **Report Generation** - PDF/HTML reports
3. **Real-time Updates** - WebSocket integration

### **Phase 3: Polish & Optimization (Week 3)**
1. **Advanced UI Components** - Monaco Editor, charts
2. **Performance Optimization** - Caching, pagination
3. **Testing & Documentation** - Comprehensive testing

## 🔍 Key Files to Reference

### **Database Models** (Established - DO NOT MODIFY)
- `backend/app/models/base.py` - Base model classes
- `backend/app/models/auth.py` - User, tenant, role models
- `backend/app/models/project.py` - Project, analysis, findings models

### **API Schemas** (Established - DO NOT MODIFY)
- `backend/app/schemas/auth.py` - Authentication schemas
- `backend/app/schemas/project.py` - Project and analysis schemas

### **API Routes** (Established - DO NOT MODIFY)
- `backend/app/api/v1/auth.py` - Authentication endpoints
- `backend/app/api/v1/projects.py` - Project management endpoints

### **Frontend Foundation** (Established - DO NOT MODIFY)
- `frontend/types/index.ts` - Complete TypeScript definitions
- `frontend/app/globals.css` - Security theme and components
- `frontend/lib/utils.ts` - Utility functions

## 🛠️ Development Environment

### **Prerequisites**
```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head

# Frontend
cd frontend
npm install
npm run dev

# Start services
docker-compose up -d
```

### **Testing**
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm run test
```

## 📚 Resources

### **Documentation**
- **REPO_MAP.md** - Complete repository structure
- **API_SPEC.md** - Detailed API documentation
- **README.md** - Project overview and setup

### **External Resources**
- **LangGraph Documentation** - https://langchain-ai.github.io/langgraph/
- **Monaco Editor** - https://microsoft.github.io/monaco-editor/
- **shadcn/ui** - https://ui.shadcn.com/
- **Tailwind CSS** - https://tailwindcss.com/

## 🎯 Success Criteria

### **Functional Requirements**
- [ ] Complete analysis pipeline with LangGraph
- [ ] Security tool integration (Slither, Mythril, Echidna)
- [ ] Semantic search with pgvector
- [ ] Real-time WebSocket updates
- [ ] PDF/HTML report generation
- [ ] Responsive frontend components

### **Quality Requirements**
- [ ] 100% TypeScript coverage
- [ ] Comprehensive error handling
- [ ] Unit and integration tests
- [ ] Performance optimization
- [ ] Security compliance
- [ ] Accessibility standards

### **User Experience**
- [ ] Intuitive navigation
- [ ] Fast loading times
- [ ] Real-time progress updates
- [ ] Professional security product aesthetics
- [ ] Mobile-responsive design

## 🚨 Important Notes

1. **DO NOT MODIFY** the established infrastructure (80% complete)
2. **FOLLOW PATTERNS** from existing code
3. **USE ESTABLISHED TYPES** and schemas
4. **MAINTAIN SECURITY** standards throughout
5. **TEST THOROUGHLY** before submitting
6. **DOCUMENT CHANGES** clearly

## 🎯 Final Deliverable

Your implementation should result in a **fully functional** ChainGuard AI application with:
- Complete smart contract analysis pipeline
- Professional security-themed UI
- Real-time progress tracking
- Comprehensive reporting system
- Semantic search capabilities
- Production-ready deployment

**Remember**: You're building on a solid foundation. Focus on the business logic and user experience while leveraging the established infrastructure! 🚀
