import json
import questionary
from jsonpath_ng import parse
from questionary import prompt
from pydantic import BaseModel
from jsonpath_ng.jsonpath import JSONPath
from typing import Optional, List, Any, Dict


class Property(BaseModel):
    type: Optional[str] = None
    ref: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    default: Optional[Any] = None
    allOf: Optional[List[BaseModel]] = None
    path: Optional[Any] = None
    value: Optional[Any] = None

    @classmethod
    def from_dict(cls, key, obj):
        return cls(
            name=key,
            type=obj.get('type'),
            ref=obj.get('$ref'),
            description=obj.get('description'),
            allOf=obj.get('allOf')
        )

    def save(self, data: Any):
        if self.value:
            self.path.update_or_create(data, self.value)

    def _get_prompt_args(self):
        args = {
            'name': self.name,
            'message': f"{self.name} ({self.type}): ",
            'default': self.default,
        }
        return {k: v for k, v in args.items() if v is not None}


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

    @classmethod
    def from_dict(cls, key, obj, parent):
        return cls(
            name=key,
            type=obj.get('type'),
            format=obj.get('format'),
            default=obj.get('default'),
            enum=obj.get('enum'),
            pattern=obj.get('pattern'),
            path=parse(parent + key)
        )

    def prompt(self):
        args = self._get_prompt_args()
        self.value = prompt(args).get(self.name)


class IntegerProperty(Property):
    type: str = 'integer'
    format: Optional[str] = None
    enum: Optional[List[int]] = None

    @classmethod
    def from_dict(cls, key, obj, parent):
        return cls(
            name=key,
            type=obj.get('type'),
            format=obj.get('format'),
            default=obj.get('default'),
            enum=obj.get('enum'),
            path=parse(parent + key)
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

    def prompt(self):
        args = self._get_prompt_args()
        self.value = prompt(args).get(self.name)


class ObjectProperty(Property):
    type: str = 'object'
    additionalProperties: bool = False
    properties: Optional[List[Property]] = []

    @classmethod
    def from_dict(cls, key, obj, parent):
        property = cls(
            name=key,
            type=obj.get('type', 'object'),
            additionalProperties=bool(obj.get('additionalProperties', False)),
            path=parse(parent + key)
        )
        if obj.get('properties') is not None:
            return property.with_properties(obj['properties'], parent + key)

        return property

    def add_property(self, property: Property):
        self.properties.append(property)

    def with_properties(self, properties, parent):
        for key, value in properties.items():
            if value.get('type') == 'string':
                self.add_property(StringProperty.from_dict(key, value, parent + '.'))
            elif value.get('type') == 'integer':
                self.add_property(IntegerProperty.from_dict(key, value, parent + '.'))
            elif value.get('type') == 'object':
                self.add_property(ObjectProperty.from_dict(key, value, parent + '.'))
            elif value.get('type') == 'boolean':
                self.add_property(BooleanProperty.from_dict(key, value, parent + '.'))
            elif value.get('type') == 'array':
                self.add_property(ArrayProperty.from_dict(key, value, parent + '.'))
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


class BooleanProperty(Property):
    type: str = 'boolean'

    @classmethod
    def from_dict(cls, key, obj, parent):
        return cls(
            name=key,
            type=obj.get('type'),
            default=obj.get('default'),
            path=parse(parent + key)
        )

    def prompt(self):
        self.value = prompt({
            'type': 'confirm',
            'name': self.name,
            'message': f"{self.name}?",
            'default': self.default or False
        }).get(self.name)


class ArrayProperty(Property):
    type: str = 'array'
    items: Optional[Property] = None

    @classmethod
    def from_dict(cls, key, obj, parent):
        return cls(
            name=key,
            type=obj.get('type'),
            items=obj.get('items'),
            path=parse(parent + key)
        )

    def prompt(self):
        self.value = prompt({
            'type': 'input',
            'name': self.name,
            'message': f"{self.name} (array):",
            'default': self.default
        }).get(self.name)


class RefProperty(Property):
    type: str = 'ref'


class Schema(BaseModel):
    schema_url: str
    type: str = 'object'
    additionalProperties: bool = False
    description: Optional[str] = None
    required: Optional[List[str]] = []
    properties: Optional[List[Property]] = []
    definitions: Optional[List[Property]] = []
    data: Dict[str, Any] = {}

    def add_property(self, property: Property):
        self.properties.append(property)

    def add_definition(self, definition: Property):
        self.definitions.append(definition)

    def save(self, filepath):
        data = {}
        with open(filepath, 'w') as fp:
            for property in self.properties:
                property.save(data)
            json.dump(data, fp)

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
                    self.save(output_file)
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

        for key, value in obj.get('definitions', []).items():
            schema.add_definition(ObjectProperty.from_dict(key, value, '$.'))

        for key, value in obj['properties'].items():
            if value.get('type') == 'string':
                schema.add_property(StringProperty.from_dict(key, value, '$.'))
            elif value.get('type') == 'integer':
                schema.add_property(IntegerProperty.from_dict(key, value, '$.'))
            elif value.get('type') == 'object':
                schema.add_property(ObjectProperty.from_dict(key, value, '$.'))
            elif value.get('type') == 'boolean':
                schema.add_property(BooleanProperty.from_dict(key, value, '$.'))
            elif value.get('type') == 'array':
                schema.add_property(ArrayProperty.from_dict(key, value, '$.'))
            elif value.get('type') == 'ref':
                schema.add_property(RefProperty.from_dict(key, value, '$.'))

        return schema
