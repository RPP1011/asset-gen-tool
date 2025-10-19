import { Button } from "@/components/ui/button";

export default function ProjectThemeCreatePage({
    params,
}: {
    params: { orgId: string; projectId: string };
}) {
    const { projectId } = params;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold">Create theme</h2>
                <p className="text-muted-foreground">
                    Define the tonal anchors and references for a group of
                    assets in {projectId}.
                </p>
            </div>
            <form className="grid gap-4 rounded-lg border border-border bg-card p-6">
                <div className="flex flex-col gap-1">
                    <label className="text-sm font-medium" htmlFor="name">
                        Theme name
                    </label>
                    <input
                        id="name"
                        className="h-10 rounded-md border border-input bg-background px-3 text-sm"
                        placeholder="Synthwave city"
                    />
                </div>
                <div className="flex flex-col gap-1">
                    <label
                        className="text-sm font-medium"
                        htmlFor="description"
                    >
                        Description
                    </label>
                    <textarea
                        id="description"
                        className="min-h-[120px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                        placeholder="Describe the tone, color palette, and mood for this theme."
                    />
                </div>
                <Button type="submit">Create theme</Button>
            </form>
        </div>
    );
}
