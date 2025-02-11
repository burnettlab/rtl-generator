"""
Handle all things related to arguments
"""
import argparse
import builtins
from pathlib import Path
from typing import List

import yaml

from .heirarchy import get_subdirs
from .format import get_pretty_name


def get_arguments(existing_vars: dict, arglist: List[str]) -> None:
    '''
    Get the value of an argument if it exists
    '''
    args = existing_vars['args']
    used_args = existing_vars['used_args']
    for arg in arglist:
        if hasattr(args, arg):
            existing_vars[arg] = getattr(args, arg)
            used_args.add(arg)


def add_args(rtl_name: str, pretty_rtl_name: str, proj_path: Path, parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
    '''
    Add arguments to the parser
    '''
    with open(Path(proj_path, "options.yml"), "r") as f:
        args = yaml.safe_load(f)

    if parser is None:
        parser = argparse.ArgumentParser(description=f"Generate {pretty_rtl_name} RTL code")

    for arg, arg_info in args.items():
        if 'type' in arg_info:
            arg_info['type'] = getattr(builtins, arg_info['type'])
        try:
            parser.add_argument(f"--{arg}", **arg_info)
        except argparse.ArgumentError:
            pass

    parser.add_argument(f"--{rtl_name}_output", type=str, help=f"{pretty_rtl_name} Output file path", default=str(Path(proj_path, f"{rtl_name}.sv")))

    available_submods = get_subdirs(proj_path)
    while available_submods:
        submod_path = available_submods.pop()
        submod_name = submod_path.name
        pretty_submod_name = get_pretty_name(submod_name)
        parser.add_argument(f"--{submod_name}_output", type=str, help=f"{pretty_submod_name} Output file path", default=str(Path(submod_path, f"{submod_name}.sv")))
        available_submods.extend(get_subdirs(submod_path))
    
    return parser