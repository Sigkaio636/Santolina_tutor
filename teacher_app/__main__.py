"""Command line of the teacher app: `python -m teacher_app --help`."""

from pathlib import Path
import webbrowser

import typer

from . import config, db
from .services import packs

app = typer.Typer(help="Santolina teacher app", no_args_is_help=True, add_completion=False)


@app.command()
def serve(open_browser: bool = typer.Option(True, help="Open the app in the browser")):
    """Start the app on http://127.0.0.1:8010 (localhost only)."""
    import uvicorn

    from .web.main import create_app

    settings = config.load()
    url = f"http://127.0.0.1:{settings.port}"
    typer.echo(f"Teacher app: {url}  (data in {settings.home})")
    if settings.fake_boards:
        typer.echo(f"Simulated boards from {settings.fake_boards}")
    if open_browser:
        webbrowser.open(url)
    uvicorn.run(create_app(settings), host="127.0.0.1", port=settings.port, log_level="warning")


@app.command("fake-boards")
def fake_boards(
    folder: Path = typer.Option(..., "--dir", help="Where to create the simulated boards"),
    n: int = typer.Option(3, help="How many"),
    start: int = typer.Option(1, help="Number of the first one"),
):
    """Create simulated boards. Start the app with SANTOLINA_FAKE_BOARDS=<dir> to see them."""
    from .simulate import create_fake_boards

    for board in create_fake_boards(folder, n, start):
        typer.echo(board)


@app.command()
def simulate(
    folder: Path = typer.Option(..., "--dir", help="The simulated boards folder"),
    serial: str = typer.Argument(..., help="e.g. FAKE0001"),
    sessions: int = typer.Option(10),
    open_sessions: int = typer.Option(1, help="Sessions left unfinished"),
    unknown_rate: float = typer.Option(0.1, help="Share of sessions with an unknown code"),
):
    """Write synthetic student sessions on a simulated board that was set up."""
    from .simulate import simulate_sessions

    n = simulate_sessions(folder / serial / "santolina", sessions, unknown_rate, open_sessions)
    typer.echo(f"{n} sessions written on {serial}")


@app.command("demo-pack")
def demo_pack_cmd(
    out: Path = typer.Option(..., help="Folder to write the pack into"),
    n: int = typer.Option(12),
):
    """Write a synthetic arithmetic pack (no M3Kang)."""
    from .simulate import demo_pack

    typer.echo(demo_pack(out, n=n))


@app.command("import-pack")
def import_pack(folder: Path):
    """Add a pack folder to the library."""
    settings = config.load()
    conn = db.connect(settings.db_path)
    m = packs.import_pack(conn, folder, settings.packs_dir)
    typer.echo(f"Imported {m.pack_id} v{m.version} ({m.count} exercises)")


@app.command("m3kang-pack")
def m3kang_pack(
    source: Path = typer.Option(..., help="A prepared M3Kang JSONL file, e.g. data/val.jsonl"),
    pack_id: str = typer.Option(...),
    title: str = typer.Option(...),
    languages: str = typer.Option("", help="e.g. eng,cat"),
    levels: str = typer.Option("", help="e.g. 0,1"),
    limit: int = typer.Option(0),
    images: Path = typer.Option(None, help="data/images, to include problem images"),
    add: bool = typer.Option(True, help="Also import it into the library"),
):
    """Build a pack from M3Kang (research use only). It is written outside the repo."""
    from .m3kang import convert

    settings = config.load()
    out = settings.home / "m3kang-packs"
    folder = convert(
        source,
        out,
        pack_id,
        title,
        languages=set(filter(None, languages.split(","))) or None,
        levels={int(x) for x in levels.split(",") if x} or None,
        limit=limit or None,
        images=images,
    )
    typer.echo(f"Pack written to {folder}")
    if add:
        import_pack(folder)


if __name__ == "__main__":
    app()
