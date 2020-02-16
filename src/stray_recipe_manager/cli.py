import sys
import argparse
from stray_recipe_manager.units import UnitHandler
from stray_recipe_manager.storage import TOMLCoding
from stray_recipe_manager.formatter import MarkdownWriter, UnitPreferences


def print_recipe(args):
    unit_handler = UnitHandler()
    prefs = UnitPreferences(unit_handler)
    if args.prefs is not None:
        prefs.load_from_toml_file(args.prefs)

    loader = TOMLCoding(unit_handler)
    recipe = loader.load_recipe_from_toml_file(args.recipe_file)

    writer = MarkdownWriter(prefs)
    writer.set_scale_factor(args.scale)
    writer.write_recipe(sys.stdout, recipe)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Utility to handle recipe books"
    )

    subparsers = parser.add_subparsers()

    print_recipe_parser = subparsers.add_parser(
        "print", description="Utility to nicely print recipe"
    )

    print_recipe_parser.add_argument(
        "recipe_file", type=argparse.FileType("r"), help="File with recipe"
    )

    print_recipe_parser.add_argument(
        "--prefs", type=argparse.FileType("r"), help="Unit preferences"
    )

    print_recipe_parser.add_argument(
        "--scale", type=float, help="Factor to scale recipe by", default=1.0
    )

    print_recipe_parser.set_defaults(func=print_recipe)

    return parser.parse_args(args)


def dispatch():
    parser = parse_args(sys.argv[1:])
    parser.func(parser)
