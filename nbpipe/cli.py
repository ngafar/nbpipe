import argparse
import glob as _glob
import sys
from pathlib import Path

from .runner import execute_notebook
from .workflow import load_workflow


def _run(args: argparse.Namespace) -> None:
    yaml_path = Path(args.workflow).resolve()
    workflow = load_workflow(yaml_path, base_dir=yaml_path.parent.parent)
    total = len(workflow.steps)
    print(f"Workflow: {workflow.name}")

    for i, step in enumerate(workflow.steps, 1):
        print(f"  [{i}/{total}] {step.notebook.name}", end="", flush=True)

        try:
            execute_notebook(step.notebook, timeout=step.timeout)
        except Exception as exc:
            print(f"  FAILED\n{exc}", file=sys.stderr)
            sys.exit(1)

        if step.output_pattern:
            if not _glob.glob(step.output_pattern):
                print(
                    f"  FAILED\nNo output matched pattern: {step.output_pattern}",
                    file=sys.stderr,
                )
                sys.exit(1)
        elif step.output and not step.output.exists():
            print(
                f"  FAILED\nExpected output not found: {step.output}", file=sys.stderr
            )
            sys.exit(1)

        print(" done")

    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="nbpipe", description="Run notebook workflows"
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    run_p = sub.add_parser("run", help="Execute a workflow YAML")
    run_p.add_argument("workflow", help="Path to workflow YAML file")

    args = parser.parse_args()

    if args.command == "run":
        _run(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
