import { URLExt } from "@jupyterlab/coreutils";
import { ServerConnection } from "@jupyterlab/services";

export async function requestAPI<T>(
  endpoint: string,
  init: RequestInit = {}
): Promise<T> {
  const settings = ServerConnection.makeSettings();
  const url = URLExt.join(settings.baseUrl, "nbpipe", endpoint);

  let response: Response;
  try {
    response = await ServerConnection.makeRequest(url, init, settings);
  } catch (err) {
    throw new ServerConnection.NetworkError(err as TypeError);
  }

  const text = await response.text();
  let data: unknown;
  try {
    data = JSON.parse(text);
  } catch {
    data = text;
  }

  if (!response.ok) {
    const message =
      typeof data === "object" && data !== null && "message" in data
        ? String((data as Record<string, unknown>).message)
        : text;
    throw new ServerConnection.ResponseError(response, message);
  }

  return data as T;
}
