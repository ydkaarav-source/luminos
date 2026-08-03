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

export interface HealthScoreExplanation {
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

export interface HealthScore {
  id: string;
  overall_score: number;
  revenue_score: number;
  operations_score: number;
  marketing_score: number;
  customer_growth_score: number;
  financial_management_score: number;
  ai_explanation: HealthScoreExplanation;
  calculated_at: string;
}

export interface CEOBriefing {
  id: string;
  title: string;
  body: string;
  priority: "low" | "medium" | "high";
  is_read: boolean;
  generated_at: string;
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
