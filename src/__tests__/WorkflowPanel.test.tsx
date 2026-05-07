import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";

const requestAPIMock = jest.fn();
jest.mock("../handler", () => ({
  requestAPI: (...args: unknown[]) => requestAPIMock(...args),
}));

const showDialogMock = jest.fn().mockResolvedValue({ button: { accept: true } });
jest.mock("@jupyterlab/apputils", () => ({
  showDialog: (...args: unknown[]) => showDialogMock(...args),
  Dialog: { okButton: () => ({ label: "OK" }) },
}));

import { WorkflowPanel } from "../WorkflowPanel";

describe("WorkflowPanel", () => {
  beforeEach(() => {
    requestAPIMock.mockReset();
    showDialogMock.mockClear();
  });

  it("shows empty state when no workflows are returned", async () => {
    requestAPIMock.mockResolvedValue([]);
    render(<WorkflowPanel />);
    await waitFor(() =>
      expect(
        screen.getByText("No workflows found in .nbpipe/")
      ).toBeInTheDocument()
    );
  });

  it("renders workflow names", async () => {
    requestAPIMock.mockResolvedValue([{ name: "daily" }, { name: "weekly" }]);
    render(<WorkflowPanel />);
    await waitFor(() => {
      expect(screen.getByText("daily")).toBeInTheDocument();
      expect(screen.getByText("weekly")).toBeInTheDocument();
    });
  });

  it("shows load error when fetch fails", async () => {
    requestAPIMock.mockRejectedValue(new Error("network error"));
    render(<WorkflowPanel />);
    await waitFor(() =>
      expect(
        screen.getByText("Could not load workflows from .nbpipe/")
      ).toBeInTheDocument()
    );
  });

  it("shows Running label while workflow is executing", async () => {
    requestAPIMock
      .mockResolvedValueOnce([{ name: "my_pipeline" }])
      .mockReturnValueOnce(new Promise(() => {})); // never resolves
    render(<WorkflowPanel />);
    await waitFor(() =>
      expect(screen.getByText("my_pipeline")).toBeInTheDocument()
    );
    fireEvent.click(screen.getByRole("button", { name: "Run" }));
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Running…" })).toBeDisabled()
    );
  });

  it("shows success indicator after workflow completes", async () => {
    requestAPIMock
      .mockResolvedValueOnce([{ name: "my_pipeline" }])
      .mockResolvedValueOnce({ status: "ok" });
    render(<WorkflowPanel />);
    await waitFor(() =>
      expect(screen.getByText("my_pipeline")).toBeInTheDocument()
    );
    fireEvent.click(screen.getByRole("button", { name: "Run" }));
    await waitFor(() => expect(screen.getByText("✓")).toBeInTheDocument());
  });

  it("shows error indicator when workflow fails", async () => {
    requestAPIMock
      .mockResolvedValueOnce([{ name: "my_pipeline" }])
      .mockRejectedValueOnce(new Error("cell error"));
    render(<WorkflowPanel />);
    await waitFor(() =>
      expect(screen.getByText("my_pipeline")).toBeInTheDocument()
    );
    fireEvent.click(screen.getByRole("button", { name: "Run" }));
    await waitFor(() => expect(screen.getByText("✕")).toBeInTheDocument());
  });

  it("clicking the error indicator opens a dialog with the error message", async () => {
    requestAPIMock
      .mockResolvedValueOnce([{ name: "my_pipeline" }])
      .mockRejectedValueOnce(new Error("cell error"));
    render(<WorkflowPanel />);
    await waitFor(() =>
      expect(screen.getByText("my_pipeline")).toBeInTheDocument()
    );
    fireEvent.click(screen.getByRole("button", { name: "Run" }));
    await waitFor(() => expect(screen.getByText("✕")).toBeInTheDocument());

    fireEvent.click(screen.getByText("✕"));
    expect(showDialogMock).toHaveBeenCalledWith(
      expect.objectContaining({
        title: "my_pipeline failed",
        body: expect.stringContaining("cell error"),
      })
    );
  });

  it("refresh button re-fetches workflows", async () => {
    requestAPIMock.mockResolvedValue([{ name: "pipeline_a" }]);
    render(<WorkflowPanel />);
    await waitFor(() =>
      expect(screen.getByText("pipeline_a")).toBeInTheDocument()
    );
    fireEvent.click(screen.getByTitle("Refresh"));
    await waitFor(() => expect(requestAPIMock).toHaveBeenCalledTimes(2));
  });
});
