import { type NavItem } from "@/types/nav";

export const mainNavigation = (
  orgId: string,
  projectId: string,
): NavItem[] => [
  {
    title: "Dashboard",
    href: `/org/${orgId}/projects/${projectId}`,
    icon: "dashboard",
  },
  {
    title: "Assets",
    href: `/org/${orgId}/projects/${projectId}/assets`,
    icon: "package",
  },
  {
    title: "Concept Art",
    href: `/org/${orgId}/projects/${projectId}/concepts`,
    icon: "image",
  },
  {
    title: "Themes",
    href: `/org/${orgId}/projects/${projectId}/themes`,
    icon: "palette",
  },
  {
    title: "Manifest",
    href: `/org/${orgId}/projects/${projectId}/manifest`,
    icon: "scroll",
  },
  {
    title: "Settings",
    href: `/org/${orgId}/projects/${projectId}/settings`,
    icon: "settings",
  },
];
