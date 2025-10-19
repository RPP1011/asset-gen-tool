import { Button } from "@/components/ui/button";

export default function ProjectConceptCreatePage({
    params,
}: {
    params: { orgId: string; projectId: string };
}) {
    const { projectId } = params;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold">New concept</h2>
                <p className="text-muted-foreground">
                    Capture references and creative direction for a new concept
                    pass in {projectId}.
                </p>
            </div>
            <form className="grid gap-4 rounded-lg border border-border bg-card p-6">
                <div className="flex flex-col gap-1">
                    <label className="text-sm font-medium" htmlFor="title">
                        Concept title
                    </label>
                    <input
                        id="title"
                        className="h-10 rounded-md border border-input bg-background px-3 text-sm"
                        placeholder="Ex. Vaporwave Alley Moodboard"
                    />
                </div>
                <div className="flex flex-col gap-1">
                    <label className="text-sm font-medium" htmlFor="notes">
                        Notes
                    </label>
                    <textarea
                        id="notes"
                        className="min-h-[120px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                        placeholder="Add reference links and creative direction."
                    />
                </div>
                <Button type="submit">Save concept</Button>
            </form>
        </div>
    );
}
