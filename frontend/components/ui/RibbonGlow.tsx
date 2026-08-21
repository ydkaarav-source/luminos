const POSITIONS = {
  "top-right": "right-[-10%] top-0",
  "bottom-right": "right-[-10%] bottom-0",
  "top-left": "left-[-10%] top-0 -scale-x-100",
  "bottom-left": "left-[-10%] bottom-0 -scale-x-100",
};

/**
 * The same layered ribbon/curve SVG from the landing page hero
 * (frontend/app/page.tsx), extracted so the app shell can reuse it at a
 * smaller scale instead of duplicating the paths/gradients per page.
 */
export function RibbonGlow({
  position = "top-right",
  width = "28%",
  className = "",
}: {
  position?: keyof typeof POSITIONS;
  width?: string;
  className?: string;
}) {
  return (
    <svg
      aria-hidden
      className={`pointer-events-none absolute hidden h-full max-w-[420px] md:block ${POSITIONS[position]} ${className}`}
      style={{ width }}
      viewBox="0 0 500 700"
      fill="none"
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        <linearGradient id="ribbonGlow1" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0A5C29" />
          <stop offset="55%" stopColor="#16A34A" />
          <stop offset="100%" stopColor="#4ADE80" />
        </linearGradient>
        <linearGradient id="ribbonGlow2" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0A5C29" />
          <stop offset="60%" stopColor="#16A34A" />
          <stop offset="100%" stopColor="#86EFAC" />
        </linearGradient>
        <linearGradient id="ribbonGlow3" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#16A34A" />
          <stop offset="100%" stopColor="#4ADE80" />
        </linearGradient>
      </defs>
      <path
        d="M470 -20C380 90 560 210 430 320C300 430 460 560 380 720"
        stroke="url(#ribbonGlow1)"
        strokeWidth="10"
        strokeLinecap="round"
        opacity="0.5"
      />
      <path
        d="M380 -20C300 100 470 230 350 340C230 450 380 580 300 720"
        stroke="url(#ribbonGlow2)"
        strokeWidth="16"
        strokeLinecap="round"
        opacity="0.4"
      />
      <path
        d="M300 -20C230 110 380 240 270 350C160 460 300 580 230 720"
        stroke="url(#ribbonGlow3)"
        strokeWidth="5"
        strokeLinecap="round"
        opacity="0.5"
      />
    </svg>
  );
}
