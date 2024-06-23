import os
import re
import json
import yaml
import logging
import requests
import questionary
import requests_cache
from jsonpath_ng import parse
from questionary import prompt
from pydantic import BaseModel
from steer.models import OutputType
from typing import Optional, List, Any, Dict


logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))


class Property(BaseModel):
    type: Optional[str] = None
    ref: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    default: Optional[Any] = None
    allOf: Optional[List[BaseModel]] = None
    path: Optional[str] = None
    value: Optional[Any] = None

    parent_schema: Optional[Any] = None

    def save(self, data: Any):
        if self.value is not None:
            json_path = parse(self.path)
            json_path.update_or_create(data, self.value)

    def _get_prompt_args(self):
        args = {
            'name': self.name,
            'message': f"{self.name} ({self.type}): ",
            'default': self.default,
        }
        return {k: v for k, v in args.items() if v is not None}

    def set_value(self, value: Any):
        self._validate(value)
        self.value = value

    def _validate(self, value: Any) -> Any:
        raise NotImplementedError()

    def prompt(self):
        args = self._get_prompt_args()
        while True:
            try:
                value = prompt(args).get(self.name)
                if value is not None:
                    self.value = self._validate(value)
            except ValueError as e:
                print(f"Error: {e}")
                continue
            break


class StringProperty(Property):
    type: str = 'string'
    format: Optional[str] = None
    pattern: Optional[str] = None
    enum: Optional[List[str]] = None

    def _get_prompt_args(self):
        args = {
            'type': 'select' if self.enum else 'input',
            'name': self.name,
            'message': f"{self.name} ({self.type}): ",
            'default': self.default,
            'choices': self.enum
        }
        return {k: v for k, v in args.items() if v is not None}

    def _validate(self, value: str) -> bool:
        if self.pattern is not None and value is not None:
            if not re.match(self.pattern, value):
                raise ValueError(f"Invalid value. Must match pattern: '{self.pattern}'")
        return True

    @classmethod
    def from_dict(cls, key: str, obj: Dict, parent: str, schema: Any = None):
        return cls(
            name=key,
            type=obj.get('type'),
            format=obj.get('format'),
            default=obj.get('default'),
            enum=obj.get('enum'),
            pattern=obj.get('pattern'),
            path=parent + key,
            schema=schema
        )

    def prompt(self):
        args = self._get_prompt_args()
        while True:
            value = prompt(args).get(self.name)
            try:
                self._validate(value)
                self.value = value
            except ValueError as e:
                print(f"Error: {e}")
            break


class IntegerProperty(Property):
    type: str = 'integer'
    format: Optional[str] = None
    enum: Optional[List[int]] = None

    @classmethod
    def from_dict(cls, key, obj, parent, schema: Any = None):
        return cls(
            name=key,
            type=obj.get('type'),
            format=obj.get('format'),
            default=obj.get('default'),
            enum=obj.get('enum'),
            path=parent + key,
            schema=schema
        )

    def _get_prompt_args(self):
        args = {
            'type': 'select' if self.enum else 'input',
            'name': self.name,
            'message': f"{self.name} ({self.type}): ",
            'choices': self.enum,
            'default': self.default
        }
        return {k: v for k, v in args.items() if v is not None}

    def _validate(self, value: str) -> int:
        validated_value = None
        try:
            validated_value = int(value)
        except ValueError:
            raise ValueError("Invalid value. Must be an integer")
        if self.enum and validated_value not in self.enum:
            raise ValueError(f"Invalid value. Must be one of: {self.enum}")
        return validated_value


class NumberProperty(Property):
    type: str = 'number'
    format: Optional[str] = None
    enum: Optional[List[float]] = None

    @classmethod
    def from_dict(cls, key, obj, parent, schema: Any = None):
        return cls(
            name=key,
            type=obj.get('type'),
            format=obj.get('format'),
            default=obj.get('default'),
            enum=obj.get('enum'),
            path=parent + key,
            schema=schema
        )

    def _get_prompt_args(self):
        args = {
            'type': 'select' if self.enum else 'input',
            'name': self.name,
            'message': f"{self.name} ({self.type}): ",
            'choices': self.enum,
            'default': str(self.default)
        }
        return {k: v for k, v in args.items() if v is not None}

    def _validate(self, value: str) -> float:
        validated_value = None
        try:
            if '.' in value:
                validated_value = float(value)
            else:
                validated_value = int(value)
        except ValueError:
            raise ValueError("Invalid value. Must be an integer")
        if self.enum and validated_value not in self.enum:
            raise ValueError(f"Invalid value. Must be one of: {self.enum}")
        return validated_value


class BooleanProperty(Property):
    type: str = 'boolean'

    @classmethod
    def from_dict(cls, key, obj, parent, schema: Any = None):
        return cls(
            name=key,
            type=obj.get('type'),
            default=obj.get('default'),
            path=parent + key,
            schema=schema
        )

    def _get_prompt_args(self):
        args = {
            'type': 'select',
            'name': self.name,
            'message': f"{self.name}?",
            'choices': ['true', 'false'],
        }
        if self.default is not None:
            args['default'] = 'true' if self.default else 'false'
        return {k: v for k, v in args.items() if v is not None}

    def prompt(self):
        args = self._get_prompt_args()
        value = prompt(args).get(self.name)
        self.value = value == 'true'


class ArrayProperty(Property):
    type: str = 'array'
    minItems: Optional[int] = 0
    items: Optional[Property] = None
    uniqueItems: Optional[bool] = False

    @classmethod
    def from_dict(cls, key, obj, parent, schema: Any = None):
        return cls(
            name=key,
            type=obj.get('type'),
            items=PropertyFactory.get_property(key, obj.get('items'), '.', schema) if 'items' in obj else None,
            uniqueItems=obj.get('uniqueItems'),
            minItems=obj.get('minItems'),
            path=parent + key,
            schema=schema
        )

    def prompt(self):
        elements = []
        while True:
            try:
                prop = PropertyFactory.get_property('Array element:', self.items.model_dump(), '.')
                prop.prompt()
            except NotImplementedError:
                continue
            elements.append(prop)
            if not self._add_more_elements():
                break
            else:
                continue
        self.value = [value.value for value in elements]

    def _add_more_elements(self):
        answer = questionary.select("Add more elements?", choices=['Yes', 'No']).ask()
        return answer == 'Yes'


class ObjectProperty(Property):
    type: str = 'object'
    additionalProperties: bool = False
    properties: Optional[List[Property]] = []

    @classmethod
    def from_dict(cls, key, obj, parent, schema: Any = None):
        property = cls(
            name=key,
            type=obj.get('type', 'object'),
            additionalProperties=bool(obj.get('additionalProperties', False)),
            path=parent + key,
            schema=schema
        )
        if obj.get('properties') is not None:
            return property.with_properties(obj['properties'], parent + key)

        return property

    def add_property(self, property: Property):
        if property is not None:
            self.properties.append(property)

    def with_properties(self, properties, parent):
        for key, value in properties.items():
            try:
                prop = PropertyFactory.get_property(key, value, parent + '.')
                self.add_property(prop)
            except NotImplementedError:
                continue
        return self

    def save(self, data: Any):
        for property in self.properties:
            property.save(data)

    def prompt(self):
        while True:
            choices = [p.name for p in self.properties]
            choices.append('Back')
            property = questionary.select('Select a property', choices=choices).ask()
            if property == 'Back':
                return
            for p in self.properties:
                if p.name == property:
                    p.prompt()


class Reference:
    reference: str

    def __init__(self, reference: str, session: requests.Session = None):
        self.reference = reference
        self.session = session

    def to_property(self, definitions: List[Property] = [], name: str = '') -> Property:
        if self.reference.startswith("https://") or self.reference.startswith("http://"):
            return self._get_url_reference(name)
        elif self.reference.startswith('#/definitions/'):
            return self._get_path_reference(definitions)

    def _get_url_reference(self, name: str) -> Dict:
        try:
            response = self.session.get(self.reference)
            response.raise_for_status()
            schema = response.json()
            path = '$.' + self.reference.split('#')[1].replace('/', '.')
            obj = parse(path).find(schema)[0].value
            return PropertyFactory.get_property(name, obj, '$.')
        except requests.exceptions.HTTPError as e:
            logging.error(f"Error fetching schema: {e}")
            raise e

    def _get_path_reference(self, definitions: List[Property]) -> Property:
        reference_name = self.reference.split('/')[-1]
        for definition in definitions:
            if definition.name == reference_name:
                return definition


class Schema(BaseModel):
    schema_url: str
    type: Optional[str] = 'object'
    additionalProperties: Optional[bool] = False
    description: Optional[str] = None
    required: Optional[List[str]] = []
    properties: Optional[List[Property]] = []
    definitions: Optional[List[Property]] = []
    data: Dict[str, Any] = {}

    def add_property(self, property: Property):
        self.properties.append(property)

    def add_definition(self, definition: Property):
        self.definitions.append(definition)

    def save(self, type: OutputType, filepath: str):
        data = {}
        for property in self.properties:
            property.save(data)

        if type.value == 'stdout':
            print(data)
        else:
            with open(filepath, 'w') as fp:
                if type == 'json':
                    json.dump(data, fp)
                elif type == 'yaml':
                    yaml.dump(data, fp)

    def prompt(self, output_type: str, output_file: str = None):
        try:
            while True:
                choices = [p.name for p in self.properties]
                choices.append('')
                choices.append('Discard & Exit')
                choices.append('Save & Exit')
                property = questionary.select('Select a property', choices=choices).ask()
                if property == 'Discard & Exit':
                    exit(0)
                if property == 'Save & Exit':
                    self.save(output_type, output_file)
                    exit(0)
                for p in self.properties:
                    if p.name == property:
                        p.prompt()
        except KeyboardInterrupt:
            exit(0)

    @classmethod
    def from_dict(cls, obj):
        schema = cls(
            schema_url=obj.get('$schema'),
            type=obj.get('type'),
            additionalProperties=obj.get('additionalProperties'),
            description=obj.get('description'),
            required=obj.get('required'),
        )

        for key, value in obj.get('definitions', {}).items():
            logging.debug("Loading definition '%s' to schema", key)
            try:
                definition = PropertyFactory.get_property(key, value, '$.', schema)
                schema.add_definition(definition)
            except NotImplementedError:
                continue

        for key, value in obj['properties'].items():
            logging.debug("Loading property '%s' to schema", key)
            try:
                prop = PropertyFactory.get_property(key, value, '$.', schema)
                schema.add_property(prop)
            except NotImplementedError:
                continue

        return schema


class PropertyFactory:
    session = requests_cache.CachedSession()

    @classmethod
    def get_property(self, key: str, obj: Dict, parent: str, schema: Schema = None):
        assert obj is not None, f"Property '{key}' object cannot be None"
        if obj.get('$ref'):
            ref = Reference(obj.get('$ref'), self.session)
            if schema is not None:
                prop = ref.to_property(schema.definitions, key)
            else:
                prop = ref.to_property(name=key)
            return prop

        match obj.get('type'):
            case 'string':
                return StringProperty.from_dict(key, obj, parent, schema)
            case 'integer':
                return IntegerProperty.from_dict(key, obj, parent, schema)
            case 'number':
                return NumberProperty.from_dict(key, obj, parent, schema)
            case 'object':
                return ObjectProperty.from_dict(key, obj, parent, schema)
            case 'boolean':
                return BooleanProperty.from_dict(key, obj, parent, schema)
            case 'array':
                return ArrayProperty.from_dict(key, obj, parent, schema)
            case _:
                raise NotImplementedError(f"Type {obj.get('type')} not supported yet")
