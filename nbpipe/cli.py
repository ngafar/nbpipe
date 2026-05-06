import argparse
import sys

from .runner import execute_notebook
from .workflow import load_workflow


def _run(args: argparse.Namespace) -> None:
    workflow = load_workflow(args.workflow)
    total = len(workflow.steps)
    print(f"Workflow: {workflow.name}  ({total} step{'s' if total != 1 else ''})")

    for i, step in enumerate(workflow.steps, 1):
        print(f"  [{i}/{total}] {step.notebook.name}", end="", flush=True)
        try:
            execute_notebook(step.notebook)
        except Exception as exc:
            print(f"  FAILED\n{exc}", file=sys.stderr)
            sys.exit(1)

        if step.output and not step.output.exists():
            print(f"  FAILED\nExpected output not found: {step.output}", file=sys.stderr)
            sys.exit(1)

        print(" done")

    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(prog="nbpipe", description="Run notebook workflows")
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
