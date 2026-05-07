const makeRequestMock = jest.fn();

class NetworkError extends Error {
  constructor(err: TypeError) {
    super(err.message);
    this.name = "NetworkError";
  }
}

class ResponseError extends Error {
  response: Response;
  constructor(response: Response, message?: string) {
    super(message ?? "ResponseError");
    this.name = "ResponseError";
    this.response = response;
  }
}

jest.mock("@jupyterlab/services", () => ({
  ServerConnection: {
    makeRequest: (...args: unknown[]) => makeRequestMock(...args),
    makeSettings: () => ({ baseUrl: "http://localhost:8888/" }),
    NetworkError,
    ResponseError,
  },
}));

jest.mock("@jupyterlab/coreutils", () => ({
  URLExt: {
    join: (...parts: string[]) =>
      parts
        .join("/")
        .replace(/([^:])\/+/g, "$1/")
        .replace(/\/$/, ""),
  },
}));

import { requestAPI } from "../handler";

function makeResponse(ok: boolean, body: unknown): Response {
  const text =
    typeof body === "string" ? body : JSON.stringify(body);
  return {
    ok,
    text: async () => text,
  } as unknown as Response;
}

describe("requestAPI", () => {
  beforeEach(() => {
    makeRequestMock.mockReset();
  });

  it("calls the correct URL", async () => {
    makeRequestMock.mockResolvedValue(makeResponse(true, []));
    await requestAPI("workflows");
    const calledUrl = makeRequestMock.mock.calls[0][0] as string;
    expect(calledUrl).toContain("nbpipe");
    expect(calledUrl).toContain("workflows");
  });

  it("returns parsed JSON on success", async () => {
    const payload = [{ name: "my_pipeline" }];
    makeRequestMock.mockResolvedValue(makeResponse(true, payload));
    const result = await requestAPI("workflows");
    expect(result).toEqual(payload);
  });

  it("throws NetworkError when the request throws", async () => {
    makeRequestMock.mockRejectedValue(new TypeError("fetch failed"));
    await expect(requestAPI("workflows")).rejects.toBeInstanceOf(NetworkError);
  });

  it("throws ResponseError when response is not ok", async () => {
    makeRequestMock.mockResolvedValue(
      makeResponse(false, { message: "not found" })
    );
    await expect(requestAPI("workflows")).rejects.toBeInstanceOf(ResponseError);
  });

  it("throws ResponseError with raw text when error body is not JSON", async () => {
    makeRequestMock.mockResolvedValue(makeResponse(false, "<html>Bad Gateway</html>"));
    const err = await requestAPI("workflows").catch((e) => e) as ResponseError;
    expect(err).toBeInstanceOf(ResponseError);
    expect(err.message).toContain("Bad Gateway");
  });

  it("passes init options to makeRequest", async () => {
    makeRequestMock.mockResolvedValue(makeResponse(true, { status: "ok" }));
    await requestAPI("workflows/test/run", { method: "POST" });
    const init = makeRequestMock.mock.calls[0][1] as RequestInit;
    expect(init.method).toBe("POST");
  });
});
