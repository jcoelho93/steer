import json
import click
import questionary
from io import TextIOWrapper
from steer.models import Schema


@click.group()
def cli():
    pass


@cli.command(help='Interactively build a values.yml file')
@click.argument('json_schema', type=click.File('r'))
@click.option('--output-file', '-o', help="The file to output data")
def values(json_schema: TextIOWrapper, output_file: str = None):
    content = json.loads(json_schema.read())
    schema = Schema.from_dict(content)
    schema.prompt(output_file)
