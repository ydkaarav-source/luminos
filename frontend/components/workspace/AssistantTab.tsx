import { ChatPanel } from "@/components/assistant/ChatPanel";

export function AssistantTab() {
  return (
    <>
      <h1 className="font-display text-2xl font-medium mb-1">AI Assistant</h1>
      <p className="text-night-text-muted mb-6">
        Calm, strategic, and grounded in your business context - not just a Q&A bot.
      </p>
      <ChatPanel />
    </>
  );
}
