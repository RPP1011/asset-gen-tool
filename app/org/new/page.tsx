import { Button } from "@/components/ui/button";

export default function OrgCreatePage() {
  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-6 py-12">
      <div>
        <h1 className="text-3xl font-semibold">Create organization</h1>
        <p className="text-muted-foreground">
          Spin up a new workspace to collaborate with your team.
        </p>
      </div>
      <form className="grid gap-4 rounded-lg border border-border bg-card p-6">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium" htmlFor="name">
            Organization name
          </label>
          <input
            id="name"
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            placeholder="Ex. Arcade Interactive"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium" htmlFor="plan">
            Plan
          </label>
          <select
            id="plan"
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            defaultValue="studio"
          >
            <option value="starter">Starter</option>
            <option value="studio">Studio</option>
            <option value="enterprise">Enterprise</option>
          </select>
        </div>
        <Button type="submit">Create organization</Button>
      </form>
    </div>
  );
}
