export default function OrgOverviewPage({
  params,
}: {
  params: { orgId: string };
}) {
  const { orgId } = params;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Overview</h2>
        <p className="text-muted-foreground">
          Get a snapshot of activity and production metrics for {orgId}.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[
          { label: "Active projects", value: "4" },
          { label: "Team members", value: "18" },
          { label: "Open invites", value: "3" },
        ].map((metric) => (
          <div
            key={metric.label}
            className="rounded-lg border border-border bg-card p-4"
          >
            <p className="text-sm text-muted-foreground">{metric.label}</p>
            <p className="mt-2 text-2xl font-semibold">{metric.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
