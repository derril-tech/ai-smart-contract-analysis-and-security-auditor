-- Initialize ChainGuard AI Database
-- This script sets up the database with pgvector extension and initial configuration

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create custom types
DO $$ BEGIN
    CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'pending');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE subscription_plan AS ENUM ('free', 'basic', 'pro', 'enterprise');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE project_type AS ENUM ('git', 'zip', 'address', 'manual');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE project_framework AS ENUM ('hardhat', 'foundry', 'truffle', 'remix', 'manual', 'unknown');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE project_status AS ENUM ('active', 'archived', 'deleted');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE analysis_profile AS ENUM ('quick', 'standard', 'comprehensive', 'custom');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE run_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled', 'paused');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE finding_severity AS ENUM ('critical', 'high', 'medium', 'low', 'informational');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE finding_status AS ENUM ('open', 'in_progress', 'resolved', 'false_positive', 'wont_fix', 'duplicate');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE finding_category AS ENUM ('access_control', 'arithmetic', 'reentrancy', 'unchecked_calls', 'frontrunning', 'oracle_manipulation', 'upgradeability', 'gas_optimization', 'logic_error', 'configuration', 'dependency', 'other');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE artifact_type AS ENUM ('trace', 'sarif', 'pdf', 'poc', 'test', 'patch', 'coverage', 'gas_report', 'storage_layout', 'bytecode', 'abi', 'metadata');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tenants_domain ON tenants(domain);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_projects_tenant_id ON projects(tenant_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_contracts_project_id ON contracts(project_id);
CREATE INDEX IF NOT EXISTS idx_analysis_runs_project_id ON analysis_runs(project_id);
CREATE INDEX IF NOT EXISTS idx_analysis_runs_status ON analysis_runs(status);
CREATE INDEX IF NOT EXISTS idx_findings_run_id ON findings(run_id);
CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
CREATE INDEX IF NOT EXISTS idx_findings_status ON findings(status);
CREATE INDEX IF NOT EXISTS idx_artifacts_run_id ON artifacts(run_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_project_id ON embeddings(project_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_ref_type ON embeddings(ref_type);

-- Create vector indexes for semantic search
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING ivfflat (vector vector_cosine_ops) WITH (lists = 100);

-- Create JSONB indexes for complex queries
CREATE INDEX IF NOT EXISTS idx_projects_settings ON projects USING gin(settings);
CREATE INDEX IF NOT EXISTS idx_contracts_abi ON contracts USING gin(abi);
CREATE INDEX IF NOT EXISTS idx_contracts_storage_layout ON contracts USING gin(storage_layout);
CREATE INDEX IF NOT EXISTS idx_findings_metadata ON findings USING gin(metadata);
CREATE INDEX IF NOT EXISTS idx_artifacts_metadata ON artifacts USING gin(metadata);

-- Create partial indexes for common queries
CREATE INDEX IF NOT EXISTS idx_findings_critical_high ON findings(severity) WHERE severity IN ('critical', 'high');
CREATE INDEX IF NOT EXISTS idx_analysis_runs_recent ON analysis_runs(created_at) WHERE status = 'completed';
CREATE INDEX IF NOT EXISTS idx_projects_active ON projects(id) WHERE status = 'active';

-- Create composite indexes for complex queries
CREATE INDEX IF NOT EXISTS idx_findings_run_severity ON findings(run_id, severity);
CREATE INDEX IF NOT EXISTS idx_findings_contract_severity ON findings(contract_id, severity);
CREATE INDEX IF NOT EXISTS idx_analysis_runs_project_status ON analysis_runs(project_id, status);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO chainguard;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO chainguard;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO chainguard;

-- Create a function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_contracts_updated_at BEFORE UPDATE ON contracts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_analysis_runs_updated_at BEFORE UPDATE ON analysis_runs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_findings_updated_at BEFORE UPDATE ON findings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_artifacts_updated_at BEFORE UPDATE ON artifacts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a function to generate UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create a function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Clean up expired refresh tokens (older than 30 days)
    DELETE FROM refresh_tokens WHERE expires_at < NOW() - INTERVAL '30 days';
    
    -- Clean up expired user sessions (older than 7 days)
    DELETE FROM user_sessions WHERE expires_at < NOW() - INTERVAL '7 days';
    
    -- Clean up expired artifacts (older than 90 days)
    DELETE FROM artifacts WHERE expires_at < NOW() - INTERVAL '90 days' AND expires_at IS NOT NULL;
    
    -- Clean up old audit logs (older than 1 year)
    DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '1 year';
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled job to run cleanup (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-old-data', '0 2 * * *', 'SELECT cleanup_old_data();');

-- Create a function to get project statistics
CREATE OR REPLACE FUNCTION get_project_stats(project_id UUID)
RETURNS TABLE(
    total_findings BIGINT,
    critical_findings BIGINT,
    high_findings BIGINT,
    medium_findings BIGINT,
    low_findings BIGINT,
    informational_findings BIGINT,
    total_runs BIGINT,
    last_run_at TIMESTAMP,
    avg_run_duration_minutes NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(f.id) as total_findings,
        COUNT(f.id) FILTER (WHERE f.severity = 'critical') as critical_findings,
        COUNT(f.id) FILTER (WHERE f.severity = 'high') as high_findings,
        COUNT(f.id) FILTER (WHERE f.severity = 'medium') as medium_findings,
        COUNT(f.id) FILTER (WHERE f.severity = 'low') as low_findings,
        COUNT(f.id) FILTER (WHERE f.severity = 'informational') as informational_findings,
        COUNT(ar.id) as total_runs,
        MAX(ar.completed_at) as last_run_at,
        AVG(EXTRACT(EPOCH FROM (ar.completed_at - ar.started_at)) / 60) as avg_run_duration_minutes
    FROM projects p
    LEFT JOIN analysis_runs ar ON p.id = ar.project_id
    LEFT JOIN findings f ON ar.id = f.run_id
    WHERE p.id = project_id
    GROUP BY p.id;
END;
$$ LANGUAGE plpgsql;

-- Create a function to search embeddings
CREATE OR REPLACE FUNCTION search_embeddings(
    query_vector vector(1536),
    search_limit INTEGER DEFAULT 10,
    similarity_threshold REAL DEFAULT 0.7
)
RETURNS TABLE(
    id UUID,
    text TEXT,
    ref_type TEXT,
    ref_id UUID,
    similarity REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.text,
        e.ref_type,
        e.ref_id,
        1 - (e.vector <=> query_vector) as similarity
    FROM embeddings e
    WHERE 1 - (e.vector <=> query_vector) > similarity_threshold
    ORDER BY e.vector <=> query_vector
    LIMIT search_limit;
END;
$$ LANGUAGE plpgsql;
