import { redirect } from "next/navigation";

export default function PortfolioPage() {
  redirect("/workspace?tab=analytics&subtab=portfolio");
}
