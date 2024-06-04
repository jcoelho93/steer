import json
import click
from io import TextIOWrapper
from steer.models import Schema


@click.group()
def cli():
    pass


output_types = ['stdout', 'json', 'yaml']


@cli.command(help='Interactively build a values.yml file')
@click.argument('json_schema', type=click.File('r'))
@click.option('--output-type', '-t', help="The type of output", type=click.Choice(output_types), default='stdout')
@click.option('--output-file', '-o', help="The file to output data")
def values(json_schema: TextIOWrapper, output_type: str, output_file: str = None):
    content = json.loads(json_schema.read())
    schema = Schema.from_dict(content)
    schema.prompt(output_type, output_file)
