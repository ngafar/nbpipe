import {
  ILabShell,
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from "@jupyterlab/application";
import { ReactWidget } from "@jupyterlab/ui-components";
import React from "react";
import { WorkflowPanel } from "./WorkflowPanel";

class WorkflowWidget extends ReactWidget {
  render(): JSX.Element {
    return React.createElement(WorkflowPanel);
  }
}

const plugin: JupyterFrontEndPlugin<void> = {
  id: "nbpipe:plugin",
  description: "Run notebook workflows from the JupyterLab sidebar",
  autoStart: true,
  requires: [ILabShell],
  activate: (_app: JupyterFrontEnd, labShell: ILabShell) => {
    const widget = new WorkflowWidget();
    widget.id = "nbpipe-sidebar";
    widget.title.caption = "nbpipe Workflows";
    widget.title.className = "nbpipe-sidebar-icon";

    labShell.add(widget, "left", { rank: 500 });
  },
};

export default plugin;
