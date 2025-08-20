# 🔌 ChainGuard AI - API Specification

## 📋 Overview
This document provides the complete API specification for ChainGuard AI Smart Contract Analysis & Security Auditor. The API follows RESTful principles with comprehensive authentication, validation, and error handling.

## 🏗️ API Architecture

### **Base URL**
```
Development: http://localhost:8000/api/v1
Production: https://api.chainguard.ai/api/v1
```

### **Authentication**
- **Type**: JWT Bearer Token
- **Header**: `Authorization: Bearer <access_token>`
- **Refresh**: Automatic token refresh with refresh tokens
- **Rate Limiting**: 100 requests/minute per IP

### **Response Format**
```json
{
  "data": {},
  "message": "Success",
  "status": "success",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### **Error Format**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {}
  },
  "status": "error",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔐 Authentication Endpoints

### **POST /auth/login**
**Description**: User login with email/password

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "remember_me": false,
  "totp_token": "123456"
}
```

**Response**:
```json
{
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "username": "user",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "is_verified": true,
      "tenant_id": "tenant_456",
      "roles": ["analyst"],
      "permissions": ["project:read", "analysis:write"]
    }
  }
}
```

### **POST /auth/refresh**
**Description**: Refresh access token

**Request Body**:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response**:
```json
{
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### **POST /auth/logout**
**Description**: User logout

**Request Body**:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **POST /auth/register**
**Description**: User registration

**Request Body**:
```json
{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "securepassword123",
  "first_name": "Jane",
  "last_name": "Smith",
  "tenant_id": "tenant_456"
}
```

## 📁 Project Management Endpoints

### **GET /projects**
**Description**: List projects for current tenant

**Query Parameters**:
- `page` (int, default: 1): Page number
- `size` (int, default: 20, max: 100): Items per page
- `status` (string, optional): Filter by status (active, archived, deleted)
- `search` (string, optional): Search in name/description

**Response**:
```json
{
  "data": {
    "projects": [
      {
        "id": "project_123",
        "name": "DeFi Protocol",
        "description": "Decentralized finance protocol",
        "project_type": "git",
        "framework": "hardhat",
        "source_url": "https://github.com/example/defi-protocol",
        "contract_address": null,
        "settings": {},
        "tenant_id": "tenant_456",
        "status": "active",
        "contract_count": 5,
        "run_count": 12,
        "last_run_at": "2024-01-01T10:00:00Z",
        "total_findings": 25,
        "critical_findings": 2,
        "high_findings": 8,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 20,
    "pages": 3
  }
}
```

### **POST /projects**
**Description**: Create new project

**Request Body**:
```json
{
  "name": "New Smart Contract",
  "description": "Smart contract for token distribution",
  "project_type": "git",
  "framework": "foundry",
  "source_url": "https://github.com/example/token-contract",
  "contract_address": null,
  "settings": {
    "compiler_version": "0.8.19",
    "optimization": true
  }
}
```

### **GET /projects/{project_id}**
**Description**: Get project details

**Response**:
```json
{
  "data": {
    "id": "project_123",
    "name": "DeFi Protocol",
    "description": "Decentralized finance protocol",
    "project_type": "git",
    "framework": "hardhat",
    "source_url": "https://github.com/example/defi-protocol",
    "contract_address": null,
    "settings": {},
    "tenant_id": "tenant_456",
    "status": "active",
    "contract_count": 5,
    "run_count": 12,
    "last_run_at": "2024-01-01T10:00:00Z",
    "total_findings": 25,
    "critical_findings": 2,
    "high_findings": 8,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  }
}
```

### **PUT /projects/{project_id}**
**Description**: Update project

**Request Body**:
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "status": "active",
  "settings": {
    "compiler_version": "0.8.20"
  }
}
```

### **DELETE /projects/{project_id}**
**Description**: Delete project (soft delete)

## 🔍 Analysis Run Endpoints

### **POST /projects/{project_id}/runs**
**Description**: Create new analysis run

**Request Body**:
```json
{
  "profile": "comprehensive",
  "settings": {
    "timeout_minutes": 60,
    "max_findings": 100,
    "include_gas_analysis": true,
    "include_coverage": true
  },
  "description": "Full security audit",
  "tags": ["security", "audit", "production"]
}
```

**Response**:
```json
{
  "data": {
    "id": "run_789",
    "project_id": "project_123",
    "profile": "comprehensive",
    "settings": {
      "timeout_minutes": 60,
      "max_findings": 100,
      "include_gas_analysis": true,
      "include_coverage": true
    },
    "description": "Full security audit",
    "tags": ["security", "audit", "production"],
    "status": "pending",
    "progress": 0.0,
    "started_at": null,
    "completed_at": null,
    "duration_seconds": null,
    "tool_versions": {},
    "checkpoints": {},
    "error_message": null,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

### **GET /projects/{project_id}/runs**
**Description**: List analysis runs for project

**Query Parameters**:
- `page` (int, default: 1): Page number
- `size` (int, default: 20, max: 100): Items per page
- `status` (string, optional): Filter by status

**Response**:
```json
{
  "data": {
    "runs": [
      {
        "id": "run_789",
        "project_id": "project_123",
        "profile": "comprehensive",
        "status": "completed",
        "progress": 100.0,
        "started_at": "2024-01-01T12:00:00Z",
        "completed_at": "2024-01-01T12:30:00Z",
        "duration_seconds": 1800,
        "description": "Full security audit",
        "tags": ["security", "audit", "production"]
      }
    ],
    "total": 12,
    "page": 1,
    "size": 20,
    "pages": 1
  }
}
```

### **GET /runs/{run_id}**
**Description**: Get analysis run details

**Response**:
```json
{
  "data": {
    "id": "run_789",
    "project_id": "project_123",
    "profile": "comprehensive",
    "settings": {
      "timeout_minutes": 60,
      "max_findings": 100,
      "include_gas_analysis": true,
      "include_coverage": true
    },
    "description": "Full security audit",
    "tags": ["security", "audit", "production"],
    "status": "completed",
    "progress": 100.0,
    "started_at": "2024-01-01T12:00:00Z",
    "completed_at": "2024-01-01T12:30:00Z",
    "duration_seconds": 1800,
    "tool_versions": {
      "slither": "0.9.3",
      "mythril": "0.23.26",
      "foundry": "0.2.0"
    },
    "checkpoints": {
      "static_analysis": "completed",
      "fuzzing": "completed",
      "symbolic_execution": "completed"
    },
    "error_message": null,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:30:00Z"
  }
}
```

## 🚨 Findings Endpoints

### **GET /runs/{run_id}/findings**
**Description**: List findings for analysis run

**Query Parameters**:
- `page` (int, default: 1): Page number
- `size` (int, default: 20, max: 100): Items per page
- `severity` (string, optional): Filter by severity (critical, high, medium, low, informational)
- `status` (string, optional): Filter by status (open, in_progress, resolved, false_positive, wont_fix, duplicate)
- `category` (string, optional): Filter by category

**Response**:
```json
{
  "data": {
    "findings": [
      {
        "id": "finding_456",
        "run_id": "run_789",
        "contract_id": "contract_101",
        "title": "Reentrancy Vulnerability",
        "description": "The contract is vulnerable to reentrancy attacks...",
        "severity": "critical",
        "category": "reentrancy",
        "swc_id": "SWC-107",
        "cwe_id": "CWE-841",
        "confidence": 0.95,
        "code_spans": [
          {
            "file_path": "contracts/Token.sol",
            "start_line": 45,
            "end_line": 52,
            "start_column": 8,
            "end_column": 12,
            "code_snippet": "function withdraw() external {\n    require(balances[msg.sender] > 0);\n    uint256 amount = balances[msg.sender];\n    balances[msg.sender] = 0;\n    (bool success, ) = msg.sender.call{value: amount}(\"\");\n    require(success);\n}"
          }
        ],
        "evidence": [
          {
            "type": "code_analysis",
            "description": "External call before state update",
            "data": {
              "external_call": "msg.sender.call{value: amount}(\"\")",
              "state_update": "balances[msg.sender] = 0"
            },
            "file_path": "contracts/Token.sol",
            "line_number": 49
          }
        ],
        "recommendations": [
          {
            "title": "Use Checks-Effects-Interactions Pattern",
            "description": "Update state before making external calls",
            "impact": "High",
            "effort": "Medium",
            "priority": "High"
          }
        ],
        "patches": [
          {
            "diff": "@@ -45,8 +45,8 @@\n function withdraw() external {\n     require(balances[msg.sender] > 0);\n     uint256 amount = balances[msg.sender];\n-    balances[msg.sender] = 0;\n     (bool success, ) = msg.sender.call{value: amount}(\"\");\n+    balances[msg.sender] = 0;\n     require(success);\n }",
            "description": "Move state update after external call",
            "test_code": "function testReentrancy() public {\n    // Test implementation\n}",
            "risk_level": "low"
          }
        ],
        "tags": ["reentrancy", "critical", "withdraw"],
        "metadata": {
          "tool": "slither",
          "rule": "reentrancy-eth"
        },
        "status": "open",
        "notes": null,
        "assigned_to": null,
        "created_at": "2024-01-01T12:15:00Z",
        "updated_at": "2024-01-01T12:15:00Z"
      }
    ],
    "total": 25,
    "page": 1,
    "size": 20,
    "pages": 2,
    "severity_counts": {
      "critical": 2,
      "high": 8,
      "medium": 10,
      "low": 3,
      "informational": 2
    },
    "category_counts": {
      "reentrancy": 3,
      "access_control": 5,
      "arithmetic": 2,
      "unchecked_calls": 8,
      "other": 7
    }
  }
}
```

### **GET /findings/{finding_id}**
**Description**: Get finding details

### **PUT /findings/{finding_id}**
**Description**: Update finding

**Request Body**:
```json
{
  "title": "Updated Finding Title",
  "description": "Updated description",
  "severity": "high",
  "status": "in_progress",
  "category": "access_control",
  "confidence": 0.85,
  "tags": ["updated", "access_control"],
  "notes": "Under investigation",
  "assigned_to": "user_123"
}
```

## 📊 Dashboard Endpoints

### **GET /dashboard/stats**
**Description**: Get dashboard statistics

**Response**:
```json
{
  "data": {
    "total_projects": 15,
    "total_runs": 45,
    "total_findings": 234,
    "critical_findings": 12,
    "high_findings": 45,
    "medium_findings": 89,
    "low_findings": 67,
    "informational_findings": 21,
    "avg_run_duration_minutes": 25.5,
    "success_rate": 94.2,
    "recent_activity": [
      {
        "type": "analysis_completed",
        "project_name": "DeFi Protocol",
        "run_id": "run_789",
        "findings_count": 25,
        "timestamp": "2024-01-01T12:30:00Z"
      }
    ]
  }
}
```

## 🔍 Search Endpoints

### **POST /search**
**Description**: Semantic search across code, findings, and reports

**Request Body**:
```json
{
  "query": "reentrancy vulnerability in withdraw function",
  "filters": {
    "severity": ["critical", "high"],
    "category": ["reentrancy"],
    "project_id": "project_123"
  },
  "page": 1,
  "size": 20
}
```

**Response**:
```json
{
  "data": {
    "results": [
      {
        "id": "finding_456",
        "type": "finding",
        "title": "Reentrancy Vulnerability",
        "description": "The contract is vulnerable to reentrancy attacks...",
        "score": 0.95,
        "metadata": {
          "severity": "critical",
          "category": "reentrancy",
          "project_name": "DeFi Protocol"
        }
      }
    ],
    "total": 5,
    "page": 1,
    "size": 20,
    "pages": 1,
    "query_time_ms": 125.5
  }
}
```

## 📄 Report Endpoints

### **POST /runs/{run_id}/reports**
**Description**: Generate audit report

**Request Body**:
```json
{
  "format": "pdf",
  "include_evidence": true,
  "include_patches": true,
  "severity_filter": ["critical", "high", "medium"],
  "template": "standard"
}
```

**Response**:
```json
{
  "data": {
    "report_id": "report_999",
    "status": "generating",
    "download_url": null,
    "expires_at": "2024-01-08T12:00:00Z",
    "estimated_completion": "2024-01-01T13:00:00Z"
  }
}
```

### **GET /reports/{report_id}**
**Description**: Get report status and download URL

**Response**:
```json
{
  "data": {
    "id": "report_999",
    "run_id": "run_789",
    "format": "pdf",
    "status": "completed",
    "download_url": "https://api.chainguard.ai/reports/report_999.pdf",
    "file_size": 2048576,
    "checksum": "sha256:abc123...",
    "created_at": "2024-01-01T13:00:00Z",
    "expires_at": "2024-01-08T12:00:00Z"
  }
}
```

## 🔧 WebSocket Endpoints

### **WebSocket Connection**
**URL**: `ws://localhost:8000/ws`

**Authentication**: Include JWT token in query parameter
```
ws://localhost:8000/ws?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### **Message Types**

#### **Subscribe to Run Progress**
```json
{
  "type": "subscribe",
  "channel": "run_progress",
  "run_id": "run_789"
}
```

#### **Run Progress Update**
```json
{
  "type": "run_progress",
  "data": {
    "run_id": "run_789",
    "status": "running",
    "progress": 45.5,
    "current_stage": "static_analysis",
    "estimated_completion": "2024-01-01T12:45:00Z"
  },
  "timestamp": "2024-01-01T12:30:00Z"
}
```

#### **Finding Update**
```json
{
  "type": "finding_update",
  "data": {
    "finding_id": "finding_456",
    "status": "resolved",
    "updated_by": "user_123",
    "notes": "Fixed by applying patch"
  },
  "timestamp": "2024-01-01T12:35:00Z"
}
```

## 🚨 Error Codes

### **HTTP Status Codes**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

### **Error Codes**
- `VALIDATION_ERROR` - Input validation failed
- `AUTHENTICATION_ERROR` - Invalid credentials
- `AUTHORIZATION_ERROR` - Insufficient permissions
- `RESOURCE_NOT_FOUND` - Resource doesn't exist
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server error

## 🔒 Security Considerations

### **Authentication**
- JWT tokens with short expiration (30 minutes)
- Refresh tokens with longer expiration (30 days)
- Automatic token refresh
- Secure token storage

### **Authorization**
- Role-based access control (RBAC)
- Fine-grained permissions
- Tenant isolation
- Resource-level permissions

### **Input Validation**
- Comprehensive request validation
- SQL injection prevention
- XSS protection
- File upload validation

### **Rate Limiting**
- IP-based rate limiting
- User-based rate limiting
- Endpoint-specific limits
- Burst protection

## 📚 SDK Examples

### **Python SDK**
```python
import chainguard

client = chainguard.Client(
    api_key="your_api_key",
    base_url="https://api.chainguard.ai"
)

# Create project
project = client.projects.create(
    name="My Smart Contract",
    project_type="git",
    source_url="https://github.com/example/contract"
)

# Run analysis
run = client.runs.create(
    project_id=project.id,
    profile="comprehensive"
)

# Get findings
findings = client.findings.list(run_id=run.id)
```

### **JavaScript SDK**
```javascript
import { ChainGuardClient } from '@chainguard/sdk';

const client = new ChainGuardClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.chainguard.ai'
});

// Create project
const project = await client.projects.create({
  name: 'My Smart Contract',
  projectType: 'git',
  sourceUrl: 'https://github.com/example/contract'
});

// Run analysis
const run = await client.runs.create({
  projectId: project.id,
  profile: 'comprehensive'
});

// Get findings
const findings = await client.findings.list({ runId: run.id });
```

This API specification provides Claude Code with complete understanding of the API structure, enabling seamless integration and development! 🎯
