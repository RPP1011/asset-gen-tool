import { Chat } from "@/components/chat";

export default function AssetDetailPage({
    params,
}: {
    params: { orgId: string; projectId: string; assetId: string };
}) {
    return (
        <div className="flex flex-col gap-6">
            <header className="space-y-1">
                <h2 className="text-2xl font-semibold capitalize">
                    {params.assetId}
                </h2>
                <p className="text-sm text-muted-foreground">
                    Collaborate with the assistant to iterate on this asset.
                </p>
            </header>
            <div className="rounded-lg border border-border">
                <Chat />
            </div>
        </div>
    );
}
