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

  const data = await response.json();

  if (!response.ok) {
    throw new ServerConnection.ResponseError(response, data?.message ?? data);
  }

  return data as T;
}
