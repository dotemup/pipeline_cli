import yaml
import subprocess
import sys
import os
import argparse

def load_pipeline_config(directory=".", filename="pipeline.yaml"):
    filepath = os.path.join(directory, filename)
    try:
        with open(filepath, 'r') as stream:
            config = yaml.safe_load(stream)
            if config is None:
                print("Warning: Empty or invalid YAML file.")
                return {}
            return config
    except yaml.YAMLError as exc:
        print(f"Error reading YAML file: {exc}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: The file {filepath} was not found.")
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
            print(f"Executing command: {command}")  
            
            # Execute the command, directing output directly to the console
            process = subprocess.run(command, shell=True, text=True)
            if process.returncode != 0:
                print(f"Error: Command '{command}' exited with return code {process.returncode}")
                sys.exit(process.returncode)
    finally:
        os.chdir(original_directory)

def main():
    parser = argparse.ArgumentParser(description='Pipeline CLI')
    parser.add_argument('action', nargs='+', choices=['build', 'test', 'deploy', 'undeploy'], help='Action(s) to perform')
    parser.add_argument('-d', '--directory', default='.', help='Specify the directory where the pipeline.yaml is located. Defaults to the current directory.')
    parser.add_argument('-f', '--file', default='pipeline.yaml', help='Specify the pipeline configuration file name. Defaults to "pipeline.yaml".')
    
    args = parser.parse_args()
        
    for action in args.action:        
        config = load_pipeline_config(directory=args.directory, filename=args.file)

        # Separate variables from action stages
        variables = {k: v for k, v in config.items() if k not in ['build', 'test', 'deploy', 'undeploy']}
        stage_commands = config.get(action, [])

        run_commands(stage_commands, variables, working_directory=args.directory)

if __name__ == "__main__":
    main()