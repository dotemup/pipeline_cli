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

def run_commands(stage_commands, variables, working_directory="."):
    original_directory = os.getcwd()
    try:
        os.chdir(working_directory)
        for command_template in stage_commands:
            command = command_template
            # Substitute variables
            for key, value in variables.items():
                command = command.replace('${' + key + '}', value)
            
            # Print the command being executed
            print(f"\033[36m\nExecuting command: \033[33m{command}\033[0m")  
            
            # Execute the command, directing output directly to the console
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
    os.environ['RELEASE_VERSION'] = release_version

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
    print(f"\033[36mRELEASE_VERSION set to:\033[0m \033[33m{release_version}\033[0m")
    print("-" * line_length)

def main():
    # Determine if this is the top-level call based on a special flag
    top_level_call = 'PIPELINE_CLI_TOP_LEVEL' not in os.environ
    
    parser = argparse.ArgumentParser(description='Pipeline CLI')
    parser.add_argument('action', nargs='+', choices=['build', 'test', 'deploy', 'undeploy'], help='Action(s) to perform')
    parser.add_argument('-d', '--directory', default='.', help='Specify the directory where the pipeline.yaml is located. Defaults to the current directory.')
    parser.add_argument('-f', '--file', default='pipeline.yaml', help='Specify the pipeline configuration file name. Defaults to "pipeline.yaml".')
    
    args = parser.parse_args()

    # If this is the top-level call, set up environment variables and print the header
    if top_level_call:
        # Indicate that this and any nested calls are not the top-level call
        os.environ['PIPELINE_CLI_TOP_LEVEL'] = 'false'
        set_print_header()    

    for action in args.action:        
        config = load_pipeline_config(directory=args.directory, filename=args.file)

        # Separate variables from action stages
        variables = {k: v for k, v in config.items() if k not in ['build', 'test', 'deploy', 'undeploy']}
        stage_commands = config.get(action, [])

        run_commands(stage_commands, variables, working_directory=args.directory)

    if top_level_call:
        del os.environ['PIPELINE_CLI_TOP_LEVEL']
        print("\033[95m\nPipeline execution completed.\n\033[0m")

if __name__ == "__main__":
    main()