import yaml
import subprocess
import argparse
import sys
import os
import uuid
import time

def load_pipeline_config(directory=".", filename="pipeline.yaml"):
    filepath = os.path.join(directory, filename)
    try:
        with open(filepath, 'r') as stream:
            config = yaml.safe_load(stream)
            if config is None:
                print("\033[93m\nWarning: Empty or invalid YAML file.\033[0m")
                return {}
            return config
    except yaml.YAMLError as exc:
        print(f"\033[91m\nError reading YAML file: {exc}\n\033[0m")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\033[91m\nError: The file {filepath} was not found.\n\033[0m")
        sys.exit(1)

def flatten(lst):
    for item in lst:
        if isinstance(item, list):
            # If the item is a list, yield from its flattened form
            yield from flatten(item)
        else:
            # Otherwise, yield the item itself
            yield item

def run_commands(stage_commands, variables, working_directory="."):
    original_directory = os.getcwd()
    try:
        os.chdir(working_directory)
        # Flatten the stage_commands to handle nested lists
        for command_template in flatten(stage_commands):
            command = command_template
            # Substitute variables
            for key, value in variables.items():
                command = command.replace('${' + key + '}', str(value))  # Ensure value is a string
            
            print(f"\033[36m\nExecuting command: \033[33m{command}\033[0m")
            
            process = subprocess.run(command, shell=True, text=True)
            if process.returncode != 0:
                print(f"\033[91m\nError: Command '{command}' exited with return code {process.returncode}\n\033[0m")
                sys.exit(process.returncode)
    finally:
        os.chdir(original_directory)

def set_print_header():
    # Generate a unique PIPELINE_ID using UUID
    pipeline_id = str(uuid.uuid4())
    os.environ['PIPELINE_ID'] = pipeline_id

    # Example: setting a timestamp-based version for the release
    release_version = time.strftime("%Y.%m.%d-%H%M%S")
    os.environ['PIPELINE_RELEASE_VERSION'] = release_version

    # Calculate padding for centered text
    line_length = 60
    title = "Pipeline CLI"
    padding_width = (line_length - len(title)) // 2
    centered_title = " " * padding_width + title + " " * padding_width

    # Adjust for odd lengths to ensure the title is centered
    if len(centered_title) < line_length:
        centered_title += " "

    # Print header with centered title
    print("-" * line_length)
    print(centered_title)
    print("-" * line_length)
    print(f"\033[36mPIPELINE_ID set to:\033[0m \033[33m{pipeline_id}\033[0m")
    print(f"\033[36mPIPELINE_RELEASE_VERSION set to:\033[0m \033[33m{release_version}\033[0m")
    print("-" * line_length)

def main():
    # Determine if this is the top-level call based on a special flag
    top_level_call = 'PIPELINE_CLI_TOP_LEVEL' not in os.environ
    
    # If this is the top-level call, set up environment variables and print the header
    if top_level_call:
        # Indicate that this and any nested calls are not the top-level call
        os.environ['PIPELINE_CLI_TOP_LEVEL'] = 'false'
        set_print_header()    
    
    # Setup arguments for parsing from executable calls
    parser = argparse.ArgumentParser(description='Pipeline CLI')
    parser.add_argument('action', nargs='+', choices=['setup', 'test', 'build', 'deploy', 'undeploy'], help='Action(s) to perform')
    parser.add_argument('-d', '--directory', default='.', help='Specify the directory where the pipeline.yaml is located. Defaults to the current directory.')
    parser.add_argument('-f', '--file', default='pipeline.yaml', help='Specify the pipeline configuration file name. Defaults to "pipeline.yaml".')
    parser.add_argument('--rollback', action='store_true', help='Execute the rollback stage for the specified action(s).')
    
    # Parse arguments given to cli
    args = parser.parse_args()

    for action in args.action:
        # Determine if the rollback flag is set and construct the stage name accordingly
        stage_name = f"{action}.rollback" if args.rollback else action
        
        if top_level_call:
            # Print stage execution info, taking into account the rollback flag
            action_display_name = f"{action} (rollback)" if args.rollback else action
            print(f"\033[36m\nExecuting stage: \033[95m{action_display_name}\033[0m")
        
        config = load_pipeline_config(directory=args.directory, filename=args.file)

        # Use the modified stage name to get the appropriate commands from the config
        variables = {k: v for k, v in config.items() if not k.endswith('.rollback')}
        stage_commands = config.get(stage_name, [])

        run_commands(stage_commands, variables, working_directory=args.directory)

    # Clean up flags and print completion information
    if top_level_call:
        del os.environ['PIPELINE_CLI_TOP_LEVEL']
        print("\033[95m\nPipeline execution completed.\n\033[0m")

if __name__ == "__main__":
    main()