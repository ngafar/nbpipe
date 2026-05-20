# Development guide

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Node.js 20+

## Setup

Install Python and JS dependencies:

```bash
uv sync --all-groups
uv run jlpm install --immutable
```

Build the JupyterLab extension:

```bash
uv run jlpm build
```

## Running JupyterLab

```bash
uv run jupyter lab
```

The nbpipe sidebar panel will appear on the left.

## Testing

Python tests:

```bash
uv run pytest
```

JS tests:

```bash
uv run jlpm test
```

## Linting and formatting

```bash
uv run ruff check        # lint
uv run ruff format       # format
uv run ruff format --check  # check formatting without writing
```

## Rebuilding after changes

TypeScript changes require a rebuild before they appear in JupyterLab:

```bash
uv run jlpm build
```

Or run in watch mode to rebuild automatically:

```bash
uv run jlpm watch
```
