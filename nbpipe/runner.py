from pathlib import Path

import nbformat
from jupyter_client import KernelManager


def _collect_outputs(kc, execution_count: int) -> tuple[list, bool]:
    """Drain iopub messages for one execute request; return (outputs, had_error)."""
    import queue

    outputs = []
    had_error = False

    while True:
        try:
            msg = kc.get_iopub_msg(timeout=60)
        except queue.Empty:
            break

        msg_type = msg["msg_type"]
        content = msg["content"]

        if msg_type == "status" and content["execution_state"] == "idle":
            break
        elif msg_type == "stream":
            outputs.append(
                nbformat.v4.new_output(
                    output_type="stream",
                    name=content["name"],
                    text=content["text"],
                )
            )
        elif msg_type == "execute_result":
            outputs.append(
                nbformat.v4.new_output(
                    output_type="execute_result",
                    data=content["data"],
                    metadata=content.get("metadata", {}),
                    execution_count=execution_count,
                )
            )
        elif msg_type == "display_data":
            outputs.append(
                nbformat.v4.new_output(
                    output_type="display_data",
                    data=content["data"],
                    metadata=content.get("metadata", {}),
                )
            )
        elif msg_type == "error":
            outputs.append(
                nbformat.v4.new_output(
                    output_type="error",
                    ename=content["ename"],
                    evalue=content["evalue"],
                    traceback=content["traceback"],
                )
            )
            had_error = True

    return outputs, had_error


def execute_notebook(nb_path: Path) -> None:
    nb = nbformat.read(str(nb_path), as_version=4)

    km = KernelManager()
    km.start_kernel()
    kc = km.client()
    kc.start_channels()
    kc.wait_for_ready(timeout=60)

    execution_count = 0
    try:
        for cell in nb.cells:
            if cell.cell_type != "code":
                continue
            if not cell.source.strip():
                cell.outputs = []
                cell.execution_count = None
                continue

            execution_count += 1
            kc.execute(cell.source)
            outputs, had_error = _collect_outputs(kc, execution_count)
            cell.outputs = outputs
            cell.execution_count = execution_count

            if had_error:
                raise RuntimeError(
                    f"Cell {execution_count} raised an error in {nb_path.name}"
                )
    finally:
        kc.stop_channels()
        km.shutdown_kernel(now=True)

    nbformat.write(nb, str(nb_path))
