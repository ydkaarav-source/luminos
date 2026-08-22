import { redirect } from "next/navigation";

export default function GoalsPage() {
  redirect("/workspace?tab=solopreneur-hub&subtab=goals");
}
