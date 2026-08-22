import { Suspense } from "react";

import { WorkspaceContent } from "@/components/workspace/WorkspaceContent";

export default function WorkspacePage() {
  return (
    <Suspense>
      <WorkspaceContent />
    </Suspense>
  );
}
