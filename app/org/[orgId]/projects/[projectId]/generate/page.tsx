export default function ProjectGeneratePage({
    params,
}: {
    params: { orgId: string; projectId: string };
}) {
    const { projectId } = params;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold">Batch generate</h2>
                <p className="text-muted-foreground">
                    Queue prompts and produce large batches of assets with
                    consistent settings for {projectId}.
                </p>
            </div>
            <div className="rounded-lg border border-border bg-card p-6">
                <p className="text-sm text-muted-foreground">
                    Plug in your orchestration layer to trigger batch runs and
                    monitor job status.
                </p>
            </div>
        </div>
    );
}
