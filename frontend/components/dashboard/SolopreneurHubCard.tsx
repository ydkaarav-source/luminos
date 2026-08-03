import Link from "next/link";
import { Card, CardHeader } from "@/components/ui/Card";
import type { Task } from "@/lib/types";

export function SolopreneurHubCard({ tasks }: { tasks: Task[] }) {
  const open = tasks.filter((t) => t.status !== "done").slice(0, 4);

  return (
    <Card>
      <CardHeader title="Solopreneur Hub" subtitle="Your open tasks" />
      {open.length === 0 ? (
        <p className="text-sm text-ink-faint">No open tasks - nice work.</p>
      ) : (
        <ul className="space-y-2.5">
          {open.map((task) => (
            <li key={task.id} className="flex items-center gap-3 text-sm">
              <span
                className={`h-1.5 w-1.5 rounded-full shrink-0 ${
                  task.priority === "high"
                    ? "bg-warning"
                    : task.priority === "medium"
                    ? "bg-accent"
                    : "bg-ink-faint"
                }`}
              />
              <span className="text-ink truncate">{task.title}</span>
            </li>
          ))}
        </ul>
      )}
      <Link href="/solopreneur-hub/tasks" className="text-xs text-accent hover:text-accent-glow mt-4 inline-block">
        View all tasks →
      </Link>
    </Card>
  );
}
