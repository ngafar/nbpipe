import { LabIcon } from "@jupyterlab/ui-components";

export const nbpipeIcon = new LabIcon({
  name: "nbpipe:icon",
  svgstr: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <!-- pipe sections -->
    <rect x="1"  y="9" width="5" height="6" rx="1"/>
    <rect x="9"  y="9" width="5" height="6" rx="1"/>
    <rect x="17" y="9" width="5" height="6" rx="1"/>
    <!-- arrows between sections -->
    <path d="M6 12h3"/>
    <path d="M8 10.5 L9.5 12 L8 13.5"/>
    <path d="M14 12h3"/>
    <path d="M16 10.5 L17.5 12 L16 13.5"/>
  </svg>`,
});
