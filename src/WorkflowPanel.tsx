import { Dialog, showDialog } from "@jupyterlab/apputils";
import React, { useEffect, useState } from "react";
import { requestAPI } from "./handler";

interface Workflow {
  name: string;
  path: string;
}

type Status = "idle" | "running" | "success" | "error";

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
  const [stopping, setStopping] = useState<Set<string>>(new Set());
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
      if (result.status === "stopped") {
        setStates((prev) => ({
          ...prev,
          [name]: { status: "idle", message: "" },
        }));
      } else {
        setStates((prev) => ({
          ...prev,
          [name]: { status: "success", message: "Done" },
        }));
      }
    } catch (err) {
      setStates((prev) => ({
        ...prev,
        [name]: { status: "error", message: String(err) },
      }));
    } finally {
      setStopping((prev) => {
        const next = new Set(prev);
        next.delete(name);
        return next;
      });
    }
  }

  async function stopWorkflow(name: string) {
    setStopping((prev) => new Set([...prev, name]));
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
          const isStopping = stopping.has(wf.name);
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
                  className={`nbpipe-status nbpipe-dot${isRunning ? " nbpipe-dot--running" : ""}`}
                  aria-label={isRunning ? "running" : "idle"}
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
              {isRunning ? (
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
