import click

from python_package.client import Client


@click.group()
def main():
    """Python Package"""


@click.command()
@click.argument("arg")
@click.option("--flag", "-f", is_flag=True, help="Flag")
def command(arg, flag):
    """Command"""

    client = Client()
    print(client.action())


main.add_command(command)
