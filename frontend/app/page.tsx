import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-6 text-center">
      <span className="label mb-4">LuminOS</span>
      <h1 className="font-display text-4xl md:text-5xl font-medium max-w-2xl leading-tight">
        The AI operating system for entrepreneurs.
      </h1>
      <p className="mt-4 text-ink-muted max-w-lg">
        Go from business idea to daily execution with a calm, strategic AI CEO
        assistant built for solopreneurs.
      </p>
      <div className="mt-8 flex gap-3">
        <Link href="/signup" className="btn-primary">
          Get started
        </Link>
        <Link href="/login" className="btn-secondary">
          Log in
        </Link>
      </div>
    </main>
  );
}
