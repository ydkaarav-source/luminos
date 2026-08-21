import { Card, CardHeader } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { CEOBriefing } from "@/lib/types";

export function CEOBriefingCard({ briefing }: { briefing: CEOBriefing | null }) {
  return (
    <Card>
      <CardHeader
        title="CEO Briefing"
        subtitle="Today's strategic read on your business"
        action={
          briefing && (
            <div className="flex items-center gap-2">
              {briefing.is_demo && <Badge variant="demo">Demo</Badge>}
              <Badge variant={briefing.confidence}>{briefing.confidence} confidence</Badge>
            </div>
          )
        }
      />
      {briefing ? (
        <div>
          <p className="font-display text-sm font-medium text-night-text mb-2">{briefing.finding}</p>
          <p className="text-sm text-night-text-muted leading-relaxed">{briefing.recommendation}</p>
        </div>
      ) : (
        <p className="text-sm text-night-text-muted">Generating today's briefing…</p>
      )}
    </Card>
  );
}
