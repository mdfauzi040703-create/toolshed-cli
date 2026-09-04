"""Perintah `toolshed git ...` — mempercepat alur kerja git harian."""

import subprocess

import click
from rich.console import Console
from rich.table import Table

console = Console()


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise click.ClickException(result.stderr.strip() or f"Perintah gagal: {' '.join(cmd)}")
    return result.stdout.strip()


@click.group()
def git():
    """Perintah bantu seputar git (status ringkas, commit cepat, bersih-bersih branch)."""
    pass


@git.command("summary")
def summary():
    """Tampilkan ringkasan status repo: branch, perubahan, dan commit terakhir."""
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    status = _run(["git", "status", "--porcelain"])
    last_commit = _run(["git", "log", "-1", "--pretty=format:%h %s (%cr)"])

    changed = [line for line in status.splitlines() if line.strip()]

    table = Table(title=f"Ringkasan repo — branch: {branch}")
    table.add_column("Info")
    table.add_column("Detail")
    table.add_row("Commit terakhir", last_commit or "-")
    table.add_row("File berubah", str(len(changed)))
    console.print(table)

    if changed:
        for line in changed:
            console.print(f"  {line}")


@git.command("quick-commit")
@click.argument("message")
@click.option("--push", is_flag=True, help="Langsung push setelah commit.")
def quick_commit(message: str, push: bool):
    """Add semua perubahan lalu commit dengan MESSAGE."""
    _run(["git", "add", "-A"])
    _run(["git", "commit", "-m", message])
    console.print(f"[green]Committed:[/green] {message}")
    if push:
        branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        _run(["git", "push", "origin", branch])
        console.print(f"[green]Pushed ke origin/{branch}[/green]")


@git.command("clean-branches")
@click.option("--dry-run", is_flag=True, default=True, help="Hanya tampilkan, tidak menghapus (default).")
@click.option("--apply", "apply_", is_flag=True, help="Benar-benar hapus branch lokal yang sudah merged.")
def clean_branches(dry_run: bool, apply_: bool):
    """Cari dan hapus branch lokal yang sudah ter-merge ke main/master."""
    default_branch = "main"
    try:
        _run(["git", "rev-parse", "--verify", "main"])
    except click.ClickException:
        default_branch = "master"

    merged = _run(["git", "branch", "--merged", default_branch]).splitlines()
    candidates = [
        b.strip().lstrip("* ").strip()
        for b in merged
        if b.strip().lstrip("* ").strip() not in (default_branch, "")
    ]

    if not candidates:
        console.print("Tidak ada branch merged yang bisa dibersihkan.")
        return

    for b in candidates:
        console.print(f"  {b}")

    if apply_:
        for b in candidates:
            _run(["git", "branch", "-d", b])
        console.print(f"[green]{len(candidates)} branch dihapus.[/green]")
    else:
        console.print("\n[yellow]Dry-run.[/yellow] Jalankan dengan --apply untuk benar-benar menghapus.")


@git.command("undo")
@click.option(
    "--hard",
    is_flag=True,
    help="Buang juga perubahan di working directory (default: perubahan tetap dipertahankan, staged).",
)
def undo(hard: bool):
    """Batalkan commit terakhir. Secara default perubahan tetap ada (unstaged/staged), tidak hilang."""
    last_commit = _run(["git", "log", "-1", "--pretty=format:%h %s"])
    if not last_commit:
        console.print("Tidak ada commit untuk dibatalkan.")
        return

    mode = "--hard" if hard else "--soft"
    _run(["git", "reset", mode, "HEAD~1"])

    if hard:
        console.print(f"[green]Commit dibatalkan (hard):[/green] {last_commit}")
        console.print("[yellow]Perubahan di commit itu ikut terhapus dari working directory.[/yellow]")
    else:
        console.print(f"[green]Commit dibatalkan:[/green] {last_commit}")
        console.print("Perubahan tetap ada dan sudah staged, siap di-commit ulang kalau perlu.")


@git.command("stash-list")
def stash_list():
    """Tampilkan semua git stash dalam bentuk tabel ringkas."""
    raw = _run(["git", "stash", "list"])
    if not raw:
        console.print("Tidak ada stash tersimpan.")
        return

    table = Table(title="Daftar stash")
    table.add_column("Index", justify="right")
    table.add_column("Branch")
    table.add_column("Pesan")

    for line in raw.splitlines():
        # Format asli: stash@{0}: On branch-name: pesan
        idx, _, rest = line.partition(":")
        rest = rest.strip()
        if rest.lower().startswith("on ") or rest.lower().startswith("wip on "):
            branch_part, _, msg = rest.partition(":")
            branch = branch_part.split(" ", 1)[-1].strip()
            msg = msg.strip()
        else:
            branch = "-"
            msg = rest
        table.add_row(idx.strip(), branch, msg or "-")

    console.print(table)
