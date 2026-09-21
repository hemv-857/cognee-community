# cognee-community-connector-google-drive

A Google Drive data-source connector for [cognee](https://github.com/topoteretes/cognee):
sync a Drive folder (Docs, Sheets, PDFs, plain text) into memory — incrementally, with
forget-on-delete.

It exposes a `dlt` source you hand to `cognee.remember(...)`, reusing cognee's existing DLT
ingestion path. Files are ingested as **documents** (routed through normal chunking + LLM graph
extraction) via cognee's self-describing content-column mechanism.

## Requirements

Requires a Cognee build with
`cognee.tasks.ingestion.dlt_utils.DOCUMENT_SYNC_VERSION >= 1`. This guarantees
table-scoped document cleanup and deletion of the final document in a source.
The factory refuses older builds rather than risking cross-folder data loss.
Until that core change is released, install the matching core checkout alongside
this package; update the release dependency pin before publishing.

## Install

```bash
uv pip install cognee-community-connector-google-drive
# or, from this monorepo:
cd packages/connector/google-drive && uv sync --all-extras
```

## Usage

```python
import cognee
from cognee_community_connector_google_drive import google_drive_source

await cognee.remember(
    google_drive_source(folder_id="<folder id from the Drive URL>"),
    dataset_name="my_drive_folder",
    primary_key="id",
    write_disposition="merge",  # incremental upsert by file id
    max_rows_per_table=0,  # folders often exceed the default 50-row cap
)

answer = await cognee.search(
    query_text="Summarize the design docs in the shared folder.",
    query_type=cognee.SearchType.GRAPH_COMPLETION,
    datasets=["my_drive_folder"],
)
```

See `examples/example.py` for the full flow.

## How sync + forget-on-delete work

Incremental sync uses the Drive Changes API page token (persisted in dlt's per-resource state):
the first run captures a start token + does a full folder listing; later runs emit only
added/changed files plus hard-delete tombstones for removed/trashed files. Deletes are emitted
with the `_deleted` hard-delete marker; dlt drops them on `merge` and cognee's `orphan_cleanup`
purges them from the graph, vector, and relational stores. Google Docs/Sheets export to
text/CSV, PDFs are parsed with cognee's core `pypdf`, and plain text/markdown/CSV download as-is;
an unparseable file is skipped with a warning.

When syncing multiple folders into one dataset, assign each a stable, distinct
`resource_name`. It isolates both the Changes API cursor and cleanup scope.
Previously ingested documents without a table provenance stamp are retained
conservatively; explicitly clear and re-sync the dataset to rebuild legacy data.

## Setup

1. Enable the Drive API in Google Cloud and create either a **service account** key
   (default, non-interactive) or an **OAuth 2.0 Client ID** (Desktop app). Share the target
   folder with the service account, or authorize the OAuth flow.
2. Point `credentials_path` at the JSON (scope is read-only `drive.readonly`), plus your
   `LLM_API_KEY` like any other cognee run.

## Testing

```bash
uv run pytest tests/
```

The unit tests mock the Drive API (no live credentials). They require a cognee build that
includes document-mode (see **Requirements**).
