import { redirect } from "next/navigation";

export default function DashboardPage() {
  redirect("/workspace?tab=dashboard");
}
