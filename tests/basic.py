import os
from unittest import TestCase

import yaml
from nl2dsl import NL2DSL
from dotenv import load_dotenv
import json
load_dotenv()


class TestBasic(TestCase):

    def test_simple_greet(self):
        instruction = "Greet the user"
        nl2dsl = NL2DSL(utterance=instruction)
        nl2dsl.nl2dsl()

        dsl = nl2dsl.dsl

        # print(json.dumps(dsl, indent=2))

        # Assertion statements
        assert isinstance(dsl, dict), "dsl should be a dictionary"

        # Check top-level keys
        assert "fsm_name" in dsl, "'fsm_name' key is missing"
        assert "config_vars" in dsl, "'config_vars' key is missing"
        assert "variables" in dsl, "'variables' key is missing"
        assert "dsl" in dsl, "'dsl' key is missing"

        # Check types of top-level values
        assert isinstance(
            dsl["fsm_name"], str), "'fsm_name' should be a string"
        assert isinstance(dsl["config_vars"],
                          list), "'config_vars' should be a list"
        assert isinstance(dsl["variables"],
                          list), "'variables' should be a list"
        assert isinstance(dsl["dsl"], list), "'dsl' should be a list"

        # Check structure of the items in the "dsl" list
        for task in dsl["dsl"]:
            assert isinstance(
                task, dict), "Each item in 'dsl' should be a dictionary"
            assert "task_type" in task, "'task_type' key is missing in a task"
            assert "name" in task, "'name' key is missing in a task"
            assert "goto" in task, "'goto' key is missing in a task"

            assert isinstance(task["task_type"],
                              str), "'task_type' should be a string"
            assert isinstance(task["name"], str), "'name' should be a string"
            # 'goto' can be None, so no type assertion for 'goto'

            if task["task_type"] == "print":
                assert "message" in task, "'message' key is missing in 'print' task"
                assert isinstance(
                    task["message"], str), "'message' should be a string in 'print' task"

        # Specific task checks (ensure the presence of start, print, and end tasks)
        start_task = next(
            (task for task in dsl["dsl"] if task["task_type"] == "start"), None)
        print_task = next(
            (task for task in dsl["dsl"] if task["task_type"] == "print"), None)
        end_task = next(
            (task for task in dsl["dsl"] if task["task_type"] == "end"), None)

        assert start_task is not None, "No 'start' task found"
        assert print_task is not None, "No 'print' task found"
        assert end_task is not None, "No 'end' task found"

        # Check 'goto' references
        assert start_task["goto"] == print_task['name'], "'start' task should go to 'greet_user_task'"
        assert print_task["goto"] == end_task['name'], "'print' task should go to 'end'"
        assert end_task["goto"] is None, "'end' task should have 'goto' as None"

    def test_plugin_call(self):
        with open(os.path.join(os.path.dirname(__file__), "plugins.yaml"), "r") as f:
            plugins = yaml.safe_load(f)
        instruction = "Tell the user we are going to help them book an appointment. For this we need to collect Rs 600. Collect the users mobile number and name. Then collect the amount using the payment plugin"
        nl2dsl = NL2DSL(utterance=instruction, plugins=plugins)
        nl2dsl.nl2dsl()

        dsl = nl2dsl.dsl

        print(json.dumps(dsl, indent=2))
