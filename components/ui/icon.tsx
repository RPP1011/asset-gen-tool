import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";
import {
  BadgeCheck,
  Boxes,
  ClipboardList,
  FileImage,
  FileText,
  Images,
  LayoutDashboard,
  Palette,
  Package,
  Settings,
  Sparkles,
  Users,
  Workflow,
} from "lucide-react";

const iconMap: Record<string, LucideIcon> = {
  dashboard: LayoutDashboard,
  assets: Boxes,
  package: Package,
  image: Images,
  palette: Palette,
  manifest: FileText,
  scroll: FileText,
  settings: Settings,
  users: Users,
  team: Users,
  invite: BadgeCheck,
  projects: Workflow,
  concepts: FileImage,
  themes: Palette,
  generate: Sparkles,
  checklist: ClipboardList,
};

interface IconProps {
  name: string;
  className?: string;
}

export function Icon({ name, className }: IconProps) {
  const IconComponent = iconMap[name];

  if (!IconComponent) {
    return null;
  }

  return <IconComponent className={cn("h-4 w-4", className)} />;
}
