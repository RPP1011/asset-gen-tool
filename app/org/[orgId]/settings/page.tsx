export default function OrgSettingsPage({
    params,
}: {
    params: { orgId: string };
}) {
    const { orgId } = params;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold">
                    Organization settings
                </h2>
                <p className="text-muted-foreground">
                    Configure billing, integrations, and guardrails for {orgId}.
                </p>
            </div>
            <div className="rounded-lg border border-border bg-card p-6">
                <p className="text-sm text-muted-foreground">
                    Hook this page up to your backend to manage organization
                    settings.
                </p>
            </div>
        </div>
    );
}
