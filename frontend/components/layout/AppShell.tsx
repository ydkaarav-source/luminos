import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

export function AppShell({
  children,
  businessName,
}: {
  children: React.ReactNode;
  businessName?: string;
}) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <TopBar businessName={businessName} />
        <div className="flex-1 px-6 md:px-8 py-8 max-w-6xl w-full mx-auto">{children}</div>
      </div>
    </div>
  );
}
