# Steer

![PyPI - Version](https://img.shields.io/pypi/v/python-steer)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/python-steer)
![PyPI - Downloads](https://img.shields.io/pypi/dm/python-steer)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=jcoelho93_steer&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=jcoelho93_steer)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=jcoelho93_steer&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=jcoelho93_steer)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=jcoelho93_steer&metric=coverage)](https://sonarcloud.io/summary/new_code?id=jcoelho93_steer)

A CLI tool to interactively generate JSON and YAML files from JSON schemas

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

This is still very much in alpha. There is still a lot of work to implement all the json schema specifications.
It is usable for a few use cases without major issues.

- [x] Implement prompt for `array` of `string`, `number` and `integer` property type
- [ ] Implement prompt for `array` of `object` property type
- [ ] Implement the `$ref` property type
- [x] Validate string property values with `pattern`
- [ ] Implement prompt for `additionalProperties`
- [ ] Validate `required` fields
- [x] Implement `number` property type
- [ ] Implement `allOf`, `anyOf`, `oneOf` keywords

## Use cases

Here are some examples where this tool might be useful.

### Helm chart values

If you're deploying to Kubernetes using a helm chart, instead of going through the charts documentation to set your values, you could use this tool to interactively set up the `values.yaml` file for the chart.

```shell
steer chart.schema.json --output-type yaml --output-file values.yaml
...
```

### OpenAPI Specification

When building an API with the OpenAPI specification you can use this tool to design your API's endpoints.

```shell
steer openapi.schema.json --output-type yaml --output-file rest-api.yaml
...
```

### Writing CICD configuration

This can help you define your CICD configuration file for different systems like GitHub Actions, CircleCI, GitLab CI, etc.

```shell
steer circleci.schema.json --output-type yaml --output-file config.yml
...
```
