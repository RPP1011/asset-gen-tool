import { Button } from "@/components/ui/button";

interface AcceptInvitePageProps {
  searchParams: Record<string, string | string[] | undefined>;
}

export default function AcceptInvitePage({
  searchParams,
}: AcceptInvitePageProps) {
  const token = typeof searchParams.token === "string" ? searchParams.token : "";

  return (
    <div className="mx-auto flex w-full max-w-md flex-col gap-6 py-16">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-semibold">Accept organization invite</h1>
        <p className="text-sm text-muted-foreground">
          Join your team and start collaborating right away.
        </p>
      </div>
      <div className="rounded-lg border border-border bg-card p-6">
        <dl className="space-y-2 text-sm">
          <div className="flex items-center justify-between">
            <dt className="text-muted-foreground">Invite token</dt>
            <dd className="font-mono text-xs">{token || "N/A"}</dd>
          </div>
        </dl>
      </div>
      <Button className="w-full" disabled={!token}>
        Accept invite
      </Button>
    </div>
  );
}
