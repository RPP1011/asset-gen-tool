import { Button } from "@/components/ui/button";

export default function OrgInvitePage({
    params,
}: {
    params: { orgId: string };
}) {
    const { orgId } = params;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold">Invite collaborators</h2>
                <p className="text-muted-foreground">
                    Send secure invites to bring teammates into {orgId}.
                </p>
            </div>
            <form className="grid gap-4 rounded-lg border border-border bg-card p-6 sm:grid-cols-[2fr_1fr_auto] sm:items-end">
                <div className="sm:col-span-2">
                    <label className="text-sm font-medium" htmlFor="emails">
                        Email addresses
                    </label>
                    <textarea
                        id="emails"
                        className="mt-2 min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        placeholder="Add one email per line"
                    />
                </div>
                <div className="flex flex-col gap-2">
                    <label className="text-sm font-medium" htmlFor="role">
                        Role
                    </label>
                    <select
                        id="role"
                        className="h-10 rounded-md border border-input bg-background px-3 text-sm"
                        defaultValue="editor"
                    >
                        <option value="admin">Admin</option>
                        <option value="editor">Editor</option>
                        <option value="viewer">Viewer</option>
                    </select>
                </div>
                <Button type="submit">Send invites</Button>
            </form>
        </div>
    );
}
