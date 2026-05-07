import React, { useEffect, useState } from "react";
import { requestAPI } from "./handler";

interface Workflow {
  name: string;
}

type Status = "idle" | "running" | "success" | "error";

interface WorkflowState {
  status: Status;
  message: string;
}

export function WorkflowPanel(): JSX.Element {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [states, setStates] = useState<Record<string, WorkflowState>>({});
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  async function fetchWorkflows() {
    setLoadError(null);
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
      await requestAPI(`workflows/${encodeURIComponent(name)}/run`, {
        method: "POST",
      });
      setStates((prev) => ({
        ...prev,
        [name]: { status: "success", message: "Done" },
      }));
    } catch (err) {
      setStates((prev) => ({
        ...prev,
        [name]: { status: "error", message: String(err) },
      }));
    }
  }

  const anyRunning = Object.values(states).some((s) => s.status === "running");

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
          const isRunning = state?.status === "running";
          return (
            <li key={wf.name} className="nbpipe-item">
              <span className="nbpipe-name">{wf.name}</span>
              {state?.status === "success" && (
                <span className="nbpipe-status nbpipe-success">✓</span>
              )}
              {state?.status === "error" && (
                <span className="nbpipe-status nbpipe-error" title={state.message}>
                  ✕
                </span>
              )}
              <button
                className="nbpipe-run-btn"
                onClick={() => runWorkflow(wf.name)}
                disabled={anyRunning}
              >
                {isRunning ? "Running…" : "Run"}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
