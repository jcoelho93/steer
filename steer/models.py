from enum import Enum


class OutputType(Enum):
    JSON = 'json'
    YAML = 'yaml'
    STDOUT = 'stdout'


class StringFormat(Enum):
    # https://json-schema.org/understanding-json-schema/reference/string#built-in-formats
    DATETIME = 'date-time'
    TIME = 'time'
    DATE = 'date'
    DURATION = 'duration'
    EMAIL = 'email'
    IDN_EMAIL = 'idn-email'
    HOSTNAME = 'hostname'
    IDN_HOSTNAME = 'idn-hostname'
    IPV4 = 'ipv4'
    IPV6 = 'ipv6'
    UUID = 'uuid'
    URI = 'uri'
    URI_REFERENCE = 'uri-reference'
    IRI = 'iri'
    IRI_REFERENCE = 'iri-reference'
    URI_TEMPLATE = 'uri-template'
    JSON_POINTER = 'json-pointer'
    RELATIVE_JSON_POINTER = 'relative-json-pointer'
    REGEX = 'regex'
