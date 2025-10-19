export default function ProjectConceptDetailPage({
  params,
}: {
  params: { orgId: string; projectId: string; conceptId: string };
}) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold capitalize">
          {params.conceptId}
        </h2>
        <p className="text-muted-foreground">
          Review the vision, references, and linked assets for this concept.
        </p>
      </div>
      <div className="rounded-lg border border-border bg-card p-6">
        <p className="text-sm text-muted-foreground">
          Populate this section with concept imagery and commentary from your
          team.
        </p>
      </div>
    </div>
  );
}
