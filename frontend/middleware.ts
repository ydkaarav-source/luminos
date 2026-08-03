import { NextRequest, NextResponse } from "next/server";

// UX-layer guard only. The backend re-validates the JWT on every request
// (see auth_dependencies.get_current_user) - that is the real boundary.
const PROTECTED_PREFIXES = ["/dashboard", "/business-builder", "/ceo-briefing", "/health-score", "/solopreneur-hub", "/assistant", "/settings"];
const AUTH_PREFIXES = ["/login", "/signup"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasSession = Boolean(request.cookies.get("access_token")?.value);

  const isProtected = PROTECTED_PREFIXES.some((p) => pathname.startsWith(p));
  const isAuthPage = AUTH_PREFIXES.some((p) => pathname.startsWith(p));

  if (isProtected && !hasSession) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (isAuthPage && hasSession) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/business-builder/:path*",
    "/ceo-briefing/:path*",
    "/health-score/:path*",
    "/solopreneur-hub/:path*",
    "/assistant/:path*",
    "/settings/:path*",
    "/login",
    "/signup",
  ],
};
