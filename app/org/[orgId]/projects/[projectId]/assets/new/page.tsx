import { Button } from "@/components/ui/button";

export default function ProjectAssetCreatePage({
    params,
}: {
    params: { orgId: string; projectId: string };
}) {
    const { projectId } = params;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold">New asset brief</h2>
                <p className="text-muted-foreground">
                    Describe the asset so the generation pipeline understands
                    the intent for {projectId}.
                </p>
            </div>
            <form className="grid gap-4 rounded-lg border border-border bg-card p-6">
                <div className="flex flex-col gap-1">
                    <label className="text-sm font-medium" htmlFor="title">
                        Asset title
                    </label>
                    <input
                        id="title"
                        className="h-10 rounded-md border border-input bg-background px-3 text-sm"
                        placeholder="Ex. Retro neon corridor"
                    />
                </div>
                <div className="flex flex-col gap-1">
                    <label className="text-sm font-medium" htmlFor="prompt">
                        Creative prompt
                    </label>
                    <textarea
                        id="prompt"
                        className="min-h-[120px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                        placeholder="Detail the mood, lighting, composition, and story beats..."
                    />
                </div>
                <Button type="submit">Generate brief</Button>
            </form>
        </div>
    );
}
