import argparse
import os
import re
import sys
from pathlib import Path
from importlib import import_module
from rtl_generator import rtl_generator, replace_includes, add_args


def main(rtl_name: str, pretty_rtl_name: str, proj_path: str) -> None:
    '''
    Main function to generate RTL code

    Constructs command line arguments, parses them, and generates the RTL code
    '''
    # Construct and parse command line arguments
    args = add_args(rtl_name, pretty_rtl_name, proj_path).parse_args()

    # Generate the RTL code using given arguments
    import_module(f"gen_{rtl_name}")
    calling_module = sys.modules[f"gen_{rtl_name}"]
    generated_rtl = rtl_generator(rtl_name, pretty_rtl_name, args, vars(calling_module)) + "\n"
    
    submod_rtls = {}
    available_submods = [os.path.join(proj_path, d) for d in os.listdir() if os.path.isdir(d) and not (d in ['sim_build', 'models'] or re.search(r"__$", d))]
    while available_submods:
        submod_path = available_submods.pop()
        name = submod_path.split(os.sep)[-1]
        pretty_name = " ".join(name.split("_")).title()
        submod = sys.modules[f"{name}.gen_{name}"]

        os.chdir(submod_path)
        submod_rtls[name] = submod.rtl_generator(name, pretty_name, args, vars(submod), include_output_filename=not args.replace_includes)
        if not args.replace_includes:
            with open(getattr(args, f"{name}_output"), "w") as f:
                f.write(submod_rtls[name])
                print(f"Generated RTL for {pretty_name} saved to {f.name}")
        os.chdir(proj_path)

        available_submods.extend([os.path.join(submod_path, d) for d in os.listdir(submod_path) if not (d == 'sim_build' or re.search(r"__$", d)) and os.path.isdir(os.path.join(submod_path, d))])

    if args.replace_includes:
        generated_rtl = replace_includes(pretty_rtl_name, generated_rtl, submod_rtls)

    with open(os.path.join(proj_path, getattr(args, f"{rtl_name}_output")), "w") as f:
        f.write(generated_rtl)
        print(f"Generated RTL saved to {f.name}")

    print(f"Finished generating RTL for {pretty_rtl_name}")


if __name__ == '__main__':
    main(__file__.split(os.sep)[-1].replace(".py", "").replace("gen_", ""), " ".join(__file__.split(os.sep)[-1].replace(".py", "").replace("gen_", "").split("_")).title(), Path(__file__).resolve().parent)