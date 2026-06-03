import { Dialog, showDialog } from "@jupyterlab/apputils";
import React, { useEffect, useState } from "react";
import { requestAPI } from "./handler";

interface Workflow {
  name: string;
  path: string;
}

type Status = "idle" | "running" | "stopping" | "success" | "error";

interface WorkflowState {
  status: Status;
  message: string;
}

interface Props {
  openFile: (path: string) => void;
}

export function WorkflowPanel({ openFile }: Props): JSX.Element {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [states, setStates] = useState<Record<string, WorkflowState>>({});
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  async function fetchWorkflows() {
    setLoadError(null);
    setStates({});
    try {
      const data = await requestAPI<Workflow[]>("workflows");
      setWorkflows(data);
    } catch {
      setLoadError("Could not load workflows from .nbpipe/");
    }
  }

  async function runWorkflow(name: string) {
    setStates((prev) => ({
      ...prev,
      [name]: { status: "running", message: "" },
    }));
    try {
      const result = await requestAPI<{ status: string }>(
        `workflows/${encodeURIComponent(name)}/run`,
        { method: "POST" }
      );
      setStates((prev) => {
        const wasStopped =
          result.status === "stopped" || prev[name]?.status === "stopping";
        return {
          ...prev,
          [name]: wasStopped
            ? { status: "idle", message: "" }
            : { status: "success", message: "Done" },
        };
      });
    } catch (err) {
      setStates((prev) => ({
        ...prev,
        [name]:
          prev[name]?.status === "stopping"
            ? { status: "idle", message: "" }
            : { status: "error", message: String(err) },
      }));
    }
  }

  async function stopWorkflow(name: string) {
    setStates((prev) => ({
      ...prev,
      [name]: { status: "stopping", message: "" },
    }));
    try {
      await requestAPI(`workflows/${encodeURIComponent(name)}/stop`, {
        method: "POST",
      });
    } catch {
      // run promise will settle the state
    }
  }

  function showError(name: string, message: string) {
    void showDialog({
      title: `${name} failed`,
      body: message,
      buttons: [Dialog.okButton()],
    });
  }

  const anyRunning = Object.values(states).some(
    (s) => s.status === "running" || s.status === "stopping"
  );

  return (
    <div className="nbpipe-panel">
      <div className="nbpipe-header">
        <span className="nbpipe-title">nbpipe</span>
        <button
          className="nbpipe-refresh"
          onClick={fetchWorkflows}
          title="Refresh"
        >
          ↻
        </button>
      </div>

      {loadError && <div className="nbpipe-load-error">{loadError}</div>}

      {workflows.length === 0 && !loadError && (
        <div className="nbpipe-empty">No workflows found in .nbpipe/</div>
      )}

      <ul className="nbpipe-list">
        {workflows.map((wf) => {
          const state = states[wf.name];
          const isActive =
            state?.status === "running" || state?.status === "stopping";
          const isStopping = state?.status === "stopping";
          return (
            <li key={wf.name} className="nbpipe-item">
              {state?.status === "success" ? (
                <span className="nbpipe-status nbpipe-success">✓</span>
              ) : state?.status === "error" ? (
                <span
                  className="nbpipe-status nbpipe-error nbpipe-error-btn"
                  onClick={() => showError(wf.name, state.message)}
                  title="Click to see error"
                >
                  ✕
                </span>
              ) : (
                <span
                  className={`nbpipe-status nbpipe-dot${isActive ? " nbpipe-dot--running" : ""}`}
                  aria-label={isActive ? "running" : "idle"}
                />
              )}
              <span className="nbpipe-name">{wf.name}</span>
              <button
                className="nbpipe-open-btn"
                onClick={() => openFile(wf.path)}
                title="Open YAML in editor"
              >
                Open
              </button>
              {isActive ? (
                <button
                  className="nbpipe-stop-btn"
                  onClick={() => stopWorkflow(wf.name)}
                  disabled={isStopping}
                >
                  {isStopping ? "Stopping…" : "Stop"}
                </button>
              ) : (
                <button
                  className="nbpipe-run-btn"
                  onClick={() => runWorkflow(wf.name)}
                  disabled={anyRunning}
                >
                  Run
                </button>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
