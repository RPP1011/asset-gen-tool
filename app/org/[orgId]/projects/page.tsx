import Link from "next/link";
import { Button } from "@/components/ui/button";

const demoProjects = [
  { id: "galaxy-runner", name: "Galaxy Runner", status: "Production" },
  { id: "nebula-night", name: "Nebula Night", status: "Concept" },
];

export default function OrgProjectsPage({
  params,
}: {
  params: { orgId: string };
}) {
  const { orgId } = params;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Projects</h2>
          <p className="text-muted-foreground">
            Explore and manage projects within this organization.
          </p>
        </div>
        <Button asChild>
          <Link href={`/org/${orgId}/projects/new`}>New project</Link>
        </Button>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {demoProjects.map((project) => (
          <Link
            key={project.id}
            href={`/org/${orgId}/projects/${project.id}`}
            className="rounded-lg border border-border bg-card p-6 transition hover:border-primary"
          >
            <h3 className="text-lg font-medium">{project.name}</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Status: {project.status}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
