# Steer

A tool to help you write JSON and YAML files from JSON schemas

## Installation

```shell
pip install python-steer
```

## Usage

Let's say you want to build an OpenAPI specification for an API.

1. Download the OpenAPI json schema from [here](https://github.com/OAI/OpenAPI-Specification/blob/main/schemas/v2.0/schema.json)
1. Run steer from the command line

[![asciicast](https://asciinema.org/a/s7k97RgWaRjhokuT1EZ6SgYlw.svg)](https://asciinema.org/a/s7k97RgWaRjhokuT1EZ6SgYlw)

## Roadmap

- [ ] Implement the `array` of `objects` property type
- [ ] Implement the `$ref` property type
- [x] Validate string property values with `pattern`
- [ ] Implement prompt for `additionalProperties`
- [ ] Validate `required` fields
- [x] Implement `number` property type
- [ ] Implement `allOf`, `anyOf`, `oneOf` keywords
