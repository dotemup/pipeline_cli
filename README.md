# Pipeline CLI

This project automates workflows similar to CI/CD processes, allowing users to define and execute build, test, deploy, and undeploy stages through a YAML-configured pipeline and a command-line interface.

## Features

- Automate build, test, deploy, and undeploy processes.
- Easy configuration with `pipeline.yaml`.
- CLI support for easy interaction.

## Requirements

- Python 3.6+
- PyYAML

## Installation

Clone the repository:

```bash
git clone https://github.com/dotemup/pipeline_cli.git
cd pipeline_cli
```

Install the package:

```bash
pip install .
```

## Usage

Execute a pipeline stage:
pipeline <action> [-d <directory>] [-f <file>]
- `<action>`: The pipeline stage (`build`, `test`, `deploy`, `undeploy`).
- `-d <directory>`: Directory containing `pipeline.yaml` (default: current directory).
- `-f <file>`: The pipeline configuration file (default: `pipeline.yaml`).

### Basic Usage Examples
While in a directory that contains a pipeline.yaml:
```
pipeline build
```
Or run multiple stages in order:
```
pipeline build test deploy
```

## Configuring `pipeline.yaml`

The `pipeline.yaml` file defines the steps to be executed for each stage of your pipeline, such as build, test, deploy, and undeploy. Here's how to structure your `pipeline.yaml`:

### Basic Structure

```yaml
build:
  - echo "Building project"
test:
  - echo "Running tests"
deploy:
  - echo "Deploying to environment"
undeploy:
  - echo "Removing from environment"
```

### Nested Calls

Nested calls allow you to execute a pipeline within another pipeline, facilitating complex workflows that require multiple stages or steps to be executed in sequence or conditionally. To implement nested calls, you specify a command to run another pipeline configuration from within a `pipeline.yaml` stage.

For instance, if you have a primary pipeline that requires executing a secondary pipeline as part of the build process, you can specify this directly within your `build` stage using the pipeline command followed by the desired action and any relevant options such as directory or configuration file.

This approach enables you to modularize your workflows, making them more manageable and reusable across different projects or environments. Remember, when designing nested calls, to ensure that your pipelines are structured in a way that avoids circular dependencies to prevent infinite execution loops.

```yaml
build:
  - pipeline build -d some_subdir
  - pipeline build -d another_subdir -f build.yaml
test:
  - pipeline test -d some_subdir
  - pipeline test -d another_subdir -f test.yaml
deploy:
  - pipeline deploy -d some_subdir
  - pipeline deploy -d another_subdir -f deploy.yaml
undeploy:
  - pipeline undeploy -d some_subdir
  - pipeline undeploy -d another_subdir -f undeploy.yaml
```

### Environment Variables

The `pipeline_cli` tool can utilize environment variables if they are set before running the pipeline. This functionality is supported on both Unix-like systems and Windows.

#### Unix-like Systems

In Unix-like systems, environment variables can be set using the `export` command and are interpreted with the `$ENV` format. Here’s an example where the `TEST` variable is set to `hello` and then used to print `hello world`.

```yaml
build:
  - echo "$TEST world"
```

#### Windows

In Windows, environment variables can be set using the `set` command and are interpreted with the `%ENV%` format. Here’s an example where the TEST variable is set to hello and then used to print hello world.

```yaml
build:
  - echo "%TEST% world"
```

### YAML Variables

In `pipeline.yaml`, you can define variables and reusable content to simplify your configuration and avoid duplication. This section explains how to use generic YAML properties and anchors, and how to reference them within your pipeline configuration.

#### Defining Variables

Variables can be defined at the top of your `pipeline.yaml` file and referenced within any command using the syntax `${VARIABLE_NAME}`. This allows for dynamic command configurations based on the values of the variables.

```yaml
MY_VARIABLE: "hello world"

build: 
  - echo ${MY_VARIABLE}
```

### Reusing Commands with YAML Anchors and Aliases

YAML anchors (`&`) and aliases (`*`) allow you to define a block of commands once and reuse them elsewhere in your YAML file. This is useful for common setup, teardown, or utility operations that need to be repeated across different stages.

#### Defining Reusable Command Blocks

You can define a reusable block with an anchor (`&`), and then reference it with an alias (`*`) in one or more stages:

```yaml
custom_setup: &custom_setup
  - command1
  - command2

build: 
  - *custom_setup
  - build_command

deploy: 
  - *custom_setup
  - deploy_command
```

This setup defines a list of commands under `custom_setup` using an anchor named `custom_setup`. Both `build` and `deploy` stages then reuse these commands via the `*custom_setup` alias, followed by stage-specific commands.

Using variables, environment variables, and YAML anchors and aliases, you can create flexible and maintainable pipeline configurations that adapt to different needs and environments with minimal duplication.

## Contributing

Contributions are welcome! Please fork the repository and open a pull request with your changes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
