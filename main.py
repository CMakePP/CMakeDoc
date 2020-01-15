#!/usr/bin/python3

"""
Generate Sphinx-compatible RST documentation for CMake files.
Documentation is written in a special form of block comments,
denoted by the starting characters :code: `#[[[` and ending with the standard :code: `#]]`.

Usage: main.py [-h] [-o OUTPUT] [-r] file [file ...]

positional arguments:
  file                  CMake file to generate documentation for. If
                        directory, will generate documentation for all *.cmake
                        files (case-insensitive)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Directory to output generated RST to. If not specified
                        will print to standard output. Output files will have
                        the original filename with the cmake extension
                        replaced by .rst
  -r, --recursive       If specified, will generate documentation for all
                        subdirectories of specified directory recursively


:Author: Branden Butler
:License: Apache 2.0
"""

from cmakedoc.documenter import Documenter
import sys
import argparse
import os

def main(args = sys.argv[1:]):
    """
    CMake Documentation Generator program entry point.

    :param args: Array of strings containing program arguments, excluding program name. Same format as sys.argv[1:].
    """

    parser = argparse.ArgumentParser(description="""
Automatic documentation generator for CMake files. This program generates Sphinx-compatible RST documents, which are incompatible with standard docutils.
    """)
    parser.add_argument("file", nargs="+", help="CMake file to generate documentation for. If directory, will generate documentation for all *.cmake files (case-insensitive)")
    parser.add_argument("-o", "--output", help="Directory to output generated RST to. If not specified will print to standard output. Output files will have the original filename with the cmake extension replaced by .rst")
    parser.add_argument("-r", "--recursive", help="If specified, will generate documentation for all subdirectories of specified directory recursively", action="store_true")
    args = parser.parse_args(args)
    output_path = None
    if args.output is not None:
         output_path = os.path.abspath(args.output)
         print(f"Writing RST files to {output_path}")

    for input in args.file:
         #Process all files specified on command line
         document(input, output_path, args.recursive)


def document(file, output_path = None, recursive = False):
    """
    Handler for documenting each specified file or directory. Will locate all cmake files in directory
    (and subdirs if recursive is true) and write generated RST output to corresponding files output_path,
    or if None will output to standard output.

    :param file: String locating a file or directory to document.
    :param output_path: String pointing to the directory to place generated files, will output to stdout if None
    :param recursive: Whether to generate documentation for subdirectories or not.
    """
    files = []
    input_path = os.path.abspath(file)

    if os.path.isdir(input_path):
        #Walk dir and add cmake files to list
        for root, subdirs, filenames in os.walk(input_path):
             for file in filenames:
                  if "cmake" == file.split(".")[-1].lower():
                       files.append(os.path.join(root, file))
             if not recursive:
                  break
    elif os.path.isfile(input_path):
        files.append(input_path)
    else:
        print("File is a special file (socket, FIFO, device file) and is unsupported", file=sys.stderr)
        exit(1)

    for file in files:
         if os.path.isdir(input_path):
              header_name = os.path.relpath(file, input_path) #Path to file relative to input_path
         else:
              header_name = file
         documenter = Documenter(file, header_name)
         output_writer = documenter.process()
         if output_path != None: #Determine where to place generated RST file
              print(f"Writing for file {file}")
              if os.path.isdir(output_path):
                   output_filename = os.path.join(output_path, ".".join(os.path.basename(file).split(".")[:-1]) + ".rst")
                   if os.path.isdir(input_path):
                        subpath = os.path.relpath(file, input_path) #Path to file relative to input_path
                        output_filename = os.path.join(output_path, os.path.join(os.path.dirname(subpath), ".".join(os.path.basename(file).split(".")[:-1]) + ".rst"))
                   print(f"Writing RST file {output_filename}")
                   os.makedirs(os.path.dirname(output_filename), exist_ok=True) #Make sure we have all the directories created
                   output_writer.write_to_file(output_filename)
         else: #Output was not specified so print to screen
              print(output_writer)
              print()

if __name__ == "__main__":
     main()