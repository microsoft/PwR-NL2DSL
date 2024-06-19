from ast import arg
import os
import json
import yaml
from termcolor import cprint
from nl2dsl import NL2DSL
from argparse import ArgumentParser

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--instruction",
        type=str,
        help="path to user instruction file, should be txt file",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--dsl",
        type=str,
        help="path to dsl file, should be json file",
        default=None,
        required=False,
    )
    parser.add_argument(
        "-p",
        "--plugins",
        type=str,
        help="path to plugins file, should be yaml file",
        default=None,
        required=False,
    )
    parser.add_argument(
        "-debug",
        "--debug",
        help="debug mode",
        action="store_true",
        required=False,
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="directory to save the output files, works only if debug mode is on",
        default=None,
        required=False,
    )

    args = parser.parse_args()

    dsl = None

    if args.instruction:
        if os.path.exists(args.instruction):
            with open(args.instruction, "r") as f:
                instruction = f.read()
        else:
            instruction = args.instruction

    if args.dsl:
        with open(args.dsl, "r") as f:
            dsl = json.load(f)
    else:
        dsl = {
            "variables": [],
            "config_vars": [],
            "dsl": [
                {
                    "task_type": "start",
                    "name": "start",
                    "goto": "end",
                },
                {
                    "task_type": "end",
                    "name": "end",
                    "goto": None,
                },
            ],
            "fsm_name": "unnamed_fsm",
        }

    if args.plugins:
        try:
            with open(args.plugins, "r") as f:
                plugins = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError("Plugins file not found")
    else:
        plugins = {}

    nl2dsl = NL2DSL(instruction, plugins, dsl, debug=args.debug)
    dsl = nl2dsl.nl2dsl()
    plan = nl2dsl.plan

    if args.debug and args.output:
        if not os.path.exists(args.output):
            os.makedirs(args.output)

        with open(f"{args.output}/plan.json", "w") as f:
            f.write(json.dumps(plan, indent=4))

        with open(f"{args.output}/dsl.json", "w") as f:
            f.write(json.dumps(dsl, indent=4))
    cprint(f"Final DSL:\n{json.dumps(dsl, indent=4)}", "light_cyan")
