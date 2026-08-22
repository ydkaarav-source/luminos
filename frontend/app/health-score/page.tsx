import { redirect } from "next/navigation";

export default function HealthScorePage() {
  redirect("/workspace?tab=health-score");
}
