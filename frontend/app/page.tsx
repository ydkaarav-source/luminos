"use client";

import Link from "next/link";
import { useState } from "react";

const FEATURES = [
  {
    title: "CEO Briefing",
    body: "A short, honest read on your business every morning — what moved, what's stuck, what to do about it.",
  },
  {
    title: "Business Builder",
    body: "Describe an idea in plain language. Get a target customer, a revenue model, and a 90-day roadmap back.",
  },
  {
    title: "Health Score",
    body: "One number for how your business is actually doing, broken into revenue, operations, marketing, and growth.",
  },
  {
    title: "AI Assistant",
    body: "Not a chatbot. It remembers your goals and decisions, and tells you what to prioritize next.",
  },
];

const NAV_LINKS = [
  { href: "#features", label: "Features" },
  { href: "#pricing", label: "Pricing" },
  { href: "#about", label: "About" },
];

export default function HomePage() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <main className="min-h-screen bg-canvas text-ink">
      <header className="sticky top-0 z-20 bg-canvas/85 backdrop-blur-sm border-b border-border-subtle">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <span className="font-serif text-lg tracking-tight">LuminOS</span>

          <nav className="hidden md:flex items-center gap-8">
            {NAV_LINKS.map((link) => (
     <a
              
                key={link.href}
                href={link.href}
                className="text-sm text-ink-muted hover:text-ink transition"
              >
                {link.label}
              </a>
            ))}
          </nav>

          <div className="hidden md:flex items-center gap-3">
            <Link href="/login" className="text-sm text-ink-muted hover:text-ink transition px-3 py-2">
              Log in
            </Link>
            <Link
              href="/signup"
              className="text-sm font-medium bg-accent text-white rounded-lg px-4 py-2 hover:bg-accent-glow transition"
            >
              Get started
            </Link>
          </div>

          <button
            onClick={() => setMenuOpen((v) => !v)}
            className="md:hidden text-ink"
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
          <div className="md:hidden border-t border-border-subtle bg-canvas px-6 py-4 flex flex-col gap-4">
            {NAV_LINKS.map((link) => (
              <a key={link.href} href={link.href} className="text-sm text-ink-muted" onClick={() => setMenuOpen(false)}>
                {link.label}
              </a>
            ))}
            <div className="flex items-center gap-3 pt-2">
              <Link href="/login" className="text-sm text-ink-muted">Log in</Link>
              <Link href="/signup" className="text-sm font-medium bg-accent text-white rounded-lg px-4 py-2">
                Get started
              </Link>
            </div>
          </div>
        )}
      </header>

      <section className="relative overflow-hidden">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 opacity-80"
          style={{
            background:
              "radial-gradient(560px 360px at 50% 15%, rgba(62,111,212,0.16), transparent 65%), radial-gradient(480px 320px at 65% 40%, rgba(82,185,138,0.10), transparent 65%)",
          }}
        />
        <div className="relative max-w-4xl mx-auto px-6 pt-24 pb-20 text-center">
          <span className="inline-block text-xs font-medium tracking-[0.18em] text-accent-glow uppercase mb-6">
            LuminOS
          </span>
          <h1 className="font-serif text-5xl md:text-6xl leading-[1.08] tracking-tight text-ink">
            The AI operating system
            <br />
            for entrepreneurs.
          </h1>
          <p className="mt-6 text-lg text-ink-muted max-w-xl mx-auto leading-relaxed">
            Go from an idea to daily execution with a calm, strategic AI CEO
            assistant — built for solopreneurs starting an AI dropshipping
            business, day trading, or their first venture.
          </p>
          <div className="mt-9 flex items-center justify-center gap-3">
            <Link
              href="/signup"
              className="bg-accent text-white rounded-lg px-6 py-3 text-sm font-medium hover:bg-accent-glow transition"
            >
              Get started
            </Link>
            <Link
              href="/login"
              className="bg-panel border border-border text-ink rounded-lg px-6 py-3 text-sm font-medium hover:border-accent/50 transition"
            >
              Log in
            </Link>
          </div>

          <div className="mt-14 max-w-xs mx-auto bg-panel border border-border rounded-xl px-5 py-4 text-left">
            <p className="text-xs text-ink-faint mb-1">Health score</p>
            <p className="text-sm text-ink">
              78 <span className="text-positive">↑ steady</span>
            </p>
          </div>
        </div>
      </section>

      <section id="features" className="max-w-6xl mx-auto px-6 py-20 border-t border-border-subtle">
        <div className="max-w-xl mb-12">
          <span className="text-xs font-medium tracking-[0.18em] text-positive uppercase">
            What it does
          </span>
          <h2 className="font-serif text-3xl mt-3 text-ink">
            Four ways LuminOS runs alongside you.
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="bg-panel border border-border rounded-xl p-7 hover:border-accent/40 transition"
            >
              <h3 className="font-serif text-xl text-ink mb-2">{f.title}</h3>
              <p className="text-sm text-ink-muted leading-relaxed">{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="about" className="border-t border-border-subtle bg-panel/40">
        <div className="max-w-3xl mx-auto px-6 py-20 text-center">
          <span className="text-xs font-medium tracking-[0.18em] text-accent-glow uppercase">
            Why we built this
          </span>
          <h2 className="font-serif text-3xl mt-3 mb-5 text-ink">
            Starting a business shouldn't require knowing where to start.
          </h2>
          <p className="text-ink-muted leading-relaxed">
            A lot of young, first-time founders — including plenty of teens
            with a real idea and no roadmap — never take the first step,
            not because the idea is bad, but because nobody around them can
            answer "okay, so what do I actually do today?" LuminOS is built
            to be that answer: an AI CEO assistant that turns an idea into a
            plan, and a plan into a daily to-do list.
          </p>
        </div>
      </section>

      <section id="pricing" className="max-w-4xl mx-auto px-6 py-20 text-center border-t border-border-subtle">
        <span className="text-xs font-medium tracking-[0.18em] text-positive uppercase">
          Pricing
        </span>
        <h2 className="font-serif text-3xl mt-3 mb-4 text-ink">
          Free to start.
        </h2>
        <p className="text-ink-muted max-w-md mx-auto">
          LuminOS is in early access. Create an account and start building —
          paid plans are coming as the product grows.
        </p>
      </section>

      <footer className="border-t border-border-subtle">
        <div className="max-w-6xl mx-auto px-6 py-10 flex flex-col md:flex-row items-center justify-between gap-4">
          <span className="font-serif text-ink">LuminOS</span>
          <p className="text-xs text-ink-faint">
            © {new Date().getFullYear()} LuminOS. Built for entrepreneurs starting out.
          </p>
        </div>
      </footer>
    </main>
  );
}