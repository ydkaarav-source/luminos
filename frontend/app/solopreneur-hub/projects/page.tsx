import { redirect } from "next/navigation";

export default function ProjectsPage() {
  redirect("/workspace?tab=solopreneur-hub&subtab=projects");
}
