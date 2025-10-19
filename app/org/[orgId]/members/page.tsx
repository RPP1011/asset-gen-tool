const demoMembers = [
    { name: "Aiko Tanaka", role: "Creative Director" },
    { name: "Jordan Miles", role: "Lead Artist" },
    { name: "Priya Singh", role: "Producer" },
];

export default function OrgMembersPage({
    params,
}: {
    params: { orgId: string };
}) {
    const { orgId } = params;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-semibold">Team members</h2>
                <p className="text-muted-foreground">
                    Manage roles and permissions for collaborators in {orgId}.
                </p>
            </div>
            <ul className="divide-y divide-border rounded-lg border border-border bg-card">
                {demoMembers.map((member) => (
                    <li
                        key={member.name}
                        className="flex items-center justify-between p-4"
                    >
                        <div>
                            <p className="font-medium">{member.name}</p>
                            <p className="text-sm text-muted-foreground">
                                {member.role}
                            </p>
                        </div>
                        <button className="text-sm font-medium text-primary hover:underline">
                            Manage
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}
