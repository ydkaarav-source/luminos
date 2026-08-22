"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { apiClient, ApiError } from "@/lib/api-client";
import type {
  BudgetRange,
  BusinessStage,
  BusinessType,
  ExperienceLevel,
  PrimaryGoal,
} from "@/lib/types";

const STEPS = ["profile", "business", "brain", "resources"] as const;
type Step = (typeof STEPS)[number];

const STAGE_OPTIONS: { value: BusinessStage; label: string }[] = [
  { value: "idea", label: "Idea stage" },
  { value: "building", label: "Building" },
  { value: "operating", label: "Operating" },
  { value: "growing", label: "Growing" },
];

const TYPE_OPTIONS: { value: BusinessType; label: string }[] = [
  { value: "ecommerce", label: "Ecommerce" },
  { value: "solopreneur_service", label: "Solopreneur service" },
  { value: "digital_product", label: "Digital product" },
  { value: "saas", label: "SaaS" },
  { value: "other", label: "Other" },
];

const GOAL_OPTIONS: { value: PrimaryGoal; label: string }[] = [
  { value: "start_first_business", label: "Start my first business" },
  { value: "increase_revenue", label: "Increase revenue" },
  { value: "improve_organization", label: "Improve organization" },
  { value: "scale_operations", label: "Scale operations" },
];

const BUDGET_OPTIONS: { value: BudgetRange; label: string }[] = [
  { value: "under_1k", label: "Under $1k" },
  { value: "1k_5k", label: "$1k – $5k" },
  { value: "5k_20k", label: "$5k – $20k" },
  { value: "20k_plus", label: "$20k+" },
];

function OptionGrid<T extends string>({
  options,
  value,
  onChange,
}: {
  options: { value: T; label: string }[];
  value: T | null;
  onChange: (v: T) => void;
}) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={`rounded-lg border px-3 py-2.5 text-sm text-left transition ${
            value === opt.value
              ? "border-accent bg-accent-soft text-accent-glow"
              : "border-border bg-panel-raised text-ink-muted hover:border-accent/40"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export default function OnboardingPage() {
  const router = useRouter();
  const [stepIndex, setStepIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // profile
  const [name, setName] = useState("");
  const [experience, setExperience] = useState<ExperienceLevel | null>(null);
  const [skillsText, setSkillsText] = useState("");
  const [interestsText, setInterestsText] = useState("");

  // business
  const [businessName, setBusinessName] = useState("");
  const [stage, setStage] = useState<BusinessStage | null>(null);
  const [businessType, setBusinessType] = useState<BusinessType | null>(null);
  const [primaryGoal, setPrimaryGoal] = useState<PrimaryGoal | null>(null);

  // brain
  const [industry, setIndustry] = useState("");
  const [description, setDescription] = useState("");
  const [productsServices, setProductsServices] = useState("");
  const [targetCustomers, setTargetCustomers] = useState("");
  const [companyGoals, setCompanyGoals] = useState("");

  // resources
  const [timePerWeek, setTimePerWeek] = useState("");
  const [budgetRange, setBudgetRange] = useState<BudgetRange | null>(null);
  const [challengesText, setChallengesText] = useState("");

  const step: Step = STEPS[stepIndex];

  async function goNext() {
    setError(null);
    setLoading(true);
    try {
      if (step === "profile") {
        await apiClient.post("/onboarding/profile", {
          name,
          experience_level: experience,
          skills: skillsText.split(",").map((s) => s.trim()).filter(Boolean),
          interests: interestsText.split(",").map((s) => s.trim()).filter(Boolean),
        });
      } else if (step === "business") {
        await apiClient.post("/onboarding/business", {
          business_name: businessName,
          stage,
          business_type: businessType,
          primary_goal: primaryGoal,
        });
      } else if (step === "brain") {
        await apiClient.post("/onboarding/business-brain", {
          industry: industry.trim() || null,
          description: description.trim() || null,
          products_services: productsServices.trim() || null,
          target_customers: targetCustomers.trim() || null,
          company_goals: companyGoals.trim() || null,
        });
      } else if (step === "resources") {
        await apiClient.post("/onboarding/resources", {
          available_time_per_week: timePerWeek ? Number(timePerWeek) : null,
          budget_range: budgetRange,
          current_challenges: challengesText.split(",").map((s) => s.trim()).filter(Boolean),
        });
        await apiClient.post("/onboarding/complete");
        router.push("/workspace");
        return;
      }
      setStepIndex((i) => i + 1);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-6 py-12 bg-night text-night-text">
      <Card className="w-full max-w-lg">
        <div className="flex gap-1.5 mb-6">
          {STEPS.map((s, i) => (
            <div
              key={s}
              className={`h-1 flex-1 rounded-full ${i <= stepIndex ? "bg-accent" : "bg-panel-raised"}`}
            />
          ))}
        </div>

        {step === "profile" && (
          <>
            <h1 className="font-display text-xl font-medium mb-1">Tell us about you</h1>
            <p className="text-sm text-ink-muted mb-6">This helps your AI CEO assistant tailor advice.</p>
            <div className="space-y-4">
              <div>
                <label className="label block mb-1.5">Your name</label>
                <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Alex Rivera" />
              </div>
              <div>
                <label className="label block mb-1.5">Experience level</label>
                <OptionGrid
                  options={[
                    { value: "beginner", label: "Beginner" },
                    { value: "intermediate", label: "Intermediate" },
                    { value: "experienced", label: "Experienced" },
                  ]}
                  value={experience}
                  onChange={setExperience}
                />
              </div>
              <div>
                <label className="label block mb-1.5">Skills (comma separated)</label>
                <Input value={skillsText} onChange={(e) => setSkillsText(e.target.value)} placeholder="marketing, design, sales" />
              </div>
              <div>
                <label className="label block mb-1.5">Interests (comma separated)</label>
                <Input value={interestsText} onChange={(e) => setInterestsText(e.target.value)} placeholder="AI, fitness, coaching" />
              </div>
            </div>
          </>
        )}

        {step === "business" && (
          <>
            <h1 className="font-display text-xl font-medium mb-1">Your business</h1>
            <p className="text-sm text-ink-muted mb-6">Where are things at right now?</p>
            <div className="space-y-4">
              <div>
                <label className="label block mb-1.5">Business name</label>
                <Input value={businessName} onChange={(e) => setBusinessName(e.target.value)} placeholder="Aurora Studio" />
              </div>
              <div>
                <label className="label block mb-1.5">Current stage</label>
                <OptionGrid options={STAGE_OPTIONS} value={stage} onChange={setStage} />
              </div>
              <div>
                <label className="label block mb-1.5">Business type</label>
                <OptionGrid options={TYPE_OPTIONS} value={businessType} onChange={setBusinessType} />
              </div>
              <div>
                <label className="label block mb-1.5">Primary goal</label>
                <OptionGrid options={GOAL_OPTIONS} value={primaryGoal} onChange={setPrimaryGoal} />
              </div>
            </div>
          </>
        )}

        {step === "brain" && (
          <>
            <h1 className="font-display text-xl font-medium mb-1">Give your AI more to work with</h1>
            <p className="text-sm text-ink-muted mb-6">
              Optional, but the more you share, the sharper your AI CEO's advice gets. Skip anything
              you'd rather fill in later.
            </p>
            <div className="space-y-4">
              <div>
                <label className="label block mb-1.5">Industry</label>
                <Input value={industry} onChange={(e) => setIndustry(e.target.value)} placeholder="e.g. Marketing services" />
              </div>
              <div>
                <label className="label block mb-1.5">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  placeholder="What does this business actually do?"
                  className="input-field resize-none"
                />
              </div>
              <div>
                <label className="label block mb-1.5">Products or services offered</label>
                <textarea
                  value={productsServices}
                  onChange={(e) => setProductsServices(e.target.value)}
                  rows={3}
                  placeholder="What do you sell?"
                  className="input-field resize-none"
                />
              </div>
              <div>
                <label className="label block mb-1.5">Target customers</label>
                <textarea
                  value={targetCustomers}
                  onChange={(e) => setTargetCustomers(e.target.value)}
                  rows={3}
                  placeholder="Who are you selling to?"
                  className="input-field resize-none"
                />
              </div>
              <div>
                <label className="label block mb-1.5">Company goals</label>
                <textarea
                  value={companyGoals}
                  onChange={(e) => setCompanyGoals(e.target.value)}
                  rows={3}
                  placeholder="What are you trying to achieve?"
                  className="input-field resize-none"
                />
              </div>
            </div>
          </>
        )}

        {step === "resources" && (
          <>
            <h1 className="font-display text-xl font-medium mb-1">Your resources</h1>
            <p className="text-sm text-ink-muted mb-6">Last step - this shapes your roadmap pacing.</p>
            <div className="space-y-4">
              <div>
                <label className="label block mb-1.5">Available hours per week</label>
                <Input
                  type="number"
                  value={timePerWeek}
                  onChange={(e) => setTimePerWeek(e.target.value)}
                  placeholder="10"
                />
              </div>
              <div>
                <label className="label block mb-1.5">Budget range</label>
                <OptionGrid options={BUDGET_OPTIONS} value={budgetRange} onChange={setBudgetRange} />
              </div>
              <div>
                <label className="label block mb-1.5">Current challenges (comma separated)</label>
                <Input
                  value={challengesText}
                  onChange={(e) => setChallengesText(e.target.value)}
                  placeholder="finding customers, pricing, time management"
                />
              </div>
            </div>
          </>
        )}

        {error && <p className="text-sm text-danger mt-4">{error}</p>}

        <div className="flex justify-between mt-8">
          {stepIndex > 0 ? (
            <Button variant="secondary" onClick={() => setStepIndex((i) => i - 1)}>
              Back
            </Button>
          ) : (
            <span />
          )}
          <Button onClick={goNext} disabled={loading}>
            {loading ? "Saving…" : step === "resources" ? "Finish setup" : "Continue"}
          </Button>
        </div>
      </Card>
    </main>
  );
}
