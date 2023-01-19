import subprocess

import click
from forgecore import Forge
from forgecore.packages import forgepackage_installed

from .install import install_git_hook


@click.command()
@click.option("--install", is_flag=True)
@click.pass_context
def cli(ctx, install):
    """Git pre-commit checks"""
    forge = Forge()

    if install:
        install_git_hook()
        return

    if forgepackage_installed("forge-format"):
        forge.venv_cmd("forge", "format", "--check", check=True)

    if not django_db_connected():
        click.echo()
        click.secho("Skipping database checks", bold=True, fg="yellow")
        click.secho("Running Django checks (without database)", bold=True)
        forge.manage_cmd("check", check=True)
    else:
        click.echo()
        click.secho("Running Django checks", bold=True)
        forge.manage_cmd("check", "--database", "default", check=True)

        click.echo()
        click.secho("Checking Django migrations", bold=True)
        forge.manage_cmd("migrate", "--check", check=True)

    click.echo()
    click.secho("Checking for Django models missing migrations", bold=True)
    forge.manage_cmd("makemigrations", "--dry-run", "--check", check=True)

    if forgepackage_installed("forge-test"):
        click.echo()
        click.secho("Running tests", bold=True)
        forge.venv_cmd("forge", "test", check=True)


def django_db_connected():
    try:
        Forge().manage_cmd(
            "showmigrations",
            "--skip-checks",
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False
