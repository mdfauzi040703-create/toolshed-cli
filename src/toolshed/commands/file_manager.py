"""Perintah `toolshed files ...` — utilitas ringkas untuk kelola file lokal."""

import os
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

console = Console()

JUNK_PATTERNS = (
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".DS_Store",
    "*.pyc",
    ".mypy_cache",
    "dist",
    "build",
)


def _human_size(num: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num) < 1024:
            return f"{num:.1f}{unit}"
        num /= 1024
    return f"{num:.1f}PB"


@click.group()
def files():
    """Perintah bantu seputar file & folder (cari file besar, bersihkan junk)."""
    pass


@files.command("largest")
@click.argument("path", type=click.Path(exists=True, file_okay=False), default=".")
@click.option("-n", "--count", default=10, show_default=True, help="Jumlah file yang ditampilkan.")
def largest(path: str, count: int):
    """Tampilkan N file terbesar di dalam PATH (rekursif)."""
    sizes = []
    for root, _, filenames in os.walk(path):
        for name in filenames:
            fp = Path(root) / name
            try:
                sizes.append((fp.stat().st_size, fp))
            except OSError:
                continue

    sizes.sort(key=lambda x: x[0], reverse=True)

    table = Table(title=f"{count} file terbesar di {path}")
    table.add_column("Ukuran", justify="right")
    table.add_column("Path")
    for size, fp in sizes[:count]:
        table.add_row(_human_size(size), str(fp))
    console.print(table)


@files.command("clean-junk")
@click.argument("path", type=click.Path(exists=True, file_okay=False), default=".")
@click.option("--apply", "apply_", is_flag=True, help="Benar-benar hapus. Tanpa ini hanya preview.")
def clean_junk(path: str, apply_: bool):
    """Cari & (opsional) hapus folder/file junk umum (__pycache__, node_modules, dll)."""
    import shutil
    import fnmatch

    targets = []
    for root, dirnames, filenames in os.walk(path):
        for d in list(dirnames):
            if any(fnmatch.fnmatch(d, pat) for pat in JUNK_PATTERNS):
                targets.append(Path(root) / d)
                dirnames.remove(d)
        for f in filenames:
            if any(fnmatch.fnmatch(f, pat) for pat in JUNK_PATTERNS):
                targets.append(Path(root) / f)

    if not targets:
        console.print("Tidak ditemukan junk file/folder.")
        return

    for t in targets:
        console.print(f"  {t}")

    if apply_:
        for t in targets:
            if t.is_dir():
                shutil.rmtree(t, ignore_errors=True)
            else:
                t.unlink(missing_ok=True)
        console.print(f"[green]{len(targets)} item dihapus.[/green]")
    else:
        console.print(f"\n[yellow]Preview saja ({len(targets)} item).[/yellow] Jalankan dengan --apply untuk menghapus.")


@files.command("tree")
@click.argument("path", type=click.Path(exists=True, file_okay=False), default=".")
@click.option("--depth", default=2, show_default=True, help="Kedalaman maksimum direktori.")
def tree(path: str, depth: int):
    """Tampilkan struktur direktori sederhana hingga --depth level."""
    root = Path(path)

    def walk(dir_path: Path, prefix: str, level: int):
        if level > depth:
            return
        entries = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name))
        entries = [e for e in entries if not e.name.startswith(".")]
        for i, entry in enumerate(entries):
            connector = "└── " if i == len(entries) - 1 else "├── "
            console.print(f"{prefix}{connector}{entry.name}")
            if entry.is_dir():
                extension = "    " if i == len(entries) - 1 else "│   "
                walk(entry, prefix + extension, level + 1)

    console.print(f"[bold]{root}[/bold]")
    walk(root, "", 1)
