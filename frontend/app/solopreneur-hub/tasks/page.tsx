import { redirect } from "next/navigation";

export default function TasksPage() {
  redirect("/workspace?tab=solopreneur-hub&subtab=tasks");
}
