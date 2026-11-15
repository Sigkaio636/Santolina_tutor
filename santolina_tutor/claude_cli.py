"""Call Claude headless through `claude -p`, on the user's subscription, with JSON-schema output."""
import json
import subprocess
import tempfile


def claude_json(prompt, system, schema, model, timeout=600, read_dir=None):
    """Return the structured output of one `claude -p` call, validated against schema.

    read_dir lets Claude use the Read tool inside that folder (for images);
    without it, Claude gets no tools at all.
    """
    tools = ["--tools", "Read", "--allowedTools", "Read", "--add-dir", read_dir] if read_dir \
        else ["--tools", ""]
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "json",
           "--json-schema", json.dumps(schema), "--system-prompt", system, *tools,
           "--setting-sources", "", "--strict-mcp-config", "--no-session-persistence",
           "--disable-slash-commands", "--permission-mode", "dontAsk"]
    # An empty working directory: no project CLAUDE.md, hooks or settings get loaded.
    with tempfile.TemporaryDirectory() as cwd:
        run = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                             check=False)
    if run.returncode != 0:
        raise RuntimeError(run.stderr.strip()[-300:] or f"exit {run.returncode}")
    reply = json.loads(run.stdout)
    if reply.get("is_error") or "structured_output" not in reply:
        raise RuntimeError(f"no structured output: {str(reply.get('result'))[:300]}")
    return reply["structured_output"], reply.get("duration_ms", 0)
