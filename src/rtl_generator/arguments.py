"""
Handle all things related to arguments
"""
import argparse
import builtins
import os
import re
import sys
from importlib import import_module
from pathlib import Path
from typing import List

import yaml


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

    parser.add_argument(f"--{rtl_name}_output", type=str, help=f"{pretty_rtl_name} Output file path", default=f"{rtl_name}.sv")

    for folder in [d for d in os.listdir() if os.path.isdir(d) and not (d in ['sim_build', 'models'] or re.search(r"__$", d))]:
        folder_path = os.path.join(proj_path, folder)
        # generator_generator(folder, folder_path, "sv")

        os.chdir(folder_path)
        submod_name = f"{folder}.gen_{folder}"
        import_module(submod_name, submod_name.split('.')[-1])
        sub_mod = sys.modules[submod_name]
        sub_mod.add_args(folder, " ".join(folder.split("_")).title(), folder_path, parser)
        os.chdir(proj_path)
    
    return parser