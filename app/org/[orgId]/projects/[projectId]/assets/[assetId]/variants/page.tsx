export default function AssetVariantsPage({
    params,
}: {
    params: { orgId: string; projectId: string; assetId: string };
}) {
    const { assetId } = params;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold capitalize">
                    {assetId} variants
                </h2>
                <p className="text-muted-foreground">
                    Review, rate, and approve asset variations.
                </p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {Array.from({ length: 6 }).map((_, index) => (
                    <div
                        key={index}
                        className="aspect-video rounded-lg border border-border bg-muted"
                    />
                ))}
            </div>
        </div>
    );
}
