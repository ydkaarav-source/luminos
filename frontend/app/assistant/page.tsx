import { ChatPanel } from "@/components/assistant/ChatPanel";
import { AppShell } from "@/components/layout/AppShell";

export default function AssistantPage() {
  return (
    <AppShell>
      <h1 className="font-display text-2xl font-medium mb-1">AI Assistant</h1>
      <p className="text-ink-muted mb-6">
        Calm, strategic, and grounded in your business context - not just a Q&A bot.
      </p>
      <ChatPanel />
    </AppShell>
  );
}
