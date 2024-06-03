import json

import click

from pyhub.client import DockerhubClient
from pyhub.tools import get_credentials_from_env


@click.group()
def main():
    """DockerHub client"""


@click.group()
def repo():
    """Repositories"""


@click.command()
@click.argument("name")
@click.option("--private", "-p", is_flag=True, required=False, default=False)
@click.option("--group", "-g", required=False)
@click.option("--permission", "-p", required=False)
def create(name, private, group, permission):
    """Create a repository"""

    try:
        credentials = get_credentials_from_env()
    except ValueError as error:
        click.echo(error, err=True)
        raise click.Abort()

    client = DockerhubClient(**credentials)

    # Check repository
    if name in client.get_repositories():
        click.echo("Repository already exists.", err=True)
        raise click.Abort()

    client.create_repository(name, private=private)

    if group and permission:
        group_id = client.get_group_by_name(group)
        client.set_permissions(name, group_id, permission)


@click.command()
@click.option("--output", "-o", required=False, default="plain")
@click.option("--separator", "-s", required=False, default=", ")
def list(output, separator):
    """List repositories"""

    try:
        credentials = get_credentials_from_env()
    except ValueError as error:
        click.echo(error, err=True)
        raise click.Abort()

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
@click.option(
    "--output", "-o", required=False, default="plain", help="Output format: plain/json"
)
@click.option(
    "--separator",
    "-s",
    required=False,
    default=", ",
    help="Separator for plain text format, default: ', '",
)
@click.option(
    "--field",
    "-f",
    multiple=True,
    required=False,
    default=[],
    help="Fields (can be multiple), eg: -f name",
)
def tags(output, repository, separator, field):
    """List tags from repository"""

    try:
        credentials = get_credentials_from_env()
    except ValueError as error:
        click.echo(error, err=True)
        raise click.Abort()

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
