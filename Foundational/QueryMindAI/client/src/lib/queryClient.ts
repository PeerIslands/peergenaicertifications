import { QueryClient, QueryFunction } from "@tanstack/react-query";

/**
 * Throws an error if the HTTP response is not OK (status code >= 400).
 * 
 * @param res - The Response object to check
 * @throws Will throw an error with status code and response text if the response is not OK
 * 
 * @private
 */
async function throwIfResNotOk(res: Response) {
  if (!res.ok) {
    const text = (await res.text()) || res.statusText;
    throw new Error(`${res.status}: ${text}`);
  }
}

/**
 * Makes an HTTP API request with automatic error handling.
 * 
 * @param method - The HTTP method (GET, POST, PUT, DELETE, etc.)
 * @param url - The URL to make the request to
 * @param data - Optional data to send in the request body (will be JSON stringified)
 * @returns A promise that resolves to the Response object if successful
 * @throws Will throw an error if the response is not OK
 * 
 * @remarks
 * Automatically sets Content-Type header to application/json when data is provided.
 * Includes credentials in the request for cookie-based authentication.
 */
export async function apiRequest(
  method: string,
  url: string,
  data?: unknown | undefined,
): Promise<Response> {
  const res = await fetch(url, {
    method,
    headers: data ? { "Content-Type": "application/json" } : {},
    body: data ? JSON.stringify(data) : undefined,
    credentials: "include",
  });

  await throwIfResNotOk(res);
  return res;
}

type UnauthorizedBehavior = "returnNull" | "throw";

/**
 * Creates a React Query query function with configurable 401 (unauthorized) handling.
 * 
 * @param options - Configuration options
 * @param options.on401 - Behavior when a 401 status is encountered: "returnNull" to return null, "throw" to throw an error
 * @returns A QueryFunction that fetches data from the query key URL
 * 
 * @remarks
 * The query key should be an array that will be joined with "/" to form the URL.
 * Includes credentials in the request for cookie-based authentication.
 */
export const getQueryFn: <T>(options: {
  on401: UnauthorizedBehavior;
}) => QueryFunction<T> =
  ({ on401: unauthorizedBehavior }) =>
  async ({ queryKey }) => {
    const res = await fetch(queryKey.join("/") as string, {
      credentials: "include",
    });

    if (unauthorizedBehavior === "returnNull" && res.status === 401) {
      return null;
    }

    await throwIfResNotOk(res);
    return await res.json();
  };

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      queryFn: getQueryFn({ on401: "throw" }),
      refetchInterval: false,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
      retry: false,
    },
    mutations: {
      retry: false,
    },
  },
});
