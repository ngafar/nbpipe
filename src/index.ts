import {
  ILabShell,
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from "@jupyterlab/application";
import { ReactWidget } from "@jupyterlab/ui-components";
import React from "react";
import { nbpipeIcon } from "./icon";
import { WorkflowPanel } from "./WorkflowPanel";

class WorkflowWidget extends ReactWidget {
  constructor(private readonly openFile: (path: string) => void) {
    super();
  }

  render(): JSX.Element {
    return React.createElement(WorkflowPanel, { openFile: this.openFile });
  }
}

const plugin: JupyterFrontEndPlugin<void> = {
  id: "nbpipe:plugin",
  description: "Run notebook workflows from the JupyterLab sidebar",
  autoStart: true,
  requires: [ILabShell],
  activate: (app: JupyterFrontEnd, labShell: ILabShell) => {
    const openFile = (path: string) => {
      void app.commands.execute("docmanager:open", { path });
    };
    const widget = new WorkflowWidget(openFile);
    widget.id = "nbpipe-sidebar";
    widget.title.icon = nbpipeIcon;
    widget.title.caption = "nbpipe Workflows";

    labShell.add(widget, "left", { rank: 500 });
  },
};

export default plugin;
