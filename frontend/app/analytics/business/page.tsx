import { redirect } from "next/navigation";

export default function BusinessAnalyticsPage() {
  redirect("/workspace?tab=analytics&subtab=business");
}
