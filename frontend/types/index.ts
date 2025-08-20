// Core API Types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

// Authentication Types
export interface User {
  id: string
  email: string
  name: string
  avatar_url?: string
  role: UserRole
  tenant_id: string
  created_at: string
  updated_at: string
  last_login?: string
  is_active: boolean
  preferences: UserPreferences
}

export type UserRole = 'admin' | 'auditor' | 'reviewer' | 'viewer'

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  notifications: NotificationSettings
  default_analysis_profile: string
  language: string
}

export interface NotificationSettings {
  email: boolean
  push: boolean
  slack: boolean
  findings: boolean
  reports: boolean
  system: boolean
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  expires_in: number
  token_type: string
}

// Project Types
export interface Project {
  id: string
  name: string
  description?: string
  source_type: ProjectSourceType
  source_url?: string
  contract_address?: string
  framework: ProjectFramework
  compiler_versions: string[]
  tenant_id: string
  created_by: string
  created_at: string
  updated_at: string
  last_analysis?: string
  status: ProjectStatus
  metadata: ProjectMetadata
  settings: ProjectSettings
}

export type ProjectSourceType = 'git' | 'zip' | 'address' | 'file'
export type ProjectFramework = 'hardhat' | 'foundry' | 'truffle' | 'brownie' | 'none'
export type ProjectStatus = 'active' | 'archived' | 'deleted'

export interface ProjectMetadata {
  repository?: {
    name: string
    owner: string
    branch: string
    commit_hash: string
  }
  contracts: ContractInfo[]
  dependencies: DependencyInfo[]
  build_info: BuildInfo
}

export interface ContractInfo {
  name: string
  path: string
  address?: string
  abi?: any[]
  bytecode?: string
  source_code?: string
  compiler_version: string
  optimization_enabled: boolean
  runs: number
  evm_version: string
}

export interface DependencyInfo {
  name: string
  version: string
  source: string
  license?: string
}

export interface BuildInfo {
  solc_version: string
  optimizer_enabled: boolean
  optimizer_runs: number
  evm_version: string
  libraries: Record<string, string>
}

export interface ProjectSettings {
  analysis_profiles: string[]
  auto_scan: boolean
  scan_schedule?: string
  retention_days: number
  notification_channels: string[]
  custom_rules: CustomRule[]
}

export interface CustomRule {
  id: string
  name: string
  description: string
  severity: FindingSeverity
  pattern: string
  enabled: boolean
}

// Analysis Run Types
export interface AnalysisRun {
  id: string
  project_id: string
  profile: AnalysisProfile
  status: RunStatus
  started_at: string
  completed_at?: string
  duration?: number
  progress: RunProgress
  results: AnalysisResults
  artifacts: Artifact[]
  metadata: RunMetadata
  checkpoints: Checkpoint[]
}

export type AnalysisProfile = 'full' | 'quick' | 'delta' | 'custom'
export type RunStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface RunProgress {
  current_step: string
  total_steps: number
  completed_steps: number
  percentage: number
  estimated_remaining?: number
  current_tool?: string
  step_details: StepDetail[]
}

export interface StepDetail {
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at?: string
  completed_at?: string
  duration?: number
  tool: string
  output?: string
  error?: string
}

export interface AnalysisResults {
  findings: Finding[]
  summary: AnalysisSummary
  gas_report?: GasReport
  coverage_report?: CoverageReport
  security_score: number
  risk_level: RiskLevel
}

export interface AnalysisSummary {
  total_findings: number
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  info_count: number
  false_positives: number
  true_positives: number
  unresolved: number
}

export type RiskLevel = 'critical' | 'high' | 'medium' | 'low' | 'safe'

export interface GasReport {
  total_gas_used: number
  average_gas_per_tx: number
  expensive_functions: GasFunction[]
  optimization_suggestions: GasSuggestion[]
}

export interface GasFunction {
  name: string
  gas_used: number
  calls: number
  average_gas: number
  max_gas: number
  min_gas: number
}

export interface GasSuggestion {
  function_name: string
  current_gas: number
  optimized_gas: number
  savings: number
  suggestion: string
}

export interface CoverageReport {
  total_lines: number
  covered_lines: number
  coverage_percentage: number
  uncovered_functions: string[]
  critical_paths: string[]
}

export interface RunMetadata {
  tool_versions: Record<string, string>
  environment: string
  resource_usage: ResourceUsage
  execution_time: number
  memory_peak: number
  cpu_usage: number
}

export interface ResourceUsage {
  cpu_time: number
  memory_peak: number
  disk_usage: number
  network_io: number
}

export interface Checkpoint {
  id: string
  step: string
  timestamp: string
  data: any
  artifacts: string[]
}

// Finding Types
export interface Finding {
  id: string
  run_id: string
  contract_id: string
  title: string
  description: string
  severity: FindingSeverity
  confidence: number
  status: FindingStatus
  category: FindingCategory
  swc_id?: string
  cwe_id?: string
  owasp_category?: string
  code_span: CodeSpan
  evidence: Evidence[]
  recommendations: Recommendation[]
  patches: Patch[]
  tags: string[]
  created_at: string
  updated_at: string
  reviewed_by?: string
  reviewed_at?: string
  review_notes?: string
  false_positive: boolean
  risk_score: number
  impact: string
  likelihood: string
}

export type FindingSeverity = 'critical' | 'high' | 'medium' | 'low' | 'info'
export type FindingStatus = 'open' | 'confirmed' | 'false_positive' | 'resolved' | 'wont_fix'
export type FindingCategory = 
  | 'access_control'
  | 'arithmetic'
  | 'reentrancy'
  | 'unchecked_external_calls'
  | 'gas_optimization'
  | 'upgradeability'
  | 'economic_risk'
  | 'oracle_manipulation'
  | 'front_running'
  | 'liquidation'
  | 'governance'
  | 'other'

export interface CodeSpan {
  file_path: string
  start_line: number
  end_line: number
  start_column: number
  end_column: number
  code: string
  context_before?: string
  context_after?: string
}

export interface Evidence {
  type: 'poc' | 'trace' | 'test' | 'screenshot' | 'log'
  title: string
  description: string
  content: string
  file_path?: string
  artifact_id?: string
  metadata?: Record<string, any>
}

export interface Recommendation {
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  effort: 'low' | 'medium' | 'high'
  impact: string
  code_example?: string
  references: string[]
}

export interface Patch {
  id: string
  finding_id: string
  title: string
  description: string
  diff: string
  test_code: string
  status: PatchStatus
  created_at: string
  applied_at?: string
  pr_url?: string
  reviewer?: string
  review_notes?: string
}

export type PatchStatus = 'proposed' | 'approved' | 'rejected' | 'applied'

// Artifact Types
export interface Artifact {
  id: string
  run_id: string
  type: ArtifactType
  name: string
  file_path: string
  file_size: number
  mime_type: string
  checksum: string
  metadata: Record<string, any>
  created_at: string
  expires_at?: string
  download_url?: string
}

export type ArtifactType = 
  | 'trace'
  | 'sarif'
  | 'pdf'
  | 'html'
  | 'poc'
  | 'test'
  | 'log'
  | 'coverage'
  | 'gas_report'
  | 'bytecode'
  | 'abi'
  | 'other'

// Report Types
export interface AuditReport {
  id: string
  run_id: string
  title: string
  executive_summary: string
  methodology: string
  scope: string
  findings_summary: FindingsSummary
  detailed_findings: DetailedFinding[]
  recommendations: string[]
  conclusion: string
  appendices: Appendix[]
  metadata: ReportMetadata
  signatures: Signature[]
  created_at: string
  updated_at: string
  version: string
  status: ReportStatus
}

export interface FindingsSummary {
  total_findings: number
  critical_findings: number
  high_findings: number
  medium_findings: number
  low_findings: number
  info_findings: number
  risk_score: number
  risk_level: RiskLevel
  key_insights: string[]
}

export interface DetailedFinding {
  finding_id: string
  title: string
  severity: FindingSeverity
  description: string
  impact: string
  likelihood: string
  code_location: CodeSpan
  evidence: Evidence[]
  recommendations: Recommendation[]
  status: FindingStatus
}

export interface Appendix {
  title: string
  content: string
  type: 'code' | 'diagram' | 'table' | 'text'
}

export interface ReportMetadata {
  auditor: string
  review_date: string
  tools_used: string[]
  methodology_version: string
  compliance_frameworks: string[]
  custom_fields: Record<string, any>
}

export interface Signature {
  signer: string
  signature: string
  timestamp: string
  public_key: string
  algorithm: string
}

export type ReportStatus = 'draft' | 'review' | 'approved' | 'published' | 'archived'

// Search Types
export interface SearchQuery {
  q: string
  filters: SearchFilters
  sort: SearchSort
  page: number
  per_page: number
}

export interface SearchFilters {
  severity?: FindingSeverity[]
  status?: FindingStatus[]
  category?: FindingCategory[]
  date_range?: {
    start: string
    end: string
  }
  projects?: string[]
  contracts?: string[]
  tags?: string[]
}

export interface SearchSort {
  field: string
  direction: 'asc' | 'desc'
}

export interface SearchResult {
  type: 'finding' | 'contract' | 'project' | 'report'
  id: string
  title: string
  description: string
  relevance_score: number
  metadata: Record<string, any>
  highlights: string[]
}

// WebSocket Types
export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
  id?: string
}

export interface RunUpdateMessage {
  run_id: string
  status: RunStatus
  progress: RunProgress
  new_findings?: Finding[]
  completed_steps?: string[]
  errors?: string[]
}

export interface NotificationMessage {
  type: 'info' | 'warning' | 'error' | 'success'
  title: string
  message: string
  action_url?: string
  metadata?: Record<string, any>
}

// Form Types
export interface CreateProjectForm {
  name: string
  description?: string
  source_type: ProjectSourceType
  source_url?: string
  contract_address?: string
  framework: ProjectFramework
  settings: Partial<ProjectSettings>
}

export interface CreateRunForm {
  profile: AnalysisProfile
  custom_settings?: Record<string, any>
  priority?: 'low' | 'normal' | 'high'
}

export interface UpdateFindingForm {
  severity?: FindingSeverity
  status?: FindingStatus
  review_notes?: string
  false_positive?: boolean
  tags?: string[]
}

// API Error Types
export interface ApiError {
  code: string
  message: string
  details?: any
  timestamp: string
  request_id: string
}

// Dashboard Types
export interface DashboardStats {
  total_projects: number
  active_runs: number
  total_findings: number
  critical_findings: number
  average_risk_score: number
  recent_activity: DashboardActivity[]
  top_findings: Finding[]
  project_health: ProjectHealth[]
}

export interface DashboardActivity {
  id: string
  type: 'project_created' | 'run_started' | 'run_completed' | 'finding_created' | 'report_published'
  title: string
  description: string
  timestamp: string
  user: string
  metadata: Record<string, any>
}

export interface ProjectHealth {
  project_id: string
  project_name: string
  risk_score: number
  risk_level: RiskLevel
  last_analysis: string
  findings_count: number
  critical_findings: number
  trend: 'improving' | 'stable' | 'worsening'
}

// Settings Types
export interface TenantSettings {
  id: string
  name: string
  domain: string
  settings: {
    default_analysis_profiles: string[]
    retention_policy: RetentionPolicy
    notification_settings: NotificationSettings
    security_settings: SecuritySettings
    integration_settings: IntegrationSettings
  }
}

export interface RetentionPolicy {
  project_retention_days: number
  run_retention_days: number
  artifact_retention_days: number
  auto_archive: boolean
  archive_after_days: number
}

export interface SecuritySettings {
  require_2fa: boolean
  session_timeout_minutes: number
  max_login_attempts: number
  password_policy: PasswordPolicy
  ip_whitelist: string[]
}

export interface PasswordPolicy {
  min_length: number
  require_uppercase: boolean
  require_lowercase: boolean
  require_numbers: boolean
  require_special_chars: boolean
  max_age_days: number
}

export interface IntegrationSettings {
  github?: GitHubIntegration
  gitlab?: GitLabIntegration
  slack?: SlackIntegration
  email?: EmailIntegration
  webhooks: WebhookConfig[]
}

export interface GitHubIntegration {
  enabled: boolean
  app_id: string
  installation_id: string
  repositories: string[]
  webhook_secret: string
}

export interface GitLabIntegration {
  enabled: boolean
  instance_url: string
  access_token: string
  projects: string[]
  webhook_secret: string
}

export interface SlackIntegration {
  enabled: boolean
  workspace_id: string
  bot_token: string
  channels: string[]
  notifications: {
    findings: boolean
    reports: boolean
    system: boolean
  }
}

export interface EmailIntegration {
  enabled: boolean
  smtp_host: string
  smtp_port: number
  smtp_username: string
  smtp_password: string
  from_email: string
  from_name: string
}

export interface WebhookConfig {
  id: string
  name: string
  url: string
  events: string[]
  secret: string
  enabled: boolean
  retry_count: number
  timeout_seconds: number
}
