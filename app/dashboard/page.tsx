import Link from "next/link";
import { Button } from "@/components/ui/button";

const demoOrgs = [
  {
    id: "arcade",
    name: "Arcade Interactive",
    projects: 4,
  },
  {
    id: "solar",
    name: "Solar Synth Labs",
    projects: 2,
  },
];

export default function DashboardPage() {
  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-8 py-12">
      <div className="space-y-2">
        <h1 className="text-3xl font-semibold">Organizations</h1>
        <p className="text-muted-foreground">
          Switch between organizations to manage projects and creative output.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {demoOrgs.map((org) => (
          <Link
            key={org.id}
            href={`/org/${org.id}`}
            className="group rounded-lg border border-border bg-card p-6"
          >
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium group-hover:text-primary">
                {org.name}
              </h2>
              <span className="text-sm text-muted-foreground">
                {org.projects} projects
              </span>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">
              Explore teams and assets for {org.name}.
            </p>
          </Link>
        ))}
      </div>

      <Button className="w-fit" asChild>
        <Link href="/org/new">Create new organization</Link>
      </Button>
    </div>
  );
}
