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
