import Link from "next/link";
import { Button } from "@/components/ui/button";

const demoConcepts = [
  { id: "cityscape", name: "Cityscape Moodboard" },
  { id: "hero-silhouette", name: "Hero Silhouette" },
];

export default function ProjectConceptsPage({
  params,
}: {
  params: { orgId: string; projectId: string };
}) {
  const { orgId, projectId } = params;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Concept art</h2>
          <p className="text-muted-foreground">
            Track explorations and target references for the project.
          </p>
        </div>
        <Button asChild>
          <Link href={`/org/${orgId}/projects/${projectId}/concepts/new`}>
            New concept
          </Link>
        </Button>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {demoConcepts.map((concept) => (
          <Link
            key={concept.id}
            href={`/org/${orgId}/projects/${projectId}/concepts/${concept.id}`}
            className="rounded-lg border border-border bg-card p-6"
          >
            <h3 className="text-lg font-medium">{concept.name}</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Click to view details and related assets.
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
