import sys
import logging
import argparse
from stray_recipe_manager import logger as root_logger
from stray_recipe_manager.units import UnitHandler
from stray_recipe_manager.storage import get_storage, TOMLCoding
from stray_recipe_manager.formatter import UnitPreferences, get_writer


def print_recipe(args):
    unit_handler = UnitHandler()
    prefs = UnitPreferences(unit_handler)
    if args.prefs is not None:
        prefs.load_from_toml_file(args.prefs)

    loader = TOMLCoding(unit_handler)
    recipe = loader.load_recipe_from_toml_file(args.recipe_file)

    writer = get_writer(args.format)(prefs)
    writer.write_standalone(sys.stdout, recipe, scale_factor=args.scale)


def book_print(storage, args):
    recipe = storage.get_recipe(args.recipe_key)

    unit_handler = storage.get_unit_handler()

    prefs = UnitPreferences(unit_handler)
    if args.prefs is not None:
        prefs.load_from_toml_file(args.prefs)

    writer = get_writer(args.format)(prefs)
    writer.write_standalone(args.output, recipe, scale_factor=args.scale)


def book_dispatch(args):
    storage = get_storage(args.recipe_book)
    args.book_func(storage, args)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Utility to handle recipe books"
    )

    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Be verbose",
        action="store_const", dest="loglevel", const=logging.INFO,
    )

    main_subparsers = parser.add_subparsers()

    # Single file

    def create_print_parser(parser_set):
        print_recipe_parser = parser_set.add_parser(
            "print_recipe", description="Utility to nicely print recipe"
        )

        print_recipe_parser.add_argument(
            "--format",
            help="Output format",
            default="text/markdown",
        )

        print_recipe_parser.add_argument(
            "recipe_file", type=argparse.FileType("r"), help="File with recipe"
        )

        print_recipe_parser.add_argument(
            "--prefs", type=argparse.FileType("r"), help="Unit preferences"
        )

        print_recipe_parser.add_argument(
            "--scale",
            type=float,
            help="Factor to scale recipe by",
            default=1.0,
        )

        print_recipe_parser.set_defaults(func=print_recipe)

    create_print_parser(main_subparsers)

    # Recipe book utilites

    recipe_book_parser = main_subparsers.add_parser(
        "book", description="Commands for interacting with sets of recipies"
    )

    recipe_book_parser.add_argument(
        "recipe_book", help="Recipe book to work with"
    )

    recipe_book_parser.set_defaults(func=book_dispatch)

    book_subparsers = recipe_book_parser.add_subparsers()

    def recipe_book_print(parser_set):
        print_selected_recipe = parser_set.add_parser(
            "print", description="Print selected recipe from recipe book"
        )

        print_selected_recipe.add_argument(
            "--format",
            help="Output format",
            default="text/markdown",
        )

        print_selected_recipe.add_argument(
            "--scale",
            type=float,
            help="Factor to scale recipe by",
            default=1.0,
        )

        print_selected_recipe.add_argument(
            "--prefs", type=argparse.FileType("r"), help="Unit preferences"
        )

        print_selected_recipe.add_argument(
            "--output",
            "-o",
            default=sys.stdout,
            type=argparse.FileType("w"),
            help="Output File",
        )

        print_selected_recipe.add_argument(
            "recipe_key", help="Recipe to print"
        )

        print_selected_recipe.set_defaults(book_func=book_print)

    recipe_book_print(book_subparsers)

    return parser.parse_args(args)


def dispatch():
    try:
        parser = parse_args(sys.argv[1:])
        root_logger.setLevel(parser.loglevel)
        root_logger.addHandler(logging.StreamHandler(sys.stderr))
        parser.func(parser)
    except Exception as e:
        if parser is not None and parser.loglevel < logging.DEBUG:
            root_logger.error(repr(e))
        else:
            raise
