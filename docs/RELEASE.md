# Release process

Publishing nbpipe pushes a new version to PyPI and makes it available via `pip install nbpipe`. The GitHub Actions publish workflow handles the build and upload automatically when a GitHub release is created.

## 1. Bump the version

Update the version in both files and keep them in sync:

| File | Why |
|------|-----|
| `pyproject.toml` | Version published to PyPI |
| `package.json` | Version embedded in the JupyterLab extension bundle |

If the two versions diverge, users may see a mismatch in JupyterLab's extension manager.

## 2. Create a GitHub release

1. Go to **Releases** on GitHub and click **Draft a new release**
2. Click **Choose a tag** and type a new tag in the format `v<version>` (e.g. `v0.1.3`) — GitHub will create it on publish
3. Set the target branch to `main`
4. Add a title and release notes
5. Click **Publish release** — do not save as draft

> The publish workflow triggers on the `published` event. Saving as a draft will not deploy to PyPI.

Once published, the workflow builds the package and uploads it to PyPI automatically. You can monitor progress in the **Actions** tab.
