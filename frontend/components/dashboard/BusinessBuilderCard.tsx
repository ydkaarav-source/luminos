import Link from "next/link";
import { Card, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export function BusinessBuilderCard() {
  return (
    <Card>
      <CardHeader title="Business Builder" subtitle="Turn an idea into a plan" />
      <p className="text-sm text-night-text-muted leading-relaxed mb-4">
        Describe a business idea and get a target customer analysis, revenue
        model, launch roadmap, and action plan generated for you.
      </p>
      <Link href="/business-builder">
        <Button className="w-full">Generate a plan</Button>
      </Link>
    </Card>
  );
}
