import abc
import argparse
import configparser
import shutil
from pathlib import Path


class CaseSensitiveDict(dict):
    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    def __getitem__(self, key):
        return super().__getitem__(key)

    def get(self, key):
        return super().get(key)

    # read_config function remains the same
    def read_config(file):
        config = configparser.ConfigParser(dict_type=CaseSensitiveDict)
        try:
            with open(file) as f:
                config.read_file(f)
        except Exception as e:
            print(f"Error reading config file: {e}")
            return None
        return config

    # is_program_in_path function remains the same
    def is_program_in_path(program_name):
        return shutil.which(program_name) is not None

    # build_program_args function remains the same
    def build_program_args(config):
        program_args = []
        label = ""
        if any(i for i in config if "Args" in i.title()):
            label = "Args"
            args_section = config[label]
            for key, value in args_section.items():
                program_args.append(f"--{key} {value}")
        else:
            args_section = {}

        nested_sections = [
            section for section in config.sections() if section.startswith(f"{label}.")
        ]

        for nested_section in nested_sections:
            nested_args_section = config[nested_section]
            nested_section_name = nested_section[5:]
            for key, value in nested_args_section.items():
                program_args.append(f"--{nested_section_name}:{key} {value}")

        label = ""
        if any(i for i in config if "Flags" in i.title()):
            label = "Flags"
            flags_section = config[label]
            for flag, value in flags_section.items():
                if value.lower() in ["true", "1", "enable"]:
                    program_args.append(f"--{flag}")

        nested_sections = [
            section for section in config.sections() if section.startswith(f"{label}.")
        ]

        for nested_section in nested_sections:
            nested_flags_section = config[nested_section]
            nested_section_name = nested_section[6:]
            for flag, value in nested_flags_section.items():
                if value.lower() in ["true", "1", "enable"]:
                    program_args.append(f"--{nested_section_name}:{flag}")
        return program_args


class Program(abc.ABC):
    def __init__(self):
        self.build_dir = Path("build")
        self.run_dir = Path("run")
        self.executable = Path("")

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def parse_arguments(self, args):
        pass

    def read_config(self, file):
        config = configparser.ConfigParser(dict_type=CaseSensitiveDict)
        try:
            with open(file) as f:
                config.read_file(f)
        except Exception as e:
            print(f"Error reading config file: {e}")
            return None
        return config

    def is_program_in_path(self, program_name):
        return shutil.which(program_name) is not None

    def build_program_args(self, config):
        program_args = []
        label = ""
        if any(i for i in config if "Args" in i.title()):
            label = "Args"
            args_section = config[label]
            for key, value in args_section.items():
                program_args.append(f"--{key} {value}")
        else:
            args_section = {}

        nested_sections = [
            section for section in config.sections() if section.startswith(f"{label}.")
        ]

        for nested_section in nested_sections:
            nested_args_section = config[nested_section]
            nested_section_name = nested_section[5:]
            for key, value in nested_args_section.items():
                program_args.append(f"--{nested_section_name}:{key} {value}")

        label = ""
        if any(i for i in config if "Flags" in i.title()):
            label = "Flags"
            flags_section = config[label]
            for flag, value in flags_section.items():
                if value.lower() in ["true", "1", "enable"]:
                    program_args.append(f"--{flag}")

        nested_sections = [
            section for section in config.sections() if section.startswith(f"{label}.")
        ]

        for nested_section in nested_sections:
            nested_flags_section = config[nested_section]
            nested_section_name = nested_section[6:]
            for flag, value in nested_flags_section.items():
                if value.lower() in ["true", "1", "enable"]:
                    program_args.append(f"--{nested_section_name}:{flag}")

        return program_args

    def launch_program(self, config):
        program_path = config.get("Program", "Path")
        program_args = self.build_program_args(config)
        try:
            result = []
            result.append(f"Program path: {program_path}")
            result.append(f"Type of program_path: {type(program_path)}")
            result.append("program arguments:")
            for arg in program_args:
                result.append(arg)
            print("\n".join(result))
        except Exception as e:
            print(f"Error launching program: {e}")


# Concrete implementation of Program
class Simulation(Program):
    def __init__(self, config):
        self.config = config

    def build(self):
        # Implement the build process
        pass

    def run(self):
        # Implement the run process
        pass


# Further specialization of Simulation
class MySimulation(Simulation):
    def build(self):
        # Customize build process if needed
        super().build()

    def run(self):
        # Customize run process if needed
        super().run()


class ConcreteProgram(Program):
    def setup(self):
        pass

    def parse_arguments(self, args):
        pass

    # Main execution block remains the same


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script to launch a program with custom arguments"
    )
    parser.add_argument(
        "config_file", type=argparse.FileType("r"), help="Path to the config file"
    )
    args = parser.parse_args()

    program = ConcreteProgram()
    config = program.read_config(args.config_file.name)
    program.launch_program(config)
