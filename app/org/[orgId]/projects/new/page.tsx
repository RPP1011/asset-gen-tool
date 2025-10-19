import { Button } from "@/components/ui/button";

export default function OrgProjectCreatePage({
    params,
}: {
    params: { orgId: string };
}) {
    const { orgId } = params;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold">Create a new project</h2>
                <p className="text-muted-foreground">
                    Define the scope for the next asset generation initiative in{" "}
                    {orgId}.
                </p>
            </div>
            <form className="grid gap-4 rounded-lg border border-border bg-card p-6">
                <div className="flex flex-col gap-1">
                    <label className="text-sm font-medium" htmlFor="name">
                        Project name
                    </label>
                    <input
                        id="name"
                        className="h-10 rounded-md border border-input bg-background px-3 text-sm"
                        placeholder="Project name"
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
                        placeholder="Describe the vision and deliverables."
                    />
                </div>
                <Button type="submit">Create project</Button>
            </form>
        </div>
    );
}
