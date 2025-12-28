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

const graphQLEndpoint =
  process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT ?? "http://localhost:8000/graphql";
const restBase = graphQLEndpoint.endsWith("/graphql")
  ? graphQLEndpoint.slice(0, -"/graphql".length)
  : graphQLEndpoint;
const restEndpoint = `${restBase}/api`;

async function restRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const token = localStorage.getItem("token");
  if (token) {
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
