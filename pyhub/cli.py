import json

import click

from pyhub.client import DockerhubClient
from pyhub.tools import get_credentials_from_env

CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
    auto_envvar_prefix="PYHUB",
)


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """DockerHub client"""


@click.group()
def repo():
    """Repositories"""


@click.command()
@click.argument("name")
@click.option("--private", "-p", is_flag=True, default=False)
@click.option("--group", "-g", type=(str, str))
@click.option("--username", required=True)
@click.option("--password", required=True)
@click.option("--org", required=True)
def create(name, private, group, **credentials):
    """Create a repository"""

    client = DockerhubClient(**credentials)

    # Check repository
    if name not in client.get_repositories():
        client.create_repository(name, private=private)
    else:
        click.echo("Skipping creation, repository already exists.")

    if group:
        team, permission = group
        group_id = client.get_group_by_name(team)

        click.echo(f"Add team {team} with {permission} permission.")
        client.set_permissions(name, group_id, permission)


@click.command()
@click.option("--output", "-o", required=False, default="plain")
@click.option("--separator", "-s", required=False, default=", ")
@click.option("--username", required=True)
@click.option("--password", required=True)
@click.option("--org", required=True)
def list(output, separator, **credentials):
    """List repositories"""

    client = DockerhubClient(**credentials)
    res = client.get_repositories()

    if output not in ["plain", "json"]:
        click.echo("Output not supported.", err=True)
        raise click.Abort()

    if output == "plain":
        content = separator.join(res)

    if output == "json":
        content = json.dumps(res, indent=4)

    click.echo(content)


@click.command()
@click.argument("repository")
@click.option("--output", "-o", default="plain", help="Output format: plain/json")
@click.option(
    "--separator", "-s", default=", ", help="Separator for plain text format."
)
@click.option(
    "--field", "-f", multiple=True, default=[], help="Fields (can be multiple)"
)
@click.option("--username", required=True)
@click.option("--password", required=True)
@click.option("--org", required=True)
def tags(output, repository, separator, field, **credentials):
    """List tags from repository"""

    options = {}
    if field:
        options["fields"] = field

    client = DockerhubClient(**credentials)
    res = client.get_tags(repository, **options)

    if output not in ["plain", "json"]:
        click.echo("Output not supported.", err=True)
        raise click.Abort()

    if output == "plain":
        content = separator.join(res)

    if output == "json":
        content = json.dumps(res, indent=4)

    click.echo(content)


repo.add_command(create)
repo.add_command(list)
repo.add_command(tags)
main.add_command(repo)
