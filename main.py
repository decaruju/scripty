#! python3
import sys
import os
import yaml
from dataclasses import dataclass

@dataclass
class Command:
    command: str
    options: dict

    def run(self):
        return self.command

def prefix_command(command, prefix):
    return Command(f'{prefix} {command.command}', command.options)

def suffix_command(command, suffix):
    return Command(f'{command.command} {suffix}', command.options)

@dataclass
class Program:
    commands: list

    @staticmethod
    def from_yml(config_yml):
        config = yaml.load(config_yml, yaml.Loader)
        commands = { command_name: Command(command["command"], command["options"]) for command_name, command in config['commands'].items() }
        for prefix_name, commands_to_prefix in config.get("config", {}).get("prefix", {}).items():
            prefix = config["prefixes"][prefix_name]
            for command_to_prefix in commands_to_prefix:
                if command_to_prefix == "$all":
                    commands = { command_name: prefix_command(command, prefix) for command_name, command in commands.items() }
                else:
                    commands[command_to_prefix] = prefix_command(commands[command_to_prefix], prefix)
        for suffix_name, commands_to_suffix in config.get("config", {}).get("suffix", {}).items():
            suffix = config["suffixes"][suffix_name]
            for command_to_suffix in commands_to_suffix:
                if command_to_suffix == "$all":
                    commands = { command_name: suffix_command(command, suffix) for command_name, command in commands.items() }
                else:
                    commands[command_to_suffix] = suffix_command(commands[command_to_suffix], suffix)

        return Program(commands)

    def run(self, command_name, options):
        command = self.commands[command_name]
        for option in options:
            command = suffix_command(command, command.options[option])


        print(f"running command {command_name} parsed as {command.command}")
        os.system(command.command)

if __name__ == "__main__":
    program = Program.from_yml(open("scripty.yml"))
    program.run(sys.argv[1], sys.argv[2:])
