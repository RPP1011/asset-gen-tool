import Link from "next/link";
import { Button } from "@/components/ui/button";

const demoThemes = [
  { id: "retro-future", name: "Retro Future", assets: 34 },
  { id: "neon-wasteland", name: "Neon Wasteland", assets: 18 },
];

export default function ProjectThemesPage({
  params,
}: {
  params: { orgId: string; projectId: string };
}) {
  const { orgId, projectId } = params;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Themes</h2>
          <p className="text-muted-foreground">
            Organize assets around style guides and creative references.
          </p>
        </div>
        <Button asChild>
          <Link href={`/org/${orgId}/projects/${projectId}/themes/new`}>
            New theme
          </Link>
        </Button>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {demoThemes.map((theme) => (
          <Link
            key={theme.id}
            href={`/org/${orgId}/projects/${projectId}/themes/${theme.id}`}
            className="rounded-lg border border-border bg-card p-6"
          >
            <h3 className="text-lg font-medium">{theme.name}</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              {theme.assets} linked assets
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
