from click.testing import CliRunner

from toolshed.cli import main


def test_main_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Toolshed" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0


def test_files_tree(tmp_path):
    (tmp_path / "a.txt").write_text("hi")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("hi")

    runner = CliRunner()
    result = runner.invoke(main, ["files", "tree", str(tmp_path)])
    assert result.exit_code == 0
    assert "a.txt" in result.output


def test_files_largest(tmp_path):
    (tmp_path / "a.txt").write_text("x" * 100)
    runner = CliRunner()
    result = runner.invoke(main, ["files", "largest", str(tmp_path)])
    assert result.exit_code == 0
    assert "a.txt" in result.output


def test_files_dedupe_preview(tmp_path):
    (tmp_path / "a.txt").write_text("sama isinya")
    (tmp_path / "b.txt").write_text("sama isinya")
    (tmp_path / "c.txt").write_text("beda")

    runner = CliRunner()
    result = runner.invoke(main, ["files", "dedupe", str(tmp_path)])
    assert result.exit_code == 0
    assert "duplikat" in result.output.lower()
    # preview: tidak ada file yang benar-benar terhapus
    assert (tmp_path / "a.txt").exists()
    assert (tmp_path / "b.txt").exists()


def test_files_dedupe_apply(tmp_path):
    (tmp_path / "a.txt").write_text("sama isinya")
    (tmp_path / "b.txt").write_text("sama isinya")

    runner = CliRunner()
    result = runner.invoke(main, ["files", "dedupe", str(tmp_path), "--apply"])
    assert result.exit_code == 0
    remaining = list(tmp_path.glob("*.txt"))
    assert len(remaining) == 1


def test_files_rename_bulk_preview(tmp_path):
    (tmp_path / "IMG_001.jpg").write_text("x")
    (tmp_path / "IMG_002.jpg").write_text("x")

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["files", "rename-bulk", str(tmp_path), "--match", r"IMG_(\d+)\.jpg", "--to", r"photo_\1.jpg"],
    )
    assert result.exit_code == 0
    # preview: file lama belum berubah nama
    assert (tmp_path / "IMG_001.jpg").exists()


def test_files_rename_bulk_apply(tmp_path):
    (tmp_path / "IMG_001.jpg").write_text("x")

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "files", "rename-bulk", str(tmp_path),
            "--match", r"IMG_(\d+)\.jpg", "--to", r"photo_\1.jpg", "--apply",
        ],
    )
    assert result.exit_code == 0
    assert (tmp_path / "photo_001.jpg").exists()
    assert not (tmp_path / "IMG_001.jpg").exists()


def test_git_stash_list_empty(tmp_path, monkeypatch):
    import subprocess
    subprocess.run(["git", "init", "-q"], cwd=tmp_path)
    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["git", "stash-list"])
    assert result.exit_code == 0
    assert "tidak ada stash" in result.output.lower()


def test_git_undo(tmp_path, monkeypatch):
    import subprocess
    subprocess.run(["git", "init", "-q"], cwd=tmp_path)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=tmp_path)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path)
    (tmp_path / "f.txt").write_text("v1")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path)
    subprocess.run(["git", "commit", "-q", "-m", "first"], cwd=tmp_path)
    (tmp_path / "f.txt").write_text("v2")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path)
    subprocess.run(["git", "commit", "-q", "-m", "second"], cwd=tmp_path)
    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["git", "undo"])
    assert result.exit_code == 0
    assert (tmp_path / "f.txt").read_text() == "v2"
