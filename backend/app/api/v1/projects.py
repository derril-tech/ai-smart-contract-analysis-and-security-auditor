"""
Project API routes for ChainGuard AI
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from datetime import datetime

from app.core.database import get_db
from app.core.security import (
    get_current_user_id, get_current_tenant_id, get_current_user_permissions,
    log_security_event, get_client_ip, rate_limit, require_permission
)
from app.schemas.project import (
    ProjectCreate, ProjectResponse, ProjectUpdate, ProjectListResponse,
    AnalysisRunCreate, AnalysisRunResponse, AnalysisRunUpdate, AnalysisRunListResponse,
    FindingCreate, FindingResponse, FindingUpdate, FindingListResponse,
    ArtifactCreate, ArtifactResponse, ArtifactListResponse,
    CustomRuleCreate, CustomRuleResponse, CustomRuleUpdate, CustomRuleListResponse,
    SearchQuery, SearchResponse, DashboardStats, ProjectStats
)
from app.models.project import Project, Contract, AnalysisRun, Finding, Artifact, CustomRule
from app.models.base import TenantModel

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/projects", tags=["Projects"])

security = HTTPBearer()


@router.post("/", response_model=ProjectResponse)
@require_permission("project:write")
async def create_project(
    request: ProjectCreate,
    current_user_id: str = Depends(get_current_user_id),
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    try:
        # Check project limits for tenant
        result = await db.execute(
            "SELECT COUNT(*) FROM project WHERE tenant_id = :tenant_id AND status != 'deleted'",
            {"tenant_id": current_tenant_id}
        )
        project_count = result.scalar()
        
        # Get tenant limits
        tenant_result = await db.execute(
            "SELECT max_projects FROM tenant WHERE id = :tenant_id",
            {"tenant_id": current_tenant_id}
        )
        max_projects = tenant_result.scalar()
        
        if project_count >= max_projects:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project limit reached ({max_projects} projects)"
            )
        
        # Create project
        await db.execute(
            """
            INSERT INTO project (name, description, project_type, framework, source_url, 
                                contract_address, settings, tenant_id, status, created_by, 
                                created_at, updated_at)
            VALUES (:name, :description, :project_type, :framework, :source_url,
                    :contract_address, :settings, :tenant_id, 'active', :created_by,
                    NOW(), NOW())
            """,
            {
                "name": request.name,
                "description": request.description,
                "project_type": request.project_type,
                "framework": request.framework,
                "source_url": str(request.source_url) if request.source_url else None,
                "contract_address": request.contract_address,
                "settings": request.settings,
                "tenant_id": current_tenant_id,
                "created_by": current_user_id
            }
        )
        
        await db.commit()
        
        # Log project creation
        log_security_event(
            "project_created",
            current_user_id,
            current_tenant_id,
            {"project_name": request.name, "project_type": request.project_type}
        )
        
        # Return created project
        return ProjectResponse(
            id="new_project_id",  # Would be actual ID in real implementation
            name=request.name,
            description=request.description,
            project_type=request.project_type,
            framework=request.framework,
            source_url=request.source_url,
            contract_address=request.contract_address,
            settings=request.settings,
            tenant_id=current_tenant_id,
            status="active",
            contract_count=0,
            run_count=0,
            total_findings=0,
            critical_findings=0,
            high_findings=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Project creation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=ProjectListResponse)
@require_permission("project:read")
async def list_projects(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """List projects for the current tenant"""
    try:
        # Build query
        query = """
            SELECT p.*, 
                   COUNT(DISTINCT c.id) as contract_count,
                   COUNT(DISTINCT ar.id) as run_count,
                   COUNT(DISTINCT f.id) as total_findings,
                   SUM(CASE WHEN f.severity = 'critical' THEN 1 ELSE 0 END) as critical_findings,
                   SUM(CASE WHEN f.severity = 'high' THEN 1 ELSE 0 END) as high_findings,
                   MAX(ar.created_at) as last_run_at
            FROM project p
            LEFT JOIN contract c ON p.id = c.project_id
            LEFT JOIN analysisrun ar ON p.id = ar.project_id
            LEFT JOIN finding f ON ar.id = f.run_id
            WHERE p.tenant_id = :tenant_id
        """
        params = {"tenant_id": current_tenant_id}
        
        if status_filter:
            query += " AND p.status = :status"
            params["status"] = status_filter
        
        if search:
            query += " AND (p.name ILIKE :search OR p.description ILIKE :search)"
            params["search"] = f"%{search}%"
        
        query += " GROUP BY p.id ORDER BY p.updated_at DESC"
        
        # Get total count
        count_query = """
            SELECT COUNT(*) FROM project 
            WHERE tenant_id = :tenant_id
        """
        if status_filter:
            count_query += " AND status = :status"
        if search:
            count_query += " AND (name ILIKE :search OR description ILIKE :search)"
        
        count_result = await db.execute(count_query, params)
        total = count_result.scalar()
        
        # Get paginated results
        query += " LIMIT :limit OFFSET :offset"
        params["limit"] = size
        params["offset"] = (page - 1) * size
        
        result = await db.execute(query, params)
        projects_data = result.fetchall()
        
        # Convert to response models
        projects = []
        for project_data in projects_data:
            projects.append(ProjectResponse(
                id=project_data.id,
                name=project_data.name,
                description=project_data.description,
                project_type=project_data.project_type,
                framework=project_data.framework,
                source_url=project_data.source_url,
                contract_address=project_data.contract_address,
                settings=project_data.settings,
                tenant_id=project_data.tenant_id,
                status=project_data.status,
                contract_count=project_data.contract_count or 0,
                run_count=project_data.run_count or 0,
                last_run_at=project_data.last_run_at,
                total_findings=project_data.total_findings or 0,
                critical_findings=project_data.critical_findings or 0,
                high_findings=project_data.high_findings or 0,
                created_at=project_data.created_at,
                updated_at=project_data.updated_at
            ))
        
        return ProjectListResponse(
            projects=projects,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )
        
    except Exception as e:
        logger.error("Project list error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
@require_permission("project:read")
async def get_project(
    project_id: str,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Get project details"""
    try:
        result = await db.execute(
            """
            SELECT p.*, 
                   COUNT(DISTINCT c.id) as contract_count,
                   COUNT(DISTINCT ar.id) as run_count,
                   COUNT(DISTINCT f.id) as total_findings,
                   SUM(CASE WHEN f.severity = 'critical' THEN 1 ELSE 0 END) as critical_findings,
                   SUM(CASE WHEN f.severity = 'high' THEN 1 ELSE 0 END) as high_findings,
                   MAX(ar.created_at) as last_run_at
            FROM project p
            LEFT JOIN contract c ON p.id = c.project_id
            LEFT JOIN analysisrun ar ON p.id = ar.project_id
            LEFT JOIN finding f ON ar.id = f.run_id
            WHERE p.id = :project_id AND p.tenant_id = :tenant_id
            GROUP BY p.id
            """,
            {"project_id": project_id, "tenant_id": current_tenant_id}
        )
        
        project_data = result.fetchone()
        
        if not project_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return ProjectResponse(
            id=project_data.id,
            name=project_data.name,
            description=project_data.description,
            project_type=project_data.project_type,
            framework=project_data.framework,
            source_url=project_data.source_url,
            contract_address=project_data.contract_address,
            settings=project_data.settings,
            tenant_id=project_data.tenant_id,
            status=project_data.status,
            contract_count=project_data.contract_count or 0,
            run_count=project_data.run_count or 0,
            last_run_at=project_data.last_run_at,
            total_findings=project_data.total_findings or 0,
            critical_findings=project_data.critical_findings or 0,
            high_findings=project_data.high_findings or 0,
            created_at=project_data.created_at,
            updated_at=project_data.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Project get error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{project_id}", response_model=ProjectResponse)
@require_permission("project:write")
async def update_project(
    project_id: str,
    request: ProjectUpdate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Update project details"""
    try:
        # Check if project exists and belongs to tenant
        result = await db.execute(
            "SELECT id FROM project WHERE id = :project_id AND tenant_id = :tenant_id",
            {"project_id": project_id, "tenant_id": current_tenant_id}
        )
        
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Build update query
        update_fields = []
        params = {"project_id": project_id}
        
        if request.name is not None:
            update_fields.append("name = :name")
            params["name"] = request.name
        
        if request.description is not None:
            update_fields.append("description = :description")
            params["description"] = request.description
        
        if request.status is not None:
            update_fields.append("status = :status")
            params["status"] = request.status
        
        if request.settings is not None:
            update_fields.append("settings = :settings")
            params["settings"] = request.settings
        
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        update_fields.append("updated_at = NOW()")
        
        query = f"UPDATE project SET {', '.join(update_fields)} WHERE id = :project_id"
        await db.execute(query, params)
        
        await db.commit()
        
        # Return updated project
        return await get_project(project_id, current_tenant_id, db)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Project update error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{project_id}")
@require_permission("project:delete")
async def delete_project(
    project_id: str,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete project (soft delete)"""
    try:
        # Check if project exists and belongs to tenant
        result = await db.execute(
            "SELECT id FROM project WHERE id = :project_id AND tenant_id = :tenant_id",
            {"project_id": project_id, "tenant_id": current_tenant_id}
        )
        
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Soft delete
        await db.execute(
            "UPDATE project SET status = 'deleted', updated_at = NOW() WHERE id = :project_id",
            {"project_id": project_id}
        )
        
        await db.commit()
        
        return {"message": "Project deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Project delete error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Analysis Run endpoints
@router.post("/{project_id}/runs", response_model=AnalysisRunResponse)
@require_permission("analysis:write")
async def create_analysis_run(
    project_id: str,
    request: AnalysisRunCreate,
    current_user_id: str = Depends(get_current_user_id),
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new analysis run"""
    try:
        # Check if project exists and belongs to tenant
        result = await db.execute(
            "SELECT id FROM project WHERE id = :project_id AND tenant_id = :tenant_id",
            {"project_id": project_id, "tenant_id": current_tenant_id}
        )
        
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Create analysis run
        await db.execute(
            """
            INSERT INTO analysisrun (project_id, profile, settings, description, tags,
                                   status, progress, created_by, created_at, updated_at)
            VALUES (:project_id, :profile, :settings, :description, :tags,
                    'pending', 0.0, :created_by, NOW(), NOW())
            """,
            {
                "project_id": project_id,
                "profile": request.profile,
                "settings": request.settings,
                "description": request.description,
                "tags": request.tags,
                "created_by": current_user_id
            }
        )
        
        await db.commit()
        
        # In real implementation, this would trigger the analysis pipeline
        # For now, return a mock response
        return AnalysisRunResponse(
            id="new_run_id",
            project_id=project_id,
            profile=request.profile,
            settings=request.settings,
            description=request.description,
            tags=request.tags,
            status="pending",
            progress=0.0,
            tool_versions={},
            checkpoints={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Analysis run creation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{project_id}/runs", response_model=AnalysisRunListResponse)
@require_permission("analysis:read")
async def list_analysis_runs(
    project_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """List analysis runs for a project"""
    try:
        # Check if project exists and belongs to tenant
        result = await db.execute(
            "SELECT id FROM project WHERE id = :project_id AND tenant_id = :tenant_id",
            {"project_id": project_id, "tenant_id": current_tenant_id}
        )
        
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Build query
        query = "SELECT * FROM analysisrun WHERE project_id = :project_id"
        params = {"project_id": project_id}
        
        if status_filter:
            query += " AND status = :status"
            params["status"] = status_filter
        
        query += " ORDER BY created_at DESC"
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM analysisrun WHERE project_id = :project_id"
        if status_filter:
            count_query += " AND status = :status"
        
        count_result = await db.execute(count_query, params)
        total = count_result.scalar()
        
        # Get paginated results
        query += " LIMIT :limit OFFSET :offset"
        params["limit"] = size
        params["offset"] = (page - 1) * size
        
        result = await db.execute(query, params)
        runs_data = result.fetchall()
        
        # Convert to response models
        runs = []
        for run_data in runs_data:
            runs.append(AnalysisRunResponse(
                id=run_data.id,
                project_id=run_data.project_id,
                profile=run_data.profile,
                settings=run_data.settings,
                description=run_data.description,
                tags=run_data.tags,
                status=run_data.status,
                progress=run_data.progress,
                started_at=run_data.started_at,
                completed_at=run_data.completed_at,
                duration_seconds=run_data.duration_seconds,
                tool_versions=run_data.tool_versions,
                checkpoints=run_data.checkpoints,
                error_message=run_data.error_message,
                created_at=run_data.created_at,
                updated_at=run_data.updated_at
            ))
        
        return AnalysisRunListResponse(
            runs=runs,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Analysis runs list error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/runs/{run_id}", response_model=AnalysisRunResponse)
@require_permission("analysis:read")
async def get_analysis_run(
    run_id: str,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Get analysis run details"""
    try:
        result = await db.execute(
            """
            SELECT ar.* FROM analysisrun ar
            JOIN project p ON ar.project_id = p.id
            WHERE ar.id = :run_id AND p.tenant_id = :tenant_id
            """,
            {"run_id": run_id, "tenant_id": current_tenant_id}
        )
        
        run_data = result.fetchone()
        
        if not run_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis run not found"
            )
        
        return AnalysisRunResponse(
            id=run_data.id,
            project_id=run_data.project_id,
            profile=run_data.profile,
            settings=run_data.settings,
            description=run_data.description,
            tags=run_data.tags,
            status=run_data.status,
            progress=run_data.progress,
            started_at=run_data.started_at,
            completed_at=run_data.completed_at,
            duration_seconds=run_data.duration_seconds,
            tool_versions=run_data.tool_versions,
            checkpoints=run_data.checkpoints,
            error_message=run_data.error_message,
            created_at=run_data.created_at,
            updated_at=run_data.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Analysis run get error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Finding endpoints
@router.get("/runs/{run_id}/findings", response_model=FindingListResponse)
@require_permission("finding:read")
async def list_findings(
    run_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """List findings for an analysis run"""
    try:
        # Check if run exists and belongs to tenant
        result = await db.execute(
            """
            SELECT ar.id FROM analysisrun ar
            JOIN project p ON ar.project_id = p.id
            WHERE ar.id = :run_id AND p.tenant_id = :tenant_id
            """,
            {"run_id": run_id, "tenant_id": current_tenant_id}
        )
        
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis run not found"
            )
        
        # Build query
        query = """
            SELECT f.*, c.name as contract_name
            FROM finding f
            LEFT JOIN contract c ON f.contract_id = c.id
            WHERE f.run_id = :run_id
        """
        params = {"run_id": run_id}
        
        if severity:
            query += " AND f.severity = :severity"
            params["severity"] = severity
        
        if status:
            query += " AND f.status = :status"
            params["status"] = status
        
        if category:
            query += " AND f.category = :category"
            params["category"] = category
        
        query += " ORDER BY f.severity DESC, f.created_at DESC"
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM finding WHERE run_id = :run_id"
        if severity:
            count_query += " AND severity = :severity"
        if status:
            count_query += " AND status = :status"
        if category:
            count_query += " AND category = :category"
        
        count_result = await db.execute(count_query, params)
        total = count_result.scalar()
        
        # Get severity counts
        severity_result = await db.execute(
            "SELECT severity, COUNT(*) FROM finding WHERE run_id = :run_id GROUP BY severity",
            {"run_id": run_id}
        )
        severity_counts = {row.severity: row.count for row in severity_result.fetchall()}
        
        # Get category counts
        category_result = await db.execute(
            "SELECT category, COUNT(*) FROM finding WHERE run_id = :run_id GROUP BY category",
            {"run_id": run_id}
        )
        category_counts = {row.category: row.count for row in category_result.fetchall()}
        
        # Get paginated results
        query += " LIMIT :limit OFFSET :offset"
        params["limit"] = size
        params["offset"] = (page - 1) * size
        
        result = await db.execute(query, params)
        findings_data = result.fetchall()
        
        # Convert to response models
        findings = []
        for finding_data in findings_data:
            findings.append(FindingResponse(
                id=finding_data.id,
                run_id=finding_data.run_id,
                contract_id=finding_data.contract_id,
                title=finding_data.title,
                description=finding_data.description,
                severity=finding_data.severity,
                category=finding_data.category,
                swc_id=finding_data.swc_id,
                cwe_id=finding_data.cwe_id,
                confidence=finding_data.confidence,
                code_spans=finding_data.code_spans,
                evidence=finding_data.evidence,
                recommendations=finding_data.recommendations,
                patches=finding_data.patches,
                tags=finding_data.tags,
                metadata=finding_data.metadata,
                status=finding_data.status,
                notes=finding_data.notes,
                assigned_to=finding_data.assigned_to,
                created_at=finding_data.created_at,
                updated_at=finding_data.updated_at
            ))
        
        return FindingListResponse(
            findings=findings,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size,
            severity_counts=severity_counts,
            category_counts=category_counts
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Findings list error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/findings/{finding_id}", response_model=FindingResponse)
@require_permission("finding:read")
async def get_finding(
    finding_id: str,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Get finding details"""
    try:
        result = await db.execute(
            """
            SELECT f.*, c.name as contract_name
            FROM finding f
            JOIN analysisrun ar ON f.run_id = ar.id
            JOIN project p ON ar.project_id = p.id
            LEFT JOIN contract c ON f.contract_id = c.id
            WHERE f.id = :finding_id AND p.tenant_id = :tenant_id
            """,
            {"finding_id": finding_id, "tenant_id": current_tenant_id}
        )
        
        finding_data = result.fetchone()
        
        if not finding_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Finding not found"
            )
        
        return FindingResponse(
            id=finding_data.id,
            run_id=finding_data.run_id,
            contract_id=finding_data.contract_id,
            title=finding_data.title,
            description=finding_data.description,
            severity=finding_data.severity,
            category=finding_data.category,
            swc_id=finding_data.swc_id,
            cwe_id=finding_data.cwe_id,
            confidence=finding_data.confidence,
            code_spans=finding_data.code_spans,
            evidence=finding_data.evidence,
            recommendations=finding_data.recommendations,
            patches=finding_data.patches,
            tags=finding_data.tags,
            metadata=finding_data.metadata,
            status=finding_data.status,
            notes=finding_data.notes,
            assigned_to=finding_data.assigned_to,
            created_at=finding_data.created_at,
            updated_at=finding_data.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Finding get error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/findings/{finding_id}", response_model=FindingResponse)
@require_permission("finding:write")
async def update_finding(
    finding_id: str,
    request: FindingUpdate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Update finding details"""
    try:
        # Check if finding exists and belongs to tenant
        result = await db.execute(
            """
            SELECT f.id FROM finding f
            JOIN analysisrun ar ON f.run_id = ar.id
            JOIN project p ON ar.project_id = p.id
            WHERE f.id = :finding_id AND p.tenant_id = :tenant_id
            """,
            {"finding_id": finding_id, "tenant_id": current_tenant_id}
        )
        
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Finding not found"
            )
        
        # Build update query
        update_fields = []
        params = {"finding_id": finding_id}
        
        if request.title is not None:
            update_fields.append("title = :title")
            params["title"] = request.title
        
        if request.description is not None:
            update_fields.append("description = :description")
            params["description"] = request.description
        
        if request.severity is not None:
            update_fields.append("severity = :severity")
            params["severity"] = request.severity
        
        if request.status is not None:
            update_fields.append("status = :status")
            params["status"] = request.status
        
        if request.category is not None:
            update_fields.append("category = :category")
            params["category"] = request.category
        
        if request.confidence is not None:
            update_fields.append("confidence = :confidence")
            params["confidence"] = request.confidence
        
        if request.tags is not None:
            update_fields.append("tags = :tags")
            params["tags"] = request.tags
        
        if request.metadata is not None:
            update_fields.append("metadata = :metadata")
            params["metadata"] = request.metadata
        
        if request.notes is not None:
            update_fields.append("notes = :notes")
            params["notes"] = request.notes
        
        if request.assigned_to is not None:
            update_fields.append("assigned_to = :assigned_to")
            params["assigned_to"] = request.assigned_to
        
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        update_fields.append("updated_at = NOW()")
        
        query = f"UPDATE finding SET {', '.join(update_fields)} WHERE id = :finding_id"
        await db.execute(query, params)
        
        await db.commit()
        
        # Return updated finding
        return await get_finding(finding_id, current_tenant_id, db)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Finding update error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Dashboard endpoints
@router.get("/dashboard/stats", response_model=DashboardStats)
@require_permission("project:read")
async def get_dashboard_stats(
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics"""
    try:
        # Get project stats
        project_result = await db.execute(
            "SELECT COUNT(*) FROM project WHERE tenant_id = :tenant_id AND status != 'deleted'",
            {"tenant_id": current_tenant_id}
        )
        total_projects = project_result.scalar()
        
        # Get run stats
        run_result = await db.execute(
            """
            SELECT COUNT(*) FROM analysisrun ar
            JOIN project p ON ar.project_id = p.id
            WHERE p.tenant_id = :tenant_id
            """,
            {"tenant_id": current_tenant_id}
        )
        total_runs = run_result.scalar()
        
        # Get finding stats
        finding_result = await db.execute(
            """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical,
                SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high,
                SUM(CASE WHEN severity = 'medium' THEN 1 ELSE 0 END) as medium,
                SUM(CASE WHEN severity = 'low' THEN 1 ELSE 0 END) as low,
                SUM(CASE WHEN severity = 'informational' THEN 1 ELSE 0 END) as informational
            FROM finding f
            JOIN analysisrun ar ON f.run_id = ar.id
            JOIN project p ON ar.project_id = p.id
            WHERE p.tenant_id = :tenant_id
            """,
            {"tenant_id": current_tenant_id}
        )
        finding_stats = finding_result.fetchone()
        
        # Get average run duration
        duration_result = await db.execute(
            """
            SELECT AVG(duration_seconds) / 60.0 as avg_duration_minutes
            FROM analysisrun ar
            JOIN project p ON ar.project_id = p.id
            WHERE p.tenant_id = :tenant_id AND ar.duration_seconds IS NOT NULL
            """,
            {"tenant_id": current_tenant_id}
        )
        avg_duration = duration_result.scalar() or 0.0
        
        # Get success rate
        success_result = await db.execute(
            """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM analysisrun ar
            JOIN project p ON ar.project_id = p.id
            WHERE p.tenant_id = :tenant_id
            """,
            {"tenant_id": current_tenant_id}
        )
        success_stats = success_result.fetchone()
        success_rate = (success_stats.completed / success_stats.total * 100) if success_stats.total > 0 else 0.0
        
        return DashboardStats(
            total_projects=total_projects,
            total_runs=total_runs,
            total_findings=finding_stats.total or 0,
            critical_findings=finding_stats.critical or 0,
            high_findings=finding_stats.high or 0,
            medium_findings=finding_stats.medium or 0,
            low_findings=finding_stats.low or 0,
            informational_findings=finding_stats.informational or 0,
            avg_run_duration_minutes=avg_duration,
            success_rate=success_rate,
            recent_activity=[]
        )
        
    except Exception as e:
        logger.error("Dashboard stats error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
