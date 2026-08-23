// Mirrors backend/app/schemas/*.py - keep these in sync manually for the
// MVP. If this drifts often, generating types from the OpenAPI schema
// (openapi-typescript) is the natural next step.

export interface User {
  id: string;
  email: string;
  name: string | null;
  onboarding_completed: boolean;
}

export type BusinessStage = "idea" | "building" | "operating" | "growing";
export type BusinessType =
  | "ecommerce"
  | "solopreneur_service"
  | "digital_product"
  | "saas"
  | "other";
export type PrimaryGoal =
  | "start_first_business"
  | "increase_revenue"
  | "improve_organization"
  | "scale_operations";
export type BudgetRange = "under_1k" | "1k_5k" | "5k_20k" | "20k_plus";
export type ExperienceLevel = "beginner" | "intermediate" | "experienced";

export interface Business {
  id: string;
  name: string;
  stage: BusinessStage;
  business_type: BusinessType;
  primary_goal: PrimaryGoal;
  available_time_per_week: number | null;
  budget_range: BudgetRange | null;
  current_challenges: string[] | null;
}

export type TaskPriority = "low" | "medium" | "high";
export type TaskStatus = "todo" | "in_progress" | "done" | "skipped";

export interface Task {
  id: string;
  title: string;
  description: string | null;
  due_date: string | null;
  priority: TaskPriority;
  status: TaskStatus;
  source: "user_created" | "ai_generated";
  project_id: string | null;
}

export interface BusinessProfile {
  id: string;
  business_id: string;
  industry: string | null;
  description: string | null;
  products_services: string | null;
  target_customers: string | null;
  company_goals: string | null;
}

export interface HealthScoreExplanation {
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

// One explanation per executive role instead of a single flat object -
// mirrors backend/app/schemas/health_score.py's HealthScoreExplanation
// (a dict of role -> RoleExplanation).
export type HealthScoreRole = "ceo" | "cfo" | "cmo" | "coo" | "cro";

export interface HealthScore {
  id: string;
  overall_score: number;
  revenue_score: number;
  operations_score: number;
  marketing_score: number;
  customer_growth_score: number;
  financial_management_score: number;
  ai_explanation: Record<HealthScoreRole, HealthScoreExplanation>;
  calculated_at: string;
  is_demo: boolean;
}

export interface CEOBriefing {
  id: string;
  finding: string;
  why: string[];
  recommendation: string;
  confidence: "high" | "medium" | "low";
  is_read: boolean;
  generated_at: string;
  is_demo: boolean;
}

export interface BusinessPlanOverview {
  target_customer: string;
  problem_solved: string;
  revenue_model: string;
  competition: string;
  risks: string;
}

export interface RoadmapMonth {
  month: number;
  focus: string;
  milestones: string[];
}

export interface ActionPlan {
  daily_tasks: string[];
  weekly_goals: string[];
  milestones: string[];
}

export interface BusinessPlan {
  id: string;
  title: string;
  overview: BusinessPlanOverview;
  roadmap: RoadmapMonth[];
  action_plan: ActionPlan;
  status: "draft" | "active" | "archived";
}

export interface TargetPage {
  name: string;
  purpose: string;
}

export interface WebsiteBrief {
  id: string;
  title: string;
  target_pages: TargetPage[];
  copy_direction: string;
  design_direction: string;
  site_url: string | null;
}

export interface WebsiteScrapeResult {
  brief: WebsiteBrief;
  content_preview: string;
}

export interface AssistantMessage {
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

export interface ApiEnvelope<T> {
  data: T;
  meta: { generated_at: string };
}

export interface ApiErrorEnvelope {
  error: { code: string; message: string; details: Record<string, unknown> };
}
export interface RevenuePoint {
  period: string;
  amount: number;
}

export interface TaskCompletionPoint {
  period: string;
  completed: number;
  created: number;
}

export interface HealthScoreHistoryPoint {
  calculated_at: string;
  overall_score: number;
}

export interface BusinessAnalytics {
  revenue_over_time: RevenuePoint[];
  task_completion_over_time: TaskCompletionPoint[];
  health_score_history: HealthScoreHistoryPoint[];
  is_demo: boolean;
}

export type MemoryType = "fact" | "decision" | "preference" | "completed_milestone" | "note";
export type MemorySource =
  | "onboarding"
  | "assistant_chat"
  | "business_builder"
  | "website_brief"
  | "scraped_site_content"
  | "user_manual"
  | "system_inferred";

export interface MemoryRecord {
  id: string;
  memory_type: MemoryType;
  content: string;
  source: MemorySource;
  relevance_score: number;
  created_at: string;
}

export type TradeSide = "buy" | "sell";

export interface Trade {
  id: string;
  symbol: string;
  side: TradeSide;
  quantity: number;
  price: number;
  trade_date: string;
  notes: string | null;
}

export interface Position {
  symbol: string;
  quantity: number;
  average_cost: number;
  total_cost: number;
  realized_pl: number;
}

export interface PortfolioSummary {
  positions: Position[];
  total_realized_pl: number;
  total_cost_basis: number;
}

export type RevenueEntryOrigin = "manual" | "stripe";

export interface RevenueEntry {
  id: string;
  amount: number;
  currency: string;
  source: string | null;
  entry_date: string;
  notes: string | null;
  origin: RevenueEntryOrigin;
}

export interface StripeConnectUrl {
  url: string;
}

export interface StripeStatus {
  connected: boolean;
  connected_at: string | null;
  stripe_account_id: string | null;
}

export interface StripeSyncResult {
  synced_count: number;
  total_fetched: number;
}