"""
Handle the RTL heirarchy
"""
import os
import re
from pathlib import Path
from typing import Dict, List


def replace_includes(pretty_rtl_name: str, generated_rtl: str, submod_rtls: Dict[str, str]) -> str:
    """
    Recursively replaces include statements in the generated RTL code with the contents of the included file.

    If an included file exists in generated RTL, includes generated RTL for that file.
    Otherwise, includes the contents of the existing file.
    """
    while True:
        match = re.search(r"`include \"(.+?)\"", generated_rtl)
        if match is None:
            break

        start, end = match.span()
        start = generated_rtl.rfind('\n', 0, start)

        include_file = match.group(1)
        submod_name = include_file.split('/')[-1].replace('.sv', '')

        if f"{submod_name}.gen_{submod_name}" in submod_rtls:
            include_rtl = submod_rtls[f"{submod_name}.gen_{submod_name}"]
        else:
            with open(include_file, "r") as f:
                include_rtl = f.read()
        
            pdir = os.getcwd()
            os.chdir(Path(include_file).parent)
            include_rtl = replace_includes(pretty_rtl_name, include_rtl, submod_rtls)
            os.chdir(pdir)
        
        generated_rtl = generated_rtl[:start] + generated_rtl[end:] + f"\n{include_rtl}"
        print(f"Included {submod_name} in {pretty_rtl_name}")

    return generated_rtl


def get_subdirs(module_path: str | Path) -> List[Path]:
    paths = []
    for d in filter(lambda d: Path(module_path, d).is_dir(), os.listdir(module_path)):
        if d in ['sim_build', 'models']:
            continue
        if re.search(r"__$", d) or re.search(r"^\.", d):
            continue

        paths.append(Path(module_path, d))

    return paths


# def generator_generator(folder: str, folder_path: Path, rtl_ext: str) -> None:
#     """
#     Discover and generate new submodule generators
#     """
#     generator_file_name = f"gen_{folder}.py"

#     # Check if generator already exists
#     if os.path.exists(os.path.join(folder_path, generator_file_name)):
#         return
        
#     parent_module = f"gen_{'ble_cdr' if Path(folder_path).resolve().parent == top_path else str(Path(folder_path).parent).split(os.sep)[-1]}"
#     generator_template = [
#         "#!/usr/bin/env python3",
#         "f'''",
#         "Generate {\" \".join(\"#{(folder)}\".split(\"_\")).title()} RTL code",
#         "'''",
#         "",
#         "# Necessary imports, path setup, and global variables",
#         "from pathlib import Path",
#         "import sys",
#         "import os",
#         "",
#         "sys.path.append(str(Path(__file__).resolve().parent))",
#         "sys.path.append(str(Path(__file__).resolve().parent.parent))",
#         f"from {parent_module} import *",
#         "",
#         "",
#         "# User-defined imports, functions, and globals",
#         "",
#         "",
#         "if __name__ == '__main__':",
#         "    main(__file__.split(os.sep)[-1].replace(\".py\", \"\").replace(\"gen_\", \"\"), \" \".join(__file__.split(os.sep)[-1].replace(\".py\", \"\").replace(\"gen_\", \"\").split(\"_\")).title(), Path(__file__).resolve().parent)",
#         ""
#     ]
    
#     print(f"Creating new submodule generator for {folder}...")
#     if not os.path.exists(os.path.join(folder_path, f"template_{folder}.{rtl_ext}")): 
#         if os.path.exists(os.path.join(folder_path, f"{folder}.{rtl_ext}")):
#             print(f"Detected {folder}.{rtl_ext}. Copying to template_{folder}.{rtl_ext}...")
#             with open(os.path.join(folder_path, f"{folder}.{rtl_ext}"), "r") as f:
#                 template = f.read()

#             with open(os.path.join(folder_path, f"template_{folder}.{rtl_ext}"), "w+") as f:
#                 f.write(template)
#         else:
#             print(f"Creating template_{folder}.{rtl_ext}...")
#             with open(os.path.join(folder_path, f"template_{folder}.{rtl_ext}"), "w+") as f:
#                 f.write("")
    
#     print(f"Creating {generator_file_name}...")
#     with open(os.path.join(folder_path, generator_file_name), "w+") as f:
#         f.write(fill_in_template("\n".join(generator_template), None, locals()))

#     print(f"Finished creating submodule generator for {folder}")
