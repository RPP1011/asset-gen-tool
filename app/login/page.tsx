import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  return (
    <div className="mx-auto flex w-full max-w-sm flex-col gap-6 py-16">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-semibold">Welcome back</h1>
        <p className="text-sm text-muted-foreground">
          Sign in to continue managing your projects.
        </p>
      </div>
      <form className="space-y-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            type="email"
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            placeholder="you@example.com"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium" htmlFor="password">
            Password
          </label>
          <input
            id="password"
            type="password"
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            placeholder="••••••••"
          />
        </div>
        <Button className="w-full" type="submit">
          Sign in
        </Button>
      </form>
      <p className="text-center text-sm text-muted-foreground">
        Don&apos;t have an account?{" "}
        <Link className="font-medium text-primary" href="/signup">
          Sign up
        </Link>
      </p>
    </div>
  );
}
