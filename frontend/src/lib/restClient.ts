type RestUser = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
};

type RestLoginResponse = {
  token: string;
  user: RestUser;
  reactivated: boolean;
};

type RestDeleteResponse = {
  deleted: boolean;
};

type RestCursorPage<T> = {
  items: T[];
  page: {
    next_cursor: string | null;
    limit: number;
    has_next: boolean;
  };
};

export const AUTH_STATE_CHANGED_EVENT = "auth-state-changed";

const graphQLEndpoint =
  process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT ?? "http://localhost:8000/graphql";
const restBase = graphQLEndpoint.endsWith("/graphql")
  ? graphQLEndpoint.slice(0, -"/graphql".length)
  : graphQLEndpoint;
const restEndpoint = `${restBase}/api`;

function isAuthPath(path: string): boolean {
  return path === "/auth" || path.startsWith("/auth/");
}

function isProtectedPath(path: string): boolean {
  return !isAuthPath(path);
}

export function clearStoredAuth(): void {
  localStorage.removeItem("token");
  localStorage.removeItem("userId");
  window.dispatchEvent(new Event(AUTH_STATE_CHANGED_EVENT));
}

async function restRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const token = localStorage.getItem("token");
  if (token && !isAuthPath(path)) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${restEndpoint}${path}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const hasJson = contentType.includes("application/json");
  const payload = hasJson ? await response.json() : null;

  if (!response.ok) {
    if (response.status === 401 && isProtectedPath(path)) {
      clearStoredAuth();
      throw new Error("Session expired. Please log in again.");
    }

    const detail =
      payload && typeof payload === "object" && "detail" in payload
        ? (payload as { detail?: unknown }).detail
        : null;
    const message = typeof detail === "string" ? detail : "Request failed.";
    throw new Error(message);
  }

  return payload as T;
}

export async function restLogin(input: {
  email: string;
  password: string;
}): Promise<RestLoginResponse> {
  return restRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function restRegister(input: {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}): Promise<RestLoginResponse> {
  return restRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify({
      email: input.email,
      password: input.password,
      first_name: input.firstName,
      last_name: input.lastName,
    }),
  });
}

export async function restGetMe(): Promise<RestUser> {
  return restRequest("/users/me");
}

export async function restUpdateMe(input: {
  email: string;
  firstName: string;
  lastName: string;
  password?: string;
}): Promise<RestUser> {
  return restRequest("/users/me", {
    method: "PATCH",
    body: JSON.stringify({
      email: input.email,
      first_name: input.firstName,
      last_name: input.lastName,
      ...(input.password ? { password: input.password } : {}),
    }),
  });
}

export async function restSoftDeleteMe(): Promise<RestDeleteResponse> {
  return restRequest("/users/me", {
    method: "DELETE",
  });
}

export async function restGetUserById(userId: string): Promise<RestUser> {
  return restRequest(`/users/${encodeURIComponent(userId)}`);
}

export async function restGetUsersPage(params: {
  limit?: number;
  cursor?: string | null;
}): Promise<RestCursorPage<RestUser>> {
  const searchParams = new URLSearchParams();
  if (params.limit) {
    searchParams.set("limit", String(params.limit));
  }
  if (params.cursor) {
    searchParams.set("cursor", params.cursor);
  }
  const suffix = searchParams.toString();
  return restRequest(`/users${suffix ? `?${suffix}` : ""}`);
}
