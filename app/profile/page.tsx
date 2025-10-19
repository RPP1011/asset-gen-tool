export default function ProfilePage() {
  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-6 py-12">
      <div className="space-y-2">
        <h1 className="text-3xl font-semibold">Profile</h1>
        <p className="text-muted-foreground">
          Manage your personal settings and account preferences.
        </p>
      </div>

      <div className="rounded-lg border border-border bg-card p-6">
        <h2 className="text-lg font-medium">Account details</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          This is a stub page. Connect to your data source to display real
          account information.
        </p>
      </div>
    </div>
  );
}
