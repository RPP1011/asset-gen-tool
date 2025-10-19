export default function ProjectDashboardPage({
  params,
}: {
  params: { orgId: string; projectId: string };
}) {
  const { projectId } = params;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold capitalize">{projectId}</h1>
        <p className="text-muted-foreground">
          Monitor milestones, production progress, and outstanding work.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {[
          { label: "Generated assets", value: "128" },
          { label: "Active themes", value: "6" },
          { label: "Pending reviews", value: "9" },
        ].map((metric) => (
          <div
            key={metric.label}
            className="rounded-lg border border-border bg-card p-5"
          >
            <p className="text-sm text-muted-foreground">{metric.label}</p>
            <p className="mt-2 text-2xl font-semibold">{metric.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
