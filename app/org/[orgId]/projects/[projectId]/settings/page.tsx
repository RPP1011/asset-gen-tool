export default function ProjectSettingsPage({
    params,
}: {
    params: { orgId: string; projectId: string };
}) {
    const { projectId } = params;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold">Project settings</h2>
                <p className="text-muted-foreground">
                    Configure prompts, guardrails, and delivery targets for{" "}
                    {projectId}.
                </p>
            </div>
            <div className="rounded-lg border border-border bg-card p-6">
                <p className="text-sm text-muted-foreground">
                    Connect this view to your backend to manage project
                    settings.
                </p>
            </div>
        </div>
    );
}
