import { Sidebar } from "@/components/sidebar";
import { mainNavigation } from "@/lib/nav";

interface ProjectLayoutProps {
  children: React.ReactNode;
  params: {
    orgId: string;
    projectId: string;
  };
}

export default function ProjectLayout({
  children,
  params,
}: ProjectLayoutProps) {
  const { orgId, projectId } = params;

  return (
    <div className="flex min-h-[calc(100vh-52px)]">
      <Sidebar items={mainNavigation(orgId, projectId)} />
      <main className="flex-1 overflow-y-auto px-8 py-10">{children}</main>
    </div>
  );
}
