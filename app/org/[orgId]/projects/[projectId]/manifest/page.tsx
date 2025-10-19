export default function ProjectManifestPage({
    params,
}: {
    params: { orgId: string; projectId: string };
}) {
    const { projectId } = params;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold">Manifest</h2>
                <p className="text-muted-foreground">
                    Export curated asset collections and metadata for{" "}
                    {projectId}.
                </p>
            </div>
            <div className="rounded-lg border border-border bg-card p-6">
                <p className="text-sm text-muted-foreground">
                    Wire this page up to your backend manifest builder to
                    generate export payloads.
                </p>
            </div>
        </div>
    );
}
