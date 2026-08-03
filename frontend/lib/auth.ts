import { cookies } from "next/headers";

/**
 * Server-side check for whether an access-token cookie is present.
 *
 * This is a UX-layer check only - it lets the middleware/layout decide
 * whether to redirect to /login without a network round trip. The real
 * security boundary is always the backend re-validating the JWT on
 * every request (see auth_dependencies.py get_current_user).
 */
export function hasSessionCookie(): boolean {
  return Boolean(cookies().get("access_token")?.value);
}
