import type { ApiEnvelope, ApiErrorEnvelope } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  code: string;
  details: Record<string, unknown>;
  status: number;

  constructor(status: number, code: string, message: string, details: Record<string, unknown>) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
}

/**
 * Thin fetch wrapper: sends the auth cookie automatically, unwraps the
 * `{ data, meta }` envelope, and throws a typed ApiError on the `{ error }`
 * envelope so callers never have to special-case error shapes.
 */
async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: options.method ?? "GET",
    headers: { "Content-Type": "application/json" },
    credentials: "include", // send the httpOnly auth cookie
    body: options.body ? JSON.stringify(options.body) : undefined,
    cache: "no-store",
  });

  const json = await response.json().catch(() => null);

  if (!response.ok) {
    const errJson = json as ApiErrorEnvelope | null;
    throw new ApiError(
      response.status,
      errJson?.error?.code ?? "UNKNOWN_ERROR",
      errJson?.error?.message ?? "Something went wrong. Please try again.",
      errJson?.error?.details ?? {}
    );
  }

  return (json as ApiEnvelope<T>).data;
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: unknown) => request<T>(path, { method: "POST", body }),
  put: <T>(path: string, body?: unknown) => request<T>(path, { method: "PUT", body }),
  patch: <T>(path: string, body?: unknown) => request<T>(path, { method: "PATCH", body }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
