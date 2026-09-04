"""Entry point utama untuk perintah `toolshed`."""

import click

from toolshed import __version__
from toolshed.commands import git_helper, file_manager


@click.group()
@click.version_option(version=__version__, prog_name="toolshed")
def main():
    """Toolshed — kumpulan perintah praktis untuk kerja developer sehari-hari."""
    pass


main.add_command(git_helper.git)
main.add_command(file_manager.files)


if __name__ == "__main__":
    main()
