"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Compass,
  FileCheck2,
  History,
  LayoutDashboard,
  Plug,
  PlusCircle,
  ShieldCheck,
  Users,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

const groups: { label: string; items: NavItem[] }[] = [
  {
    label: "Decisions",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
      { href: "/decisions/new", label: "New decision", icon: PlusCircle },
      { href: "/decisions", label: "History", icon: History },
    ],
  },
  {
    label: "Governance",
    items: [
      { href: "/reviews", label: "Reviews", icon: ShieldCheck },
      { href: "/audit", label: "Audit", icon: FileCheck2 },
    ],
  },
  { label: "Insights", items: [{ href: "/analytics", label: "Analytics", icon: BarChart3 }] },
  {
    label: "Settings",
    items: [
      { href: "/settings/members", label: "Members", icon: Users },
      { href: "/settings/connectors", label: "Connectors", icon: Plug },
    ],
  },
];

function isActive(pathname: string, href: string): boolean {
  if (href === "/dashboard") return pathname === "/dashboard";
  if (href === "/decisions") {
    return (
      pathname === "/decisions" ||
      (pathname.startsWith("/decisions/") && !pathname.startsWith("/decisions/new"))
    );
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-line bg-surface md:flex">
      <div className="flex items-center gap-2 px-5 py-5">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white">
          <Compass className="h-5 w-5" />
        </span>
        <span className="text-base font-semibold">TrueNorth</span>
      </div>
      <nav className="flex-1 space-y-6 overflow-y-auto px-3 py-2">
        {groups.map((group) => (
          <div key={group.label}>
            <p className="px-3 pb-2 text-xs font-medium uppercase tracking-wide text-muted">
              {group.label}
            </p>
            <ul className="space-y-1">
              {group.items.map((item) => {
                const active = isActive(pathname, item.href);
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                        active
                          ? "bg-brand-50 font-medium text-brand-700"
                          : "text-muted hover:bg-app hover:text-ink",
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  );
}
