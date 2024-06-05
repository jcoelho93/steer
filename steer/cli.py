import json
import click
from io import TextIOWrapper
from steer.schema import Schema
from steer.models import OutputType


output_types = [t.value for t in OutputType]


@click.command()
@click.argument('json_schema', type=click.File('r'))
@click.option('--output-type', '-t', help="The type of output", type=click.Choice(output_types), default='stdout')
@click.option('--output-file', '-o', help="The file to output data")
def steer(json_schema: TextIOWrapper, output_type: str, output_file: str = None):
    content = json.loads(json_schema.read())
    schema = Schema.from_dict(content)
    schema.prompt(OutputType(output_type), output_file)
