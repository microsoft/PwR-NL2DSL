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

        # Assertion statements
        assert isinstance(dsl, dict), "dsl should be a dictionary"

        # Check top-level keys
        assert "fsm_name" in dsl, "'fsm_name' key is missing"
        assert "config_vars" in dsl, "'config_vars' key is missing"
        assert "variables" in dsl, "'variables' key is missing"
        assert "dsl" in dsl, "'dsl' key is missing"

        # Check types of top-level values
        assert isinstance(dsl["fsm_name"], str), "'fsm_name' should be a string"
        assert isinstance(dsl["config_vars"], list), "'config_vars' should be a list"
        assert isinstance(dsl["variables"], list), "'variables' should be a list"
        assert isinstance(dsl["dsl"], list), "'dsl' should be a list"

        # Check structure of the items in the "config_vars" list
        for var in dsl["config_vars"]:
            assert isinstance(var, dict), "Each item in 'config_vars' should be a dictionary"
            assert "name" in var, "'name' key is missing in a config_var"
            assert "type" in var, "'type' key is missing in a config_var"
            assert "description" in var, "'description' key is missing in a config_var"
            assert "plugins" in var, "'plugins' key is missing in a config_var"

            assert isinstance(var["name"], str), "'name' should be a string in config_var"
            assert isinstance(var["type"], str), "'type' should be a string in config_var"
            assert isinstance(var["description"], str), "'description' should be a string in config_var"
            assert isinstance(var["plugins"], list), "'plugins' should be a list in config_var"

        # Check structure of the items in the "variables" list
        for var in dsl["variables"]:
            assert isinstance(var, dict), "Each item in 'variables' should be a dictionary"
            assert "name" in var, "'name' key is missing in a variable"
            assert "type" in var, "'type' key is missing in a variable"
            assert "validation" in var, "'validation' key is missing in a variable"
            assert "description" in var, "'description' key is missing in a variable"

            assert isinstance(var["name"], str), "'name' should be a string in variable"
            assert isinstance(var["type"], str), "'type' should be a string in variable"
            assert isinstance(var["validation"], str), "'validation' should be a string in variable"
            assert isinstance(var["description"], str), "'description' should be a string in variable"

        # Check structure of the items in the "dsl" list
        for task in dsl["dsl"]:
            assert isinstance(task, dict), "Each item in 'dsl' should be a dictionary"
            assert "task_type" in task, "'task_type' key is missing in a task"
            assert "name" in task, "'name' key is missing in a task"
            assert "goto" in task, "'goto' key is missing in a task"

            assert isinstance(task["task_type"], str), "'task_type' should be a string in task"
            assert isinstance(task["name"], str), "'name' should be a string in task"
            # 'goto' can be None, so no type assertion for 'goto'

            if task["task_type"] == "print":
                assert "message" in task, "'message' key is missing in 'print' task"
                assert isinstance(task["message"], str), "'message' should be a string in 'print' task"

            if task["task_type"] == "input":
                assert "message" in task, "'message' key is missing in 'input' task"
                assert "write_variable" in task, "'write_variable' key is missing in 'input' task"
                assert "datatype" in task, "'datatype' key is missing in 'input' task"
                assert "error_goto" in task, "'error_goto' key is missing in 'input' task"

                assert isinstance(task["message"], str), "'message' should be a string in 'input' task"
                assert isinstance(task["write_variable"], str), "'write_variable' should be a string in 'input' task"
                assert isinstance(task["datatype"], str), "'datatype' should be a string in 'input' task"
                assert isinstance(task["error_goto"], str), "'error_goto' should be a string in 'input' task"

            if task["task_type"] == "plugin":
                assert "read_variables" in task, "'read_variables' key is missing in 'plugin' task"
                assert "environment_variables" in task, "'environment_variables' key is missing in 'plugin' task"
                assert "write_variables" in task, "'write_variables' key is missing in 'plugin' task"
                assert "plugin" in task, "'plugin' key is missing in 'plugin' task"
                assert "description" in task, "'description' key is missing in 'plugin' task"
                assert "transitions" in task, "'transitions' key is missing in 'plugin' task"

                assert isinstance(task["read_variables"], list), "'read_variables' should be a list in 'plugin' task"
                assert isinstance(task["environment_variables"], list), "'environment_variables' should be a list in 'plugin' task"
                assert isinstance(task["write_variables"], list), "'write_variables' should be a list in 'plugin' task"
                assert isinstance(task["plugin"], dict), "'plugin' should be a dictionary in 'plugin' task"
                assert isinstance(task["description"], str), "'description' should be a string in 'plugin' task"
                assert isinstance(task["transitions"], list), "'transitions' should be a list in 'plugin' task"

                # Check structure of the plugin
                plugin = task["plugin"]
                assert "name" in plugin, "'name' key is missing in 'plugin'"
                assert "inputs" in plugin, "'inputs' key is missing in 'plugin'"
                assert "outputs" in plugin, "'outputs' key is missing in 'plugin'"

                assert isinstance(plugin["name"], str), "'name' should be a string in 'plugin'"
                assert isinstance(plugin["inputs"], dict), "'inputs' should be a dictionary in 'plugin'"
                assert isinstance(plugin["outputs"], dict), "'outputs' should be a dictionary in 'plugin'"

                # Check structure of the transitions
                for transition in task["transitions"]:
                    assert isinstance(transition, dict), "Each item in 'transitions' should be a dictionary"
                    assert "code" in transition, "'code' key is missing in a transition"
                    assert "goto" in transition, "'goto' key is missing in a transition"
                    assert "description" in transition, "'description' key is missing in a transition"

                    assert isinstance(transition["code"], str), "'code' should be a string in transition"
                    assert isinstance(transition["goto"], (str, type(None))), "'goto' should be a string or None in transition"
                    assert isinstance(transition["description"], str), "'description' should be a string in transition"

        # Specific task checks (ensure the presence of start, print, input, plugin, and end tasks)
        start_task = next((task for task in dsl["dsl"] if task["task_type"] == "start"), None)
        print_task = next((task for task in dsl["dsl"] if task["task_type"] == "print"), None)
        input_tasks = [task for task in dsl["dsl"] if task["task_type"] == "input"]
        plugin_task = next((task for task in dsl["dsl"] if task["task_type"] == "plugin"), None)
        end_task = next((task for task in dsl["dsl"] if task["task_type"] == "end"), None)

        assert start_task is not None, "No 'start' task found"
        assert print_task is not None, "No 'print' task found"
        assert len(input_tasks) > 0, "No 'input' tasks found"
        assert plugin_task is not None, "No 'plugin' task found"
        assert end_task is not None, "No 'end' task found"

