"use client";

import Link from "next/link";
import { useState } from "react";

import { Logo } from "@/components/ui/Logo";

const NAV_LINKS = [
  { href: "#features", label: "Features" },
  { href: "#pricing", label: "Pricing" },
  { href: "#about", label: "About" },
];

const CAPABILITIES = [
  {
    title: "CEO Briefing",
    body: "Pulls this week's revenue, yesterday's task completions, and your latest Health Score from the database before it writes a word.",
  },
  {
    title: "Business Builder",
    body: "Turns a plain-language idea into a target customer, a revenue model, and a 90-day roadmap — stored, not thrown away.",
  },
  {
    title: "Health Score",
    body: "Computed with fixed rules across revenue, operations, marketing, and growth — the same inputs always produce the same score.",
  },
  {
    title: "AI Assistant",
    body: "Reads the same memory pool as every other feature — your goals, decisions, and history carry over between sessions.",
  },
];

const TRUST_ITEMS = [
  {
    label: "Auditable scoring",
    body: "Health Score is computed with plain math, not an AI guess — the same inputs reproduce the same score every time.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M20 6L9 17l-5-5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    label: "Persistent memory",
    body: "Every AI feature reads from the same memory pool. It gets sharper the more you use it, not generic every time.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 3l9 5-9 5-9-5 9-5z" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M3 12l9 5 9-5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    label: "Tenant isolation",
    body: "Every task, revenue entry, and insight is scoped to your business ID at the database level — nothing crosses between accounts.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="4" y="10" width="16" height="10" rx="2" />
        <path d="M8 10V7a4 4 0 018 0v3" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    label: "No fake numbers",
    body: "If something isn't real yet, the product says so — empty states stay empty instead of showing invented data.",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="9" />
        <path d="M12 8v5" strokeLinecap="round" />
        <path d="M12 16h.01" strokeLinecap="round" />
      </svg>
    ),
  },
];

const SPECIFICITY_BARS = [
  { label: "Day 1", heightPct: 22, className: "bg-gray-300" },
  { label: "Week 1", heightPct: 48, className: "bg-accent-soft" },
  { label: "Week 4", heightPct: 74, className: "bg-accent" },
  { label: "Week 12", heightPct: 100, className: "bg-positive" },
];

export default function HomePage() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <main className="min-h-screen bg-canvas text-ink">
      {/* ============ SECTION 1 — Hero (dark) ============ */}
      <section className="relative overflow-hidden bg-night min-h-screen flex flex-col">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "radial-gradient(640px 480px at 82% 8%, rgba(74,222,128,0.28), transparent 60%), radial-gradient(420px 360px at 95% 30%, rgba(22,163,74,0.18), transparent 65%)",
            filter: "blur(2px)",
          }}
        />

        {/* Ribbon/curve decoration — inline SVG, not an image */}
        <svg
          aria-hidden
          className="pointer-events-none absolute right-[-6%] top-0 hidden h-full w-[46%] max-w-[560px] md:block"
          viewBox="0 0 500 700"
          fill="none"
          preserveAspectRatio="xMidYMid slice"
        >
          <defs>
            <linearGradient id="ribbon1" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#0A5C29" />
              <stop offset="55%" stopColor="#16A34A" />
              <stop offset="100%" stopColor="#4ADE80" />
            </linearGradient>
            <linearGradient id="ribbon2" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#0A5C29" />
              <stop offset="60%" stopColor="#16A34A" />
              <stop offset="100%" stopColor="#86EFAC" />
            </linearGradient>
            <linearGradient id="ribbon3" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#16A34A" />
              <stop offset="100%" stopColor="#4ADE80" />
            </linearGradient>
          </defs>
          <path
            d="M470 -20C380 90 560 210 430 320C300 430 460 560 380 720"
            stroke="url(#ribbon1)"
            strokeWidth="10"
            strokeLinecap="round"
            opacity="0.85"
          />
          <path
            d="M380 -20C300 100 470 230 350 340C230 450 380 580 300 720"
            stroke="url(#ribbon2)"
            strokeWidth="16"
            strokeLinecap="round"
            opacity="0.7"
          />
          <path
            d="M300 -20C230 110 380 240 270 350C160 460 300 580 230 720"
            stroke="url(#ribbon3)"
            strokeWidth="5"
            strokeLinecap="round"
            opacity="0.9"
          />
        </svg>

        <div className="relative z-10 flex flex-col flex-1">
          <div className="max-w-6xl mx-auto px-6 h-16 w-full flex items-center justify-between shrink-0">
            <Logo className="text-lg" variant="dark" />

            <nav className="hidden md:flex items-center gap-8">
              {NAV_LINKS.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  className="text-sm text-[#9CA89F] hover:text-night-text transition"
                >
                  {link.label}
                </a>
              ))}
            </nav>

            <div className="hidden md:flex items-center gap-3">
              <Link
                href="/login"
                className="text-sm font-medium border border-night-border text-night-text rounded-lg px-4 py-2 hover:border-accent-bright/50 transition"
              >
                Log in
              </Link>
              <Link
                href="/signup"
                className="text-sm font-medium bg-accent-glow text-night rounded-lg px-4 py-2 shadow-glow hover:bg-accent-bright transition"
              >
                Get started
              </Link>
            </div>

            <button
              onClick={() => setMenuOpen((v) => !v)}
              className="md:hidden text-night-text"
              aria-label="Toggle menu"
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                {menuOpen ? (
                  <path d="M6 6l12 12M18 6L6 18" strokeLinecap="round" />
                ) : (
                  <path d="M4 7h16M4 12h16M4 17h16" strokeLinecap="round" />
                )}
              </svg>
            </button>
          </div>

          {menuOpen && (
            <div className="md:hidden border-t border-night-border bg-night px-6 py-4 flex flex-col gap-4">
              {NAV_LINKS.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  className="text-sm text-[#9CA89F]"
                  onClick={() => setMenuOpen(false)}
                >
                  {link.label}
                </a>
              ))}
              <div className="flex items-center gap-3 pt-2">
                <Link href="/login" className="text-sm text-night-text">
                  Log in
                </Link>
                <Link
                  href="/signup"
                  className="text-sm font-medium bg-accent-glow text-night rounded-lg px-4 py-2"
                >
                  Get started
                </Link>
              </div>
            </div>
          )}

          <div className="flex-1 flex items-center">
            <div className="max-w-4xl px-6 py-16">
              <h1 className="font-serif text-5xl md:text-6xl leading-[1.08] tracking-tight text-night-text">
                The AI operating system <span className="text-accent-bright">for entrepreneurs.</span>
              </h1>
              <p className="mt-6 text-lg text-night-text-muted max-w-xl leading-relaxed">
                Health Score is plain math, not an AI guess — and every
                recommendation reads your actual logged tasks and revenue.
              </p>
              <div className="mt-9 flex items-center gap-3">
                <Link
                  href="/signup"
                  className="bg-accent-glow text-night rounded-lg px-6 py-3 text-sm font-medium shadow-glow hover:bg-accent-bright transition"
                >
                  Get started
                </Link>
                <Link
                  href="/login"
                  className="border border-night-border text-night-text rounded-lg px-6 py-3 text-sm font-medium hover:border-accent-bright/50 transition"
                >
                  Log in
                </Link>
                <Link
                  href="/signup"
                  className="text-sm font-medium text-accent-bright hover:text-night-text transition px-2"
                >
                  Try the demo →
                </Link>
              </div>
              <p className="mt-3 text-xs text-night-text-muted">
                After signing up, you'll see LuminOS running on a real example
                business before you enter your own data.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ============ SECTION 2 — Feature intro (light) ============ */}
      <section id="features" className="bg-panel">
        <div className="max-w-6xl mx-auto px-6 py-20 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div>
            <span className="inline-flex items-center gap-2 text-xs font-medium tracking-[0.18em] text-accent uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-accent" />
              Why LuminOS
            </span>
            <h2 className="font-serif text-3xl md:text-4xl mt-4 text-ink leading-tight">
              <span className="text-accent">Built for founders</span> starting from zero.
            </h2>
            <p className="mt-4 text-ink-muted leading-relaxed">
              Four systems that run alongside you, each reading real data
              before saying anything.
            </p>
            <div className="mt-8 space-y-5">
              {CAPABILITIES.map((c) => (
                <div key={c.title}>
                  <p className="text-sm font-medium text-ink">{c.title}</p>
                  <p className="mt-1 text-sm text-ink-muted leading-relaxed">{c.body}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-border overflow-hidden shadow-card">
            <div
              className="px-5 py-4 flex items-center justify-between"
              style={{ background: "linear-gradient(135deg, #0A5C29, #16A34A)" }}
            >
              <div>
                <p className="text-white text-sm font-medium">Business Health</p>
                <p className="text-white/70 text-xs">This week</p>
              </div>
              <span className="text-[10px] uppercase tracking-wide text-white/70 border border-white/30 rounded-full px-2 py-1">
                Sample view
              </span>
            </div>
            <div className="bg-panel px-5 py-5 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-ink-muted">Health Score</span>
                <span className="text-sm font-medium text-ink">
                  71 <span className="text-positive">↑ 6</span>
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-ink-muted">Revenue, 7d</span>
                <span className="text-sm font-medium text-ink">
                  $1,240 <span className="text-positive">↑ 18%</span>
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-ink-muted">Tasks completed</span>
                <span className="text-sm font-medium text-ink">5</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============ SECTION 3 — Proof / mechanism (dark) ============ */}
      <section className="relative overflow-hidden bg-night">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
          style={{
            background: "radial-gradient(480px 380px at 8% 90%, rgba(74,222,128,0.16), transparent 65%)",
            filter: "blur(2px)",
          }}
        />
        <div className="relative max-w-6xl mx-auto px-6 py-20 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="font-serif text-3xl md:text-4xl text-night-text leading-tight">
              Grounded in real numbers, not vibes.
            </h2>
            <p className="mt-5 text-night-text-muted leading-relaxed">
              CEO Briefing pulls this week's revenue, yesterday's task
              completions, and your latest Health Score straight from the
              database before it generates anything. The AI explains what the
              numbers mean — it doesn't invent them.
            </p>
          </div>

          <div className="rounded-2xl bg-night-card border border-night-border p-6">
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-accent-bright bg-accent/15 rounded-full px-2.5 py-1">
              High confidence
            </span>
            <h3 className="mt-4 font-serif text-xl text-night-text leading-snug">
              Revenue is up, but task completion is falling behind.
            </h3>
            <p className="mt-3 text-sm text-night-text-muted leading-relaxed">
              Revenue rose over the past week, but only 2 of 6 priority tasks
              were completed — worth acting on before it compounds.
            </p>
            <div className="mt-5 pt-5 border-t border-night-border grid grid-cols-3 gap-3 text-center">
              <div>
                <p className="text-lg font-medium text-accent-bright">+18%</p>
                <p className="text-xs text-night-text-muted mt-0.5">Revenue, 7d</p>
              </div>
              <div>
                <p className="text-lg font-medium text-accent-bright">2/6</p>
                <p className="text-xs text-night-text-muted mt-0.5">Tasks done</p>
              </div>
              <div>
                <p className="text-lg font-medium text-accent-bright">71</p>
                <p className="text-xs text-night-text-muted mt-0.5">Health Score</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============ SECTION 4 — Trust / honesty (dark) ============ */}
      <section id="about" className="relative overflow-hidden bg-night border-t border-night-border">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
          style={{
            background: "radial-gradient(520px 420px at 92% 100%, rgba(22,163,74,0.20), transparent 65%)",
            filter: "blur(2px)",
          }}
        />
        <div className="relative max-w-6xl mx-auto px-6 py-20">
          <h2 className="font-serif text-3xl md:text-4xl text-night-text text-center">
            Built to be <span className="text-accent-bright">honest.</span>
          </h2>
          <div className="mt-14 grid grid-cols-1 sm:grid-cols-2 gap-x-10 gap-y-10 max-w-3xl mx-auto">
            {TRUST_ITEMS.map((item) => (
              <div key={item.label} className="flex gap-4">
                <span className="shrink-0 w-9 h-9 rounded-lg bg-accent/15 text-accent-bright flex items-center justify-center">
                  {item.icon}
                </span>
                <div>
                  <p className="text-sm font-semibold text-night-text">{item.label}</p>
                  <p className="mt-1 text-sm text-night-text-muted leading-relaxed">{item.body}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============ SECTION 5 — Time is money (light) ============ */}
      <section className="bg-panel border-t border-border-subtle">
        <div className="max-w-6xl mx-auto px-6 py-20">
          <div className="max-w-2xl">
            <span className="text-xs font-medium tracking-[0.18em] text-accent uppercase">Time is money</span>
            <h2 className="font-serif text-3xl md:text-4xl mt-3 text-ink leading-tight">
              Less time deciding, <span className="text-accent">more time doing.</span>
            </h2>
            <p className="mt-4 text-ink-muted leading-relaxed">
              Business Brain and CEO Briefing exist to cut down the hours
              founders spend figuring out what to do next — not to promise an
              outcome. Here's what actually changes as you use them.
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="rounded-2xl border border-border bg-canvas p-6">
              <p className="text-sm font-medium text-ink">AI output specificity</p>
              <div className="mt-6 h-40 flex items-end gap-4">
                {SPECIFICITY_BARS.map((bar) => (
                  <div key={bar.label} className="flex-1 flex flex-col items-center gap-2">
                    <div className="w-full flex items-end h-32">
                      <div
                        className={`w-full rounded-t-md ${bar.className}`}
                        style={{ height: `${bar.heightPct}%` }}
                      />
                    </div>
                    <span className="text-xs text-ink-faint">{bar.label}</span>
                  </div>
                ))}
              </div>
              <p className="mt-5 text-xs text-ink-faint italic leading-relaxed">
                Illustrative only — output specificity scales with how much
                real data you've logged, not with time alone.
              </p>
            </div>

            <div className="rounded-2xl border border-border bg-canvas p-6">
              <p className="text-sm font-medium text-ink">Weekly planning time</p>
              <div className="mt-6 h-40 flex items-end justify-center gap-10">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-16 flex items-end h-32">
                    <div className="w-full rounded-t-md bg-gray-300" style={{ height: "88%" }} />
                  </div>
                  <span className="text-xs text-ink-faint">Manual</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-16 flex items-end h-32">
                    <div className="w-full rounded-t-md bg-accent" style={{ height: "32%" }} />
                  </div>
                  <span className="text-xs text-ink-faint">With LuminOS</span>
                </div>
              </div>
              <div className="mt-4 flex items-center gap-4 text-xs text-ink-muted">
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-sm bg-gray-300" /> Piecing it together yourself
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-sm bg-accent" /> Starting from a generated briefing
                </span>
              </div>
              <p className="mt-4 text-xs text-ink-faint italic leading-relaxed">
                An illustrative comparison, not a guaranteed time savings for
                every business.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ============ SECTION 6 — Closing CTA (light, pale green) ============ */}
      <section id="pricing" className="bg-canvas border-t border-border-subtle">
        <div className="max-w-2xl mx-auto px-6 py-20 text-center">
          <h2 className="font-serif text-3xl md:text-4xl text-ink">Free to start.</h2>
          <p className="mt-4 text-ink-muted">
            LuminOS is in early access. Create an account and start building —
            paid plans are coming as the product grows.
          </p>
          <div className="mt-8">
            <Link
              href="/signup"
              className="inline-block bg-accent text-white rounded-lg px-6 py-3 text-sm font-medium hover:bg-accent-glow transition"
            >
              Get started
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-border-subtle bg-canvas">
        <div className="max-w-6xl mx-auto px-6 py-10 flex flex-col md:flex-row items-center justify-between gap-4">
          <Logo />
          <p className="text-xs text-ink-faint">
            © {new Date().getFullYear()} LuminOS. Built for entrepreneurs starting out.
          </p>
        </div>
      </footer>
    </main>
  );
}
