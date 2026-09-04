"""Perintah `toolshed files ...` — utilitas ringkas untuk kelola file lokal."""

import hashlib
import os
import re
from collections import defaultdict
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


def _file_hash(fp: Path, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with open(fp, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


@files.command("dedupe")
@click.argument("path", type=click.Path(exists=True, file_okay=False), default=".")
@click.option("--apply", "apply_", is_flag=True, help="Hapus duplikat (menyisakan 1 file per grup). Tanpa ini hanya preview.")
def dedupe(path: str, apply_: bool):
    """Cari file duplikat berdasarkan isi (hash), bukan sekadar nama."""
    by_size = defaultdict(list)
    for root, _, filenames in os.walk(path):
        for name in filenames:
            fp = Path(root) / name
            try:
                size = fp.stat().st_size
            except OSError:
                continue
            if size > 0:
                by_size[size].append(fp)

    # Hanya hash file yang size-nya bentrok dengan file lain (hemat waktu)
    by_hash = defaultdict(list)
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        for fp in paths:
            try:
                by_hash[_file_hash(fp)].append(fp)
            except OSError:
                continue

    dupe_groups = {h: paths for h, paths in by_hash.items() if len(paths) > 1}

    if not dupe_groups:
        console.print("Tidak ditemukan file duplikat.")
        return

    total_wasted = 0
    total_removed = 0
    for h, paths in dupe_groups.items():
        keep, *rest = sorted(paths, key=lambda p: str(p))
        size = keep.stat().st_size
        console.print(f"\n[bold]Grup duplikat[/bold] ({_human_size(size)} masing-masing):")
        console.print(f"  [green]simpan[/green]  {keep}")
        for r in rest:
            console.print(f"  [red]dobel [/red]  {r}")
            total_wasted += size

        if apply_:
            for r in rest:
                r.unlink(missing_ok=True)
                total_removed += 1

    if apply_:
        console.print(f"\n[green]{total_removed} file duplikat dihapus, menghemat {_human_size(total_wasted)}.[/green]")
    else:
        console.print(
            f"\n[yellow]Preview saja.[/yellow] Total bisa hemat {_human_size(total_wasted)}. "
            "Jalankan dengan --apply untuk benar-benar menghapus duplikat (1 salinan tetap disimpan per grup)."
        )


@files.command("rename-bulk")
@click.argument("path", type=click.Path(exists=True, file_okay=False), default=".")
@click.option("--match", "pattern", required=True, help="Regex pattern untuk dicocokkan pada nama file (bukan path).")
@click.option("--to", "replacement", required=True, help="Pengganti. Bisa pakai grup regex, misal '\\1_baru'.")
@click.option("--recursive", is_flag=True, help="Telusuri juga sub-folder, bukan cuma folder ini.")
@click.option("--apply", "apply_", is_flag=True, help="Benar-benar rename. Tanpa ini hanya preview.")
def rename_bulk(path: str, pattern: str, replacement: str, recursive: bool, apply_: bool):
    """Rename banyak file sekaligus pakai regex pada PATH.

    Contoh:

        toolshed files rename-bulk . --match "IMG_(\\d+)\\.jpg" --to "photo_\\1.jpg"
    """
    try:
        regex = re.compile(pattern)
    except re.error as e:
        raise click.ClickException(f"Pattern regex tidak valid: {e}")

    root = Path(path)
    if recursive:
        candidates = [p for p in root.rglob("*") if p.is_file()]
    else:
        candidates = [p for p in root.iterdir() if p.is_file()]

    renames = []
    for fp in candidates:
        new_name = regex.sub(replacement, fp.name)
        if new_name != fp.name:
            renames.append((fp, fp.with_name(new_name)))

    if not renames:
        console.print("Tidak ada file yang cocok dengan pattern.")
        return

    table = Table(title=f"Rename {len(renames)} file")
    table.add_column("Dari")
    table.add_column("Ke")
    for old, new in renames:
        table.add_row(old.name, new.name)
    console.print(table)

    if apply_:
        renamed = 0
        for old, new in renames:
            if new.exists():
                console.print(f"[yellow]Lewati (target sudah ada):[/yellow] {new.name}")
                continue
            old.rename(new)
            renamed += 1
        console.print(f"[green]{renamed} file di-rename.[/green]")
    else:
        console.print("\n[yellow]Preview saja.[/yellow] Jalankan dengan --apply untuk benar-benar rename.")
