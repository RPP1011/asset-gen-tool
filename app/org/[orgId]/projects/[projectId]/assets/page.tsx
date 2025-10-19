import Link from "next/link";
import { Button } from "@/components/ui/button";

const demoAssets = [
  { id: "pilot-suit", name: "Pilot Suit Concept", status: "In review" },
  { id: "portal-gun", name: "Portal Gun", status: "Approved" },
  { id: "hoverboard", name: "Hoverboard Model", status: "In progress" },
];

export default function ProjectAssetsPage({
  params,
}: {
  params: { orgId: string; projectId: string };
}) {
  const { orgId, projectId } = params;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Assets</h2>
          <p className="text-muted-foreground">
            Browse generated assets and track their review status.
          </p>
        </div>
        <Button asChild>
          <Link href={`/org/${orgId}/projects/${projectId}/assets/new`}>
            New asset brief
          </Link>
        </Button>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {demoAssets.map((asset) => (
          <Link
            key={asset.id}
            href={`/org/${orgId}/projects/${projectId}/assets/${asset.id}`}
            className="rounded-lg border border-border bg-card p-5 transition hover:border-primary"
          >
            <h3 className="text-lg font-medium">{asset.name}</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Status: {asset.status}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
