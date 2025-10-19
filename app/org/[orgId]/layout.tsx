import Link from "next/link";

interface OrgLayoutProps {
  children: React.ReactNode;
  params: {
    orgId: string;
  };
}

const orgNav = [
  { href: "", label: "Overview" },
  { href: "projects", label: "Projects" },
  { href: "members", label: "Members" },
  { href: "invite", label: "Invite" },
  { href: "settings", label: "Settings" },
];

export default function OrgLayout({ children, params }: OrgLayoutProps) {
  const { orgId } = params;

  return (
    <div className="mx-auto w-full max-w-6xl px-6 py-10">
      <header className="space-y-6 border-b border-border pb-6">
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground uppercase tracking-wide">
            Organization
          </p>
          <h1 className="text-3xl font-semibold capitalize">{orgId}</h1>
        </div>
        <nav className="flex flex-wrap gap-3 text-sm">
          {orgNav.map((item) => (
            <Link
              key={item.href}
              href={`/org/${orgId}/${item.href}`.replace(/\/$/, "")}
              className="rounded-md border border-transparent px-3 py-1.5 text-muted-foreground transition-colors hover:border-border hover:text-foreground"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </header>
      <section className="py-8">{children}</section>
    </div>
  );
}
