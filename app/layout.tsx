import "./globals.css";
import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { Toaster } from "sonner";
import { cn } from "@/lib/utils";
import { Navbar } from "@/components/navbar";

export const metadata: Metadata = {
    title: "AssetGen",
    description:
        "Manage organizations, projects, and creative assets with the AssetGen dashboard.",
    openGraph: {
        title: "AssetGen",
        description:
            "Manage organizations, projects, and creative assets with the AssetGen dashboard.",
        images: [
            {
                url: "/og?title=AssetGen",
            },
        ],
    },
    twitter: {
        card: "summary_large_image",
        images: [
            {
                url: "/og?title=AssetGen",
            },
        ],
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body
                className={cn(
                    GeistSans.className,
                    "min-h-screen bg-background text-foreground antialiased",
                )}
                suppressHydrationWarning
            >
                <Toaster position="top-center" richColors />
                <Navbar />
                <main className="min-h-[calc(100vh-52px)] bg-background">
                    {children}
                </main>
            </body>
        </html>
    );
}
