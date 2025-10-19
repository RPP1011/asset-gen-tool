export default function ProjectThemeDetailPage({
  params,
}: {
  params: { orgId: string; projectId: string; themeId: string };
}) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold capitalize">{params.themeId}</h2>
        <p className="text-muted-foreground">
          Adjust references, palettes, and linked assets for this theme.
        </p>
      </div>
      <div className="rounded-lg border border-border bg-card p-6">
        <p className="text-sm text-muted-foreground">
          Add your own data to populate theme details and audit history.
        </p>
      </div>
    </div>
  );
}
