import json
import click
import questionary
from io import TextIOWrapper
from steer.models import Schema
from questionary import prompt


@click.group()
def cli():
    pass


@cli.command(help='Interactively build a values.yml file')
@click.argument('json_schema', type=click.File('r'))
def values(json_schema: TextIOWrapper):
    content = json.loads(json_schema.read())
    schema = Schema.from_dict(content)

    while True:
        property = questionary.select('Select a property', choices=[p.name for p in schema.properties]).ask()
        for p in schema.properties:
            if p.name == property:
                p.prompt()
