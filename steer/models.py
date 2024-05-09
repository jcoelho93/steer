from pydantic import BaseModel
from typing import Optional, List
from questionary import prompt


class Property(BaseModel):
    type: Optional[str] = None
    ref: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class StringProperty(Property):
    type: str = 'string'
    format: Optional[str] = None
    default: Optional[str] = None
    enum: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, key, obj):
        return cls(
            name=key,
            type=obj.get('type'),
            format=obj.get('format'),
            default=obj.get('default'),
            enum=obj.get('enum')
        )

    def prompt(self):
        if self.enum:
            return prompt({
                'type': 'select',
                'name': self.name,
                'message': f"{self.name} (string): [{self.default or ""}]",
                'choices': self.enum
            })
        else:
            return prompt({
                'type': 'input',
                'name': self.name,
                'message': f"{self.name} (string): [{self.default or ""}]",
            })


class IntegerProperty(Property):
    type: str = 'integer'
    format: Optional[str] = None
    default: Optional[int] = None
    enum: Optional[List[int]] = None

    @classmethod
    def from_dict(cls, key, obj):
        return cls(
            name=key,
            type=obj.get('type'),
            format=obj.get('format'),
            default=obj.get('default'),
            enum=obj.get('enum')
        )

    def prompt(self):
        return prompt({
            'type': 'input',
            'name': self.name,
            'message': f"{self.name} (int): [{self.default or ""}]",
        })


class ObjectProperty(Property):
    type: str = 'object'
    additionalProperties: bool = False
    properties: Optional[List[Property]] = []

    @classmethod
    def from_dict(cls, key, obj):
        property = cls(
            name=key,
            type=obj.get('type'),
            additionalProperties=bool(obj.get('additionalProperties', False)),
        )
        if obj.get('properties') is not None:
            return property.with_properties(obj['properties'])

        return property

    def add_property(self, property: Property):
        self.properties.append(property)

    def with_properties(self, properties):
        for key, value in properties.items():
            if value.get('type') == 'string':
                self.add_property(StringProperty.from_dict(key, value))
            elif value.get('type') == 'integer':
                self.add_property(IntegerProperty.from_dict(key, value))
            elif value.get('type') == 'object':
                self.add_property(ObjectProperty.from_dict(key, value))
            elif value.get('type') == 'boolean':
                self.add_property(BooleanProperty.from_dict(key, value))
            elif value.get('type') == 'array':
                self.add_property(ArrayProperty.from_dict(key, value))
        return self


class BooleanProperty(Property):
    type: str = 'boolean'
    default: Optional[bool] = False

    @classmethod
    def from_dict(cls, key, obj):
        return cls(
            name=key,
            type=obj.get('type'),
            default=obj.get('default')
        )

    def prompt(self):
        return prompt({
            'type': 'confirm',
            'name': self.name,
            'message': f"{self.name}: [{self.default or False}]",
        })


class ArrayProperty(Property):
    type: str = 'array'
    items: Optional[Property] = None

    @classmethod
    def from_dict(cls, key, obj):
        return cls(
            name=key,
            type=obj.get('type'),
            items=obj.get('items')
        )

    def prompt(self):
        return prompt({
            'type': 'input',
            'name': self.name,
            'message': f"{self.name} (array):",
        })


class Schema(BaseModel):
    schema_url: str
    type: str = 'object'
    additionalProperties: bool = False
    description: Optional[str] = None
    required: Optional[List[str]] = []
    properties: Optional[List[Property]] = []
    definitions: Optional[List[Property]] = []

    def add_property(self, property: Property):
        self.properties.append(property)

    @classmethod
    def from_dict(cls, obj):
        schema = cls(
            schema_url=obj.get('$schema'),
            type=obj.get('type'),
            additionalProperties=obj.get('additionalProperties'),
            description=obj.get('description'),
            required=obj.get('required'),
        )

        for key, value in obj['properties'].items():
            if value.get('type') == 'string':
                schema.add_property(StringProperty.from_dict(key, value))
            elif value.get('type') == 'integer':
                schema.add_property(IntegerProperty.from_dict(key, value))
            elif value.get('type') == 'object':
                schema.add_property(ObjectProperty.from_dict(key, value))
            elif value.get('type') == 'boolean':
                schema.add_property(BooleanProperty.from_dict(key, value))
            elif value.get('type') == 'array':
                schema.add_property(ArrayProperty.from_dict(key, value))

        return schema
