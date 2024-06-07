# Steer

A tool to help you write JSON and YAML files from JSON schemas

## Installation

```shell
pip install steer
```

## Usage

Let's say you want to build an OpenAPI specification for an API.

1. Download the OpenAPI json schema from [here](https://github.com/OAI/OpenAPI-Specification/blob/main/schemas/v2.0/schema.json)
1. Run `steer`:
    ```
    ~$ steer examples/openapi.schema.json --output-type json --output-file restapi.json
    ? Select a property (Use arrow keys)
     » swagger
       host
       basePath
       tags

       Discard & Exit
       Save & Exit
    ```

## Roadmap

- [ ] Implement the `array` of `objects` property type
- [ ] Implement the `$ref` property type
- [x] Validate string property values with `pattern`
- [ ] Implement prompt for `additionalProperties`
- [ ] Validate `required` fields
- [ ] Implement `number` property type
