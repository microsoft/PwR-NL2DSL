from collections import defaultdict
import json
class Checker:
    def __init__(
        self,
        dsl,
        variables,
        config_variables=None
    ):
        self.errors = []
        self.dsl = dsl
        self.dsl_dict = {}
        self.defined_variables = {var['name'] for var in variables}
        self.config_variables = config_variables
        for task in dsl:
            self.dsl_dict[task["name"]] = task
        self.variables_dict = {}
        for variable in variables:
            self.variables_dict[variable["name"]] = variable

    def transition_checker(self, key, condition_key=None):
        if condition_key is None:
            condition_key = "transitions"

        value = self.dsl_dict[key]
        if not isinstance(value[condition_key], list):
            self.errors.append(f"{key} transitions is not a list")
        else:
            for transition in value[condition_key]:
                if not isinstance(transition, dict):
                    self.errors.append(f"{key} transition is not a dict")
                else:

                    if "condition" in transition:
                        if not isinstance(transition["condition"], str):
                            # how to check if the condition is valid python expression
                            self.errors.append(
                                f"{key} transition condition is not a string"
                            )
                    elif "code" in transition:
                        if not isinstance(transition["code"], str):
                            self.errors.append(f"{key} transition code is not a string")
                    else:
                        self.errors.append(f"{key} transition condition is missing")

                    if "goto" in transition:
                        if transition["goto"] is not None and transition["goto"] not in self.dsl_dict:
                            self.errors.append(
                                f"{key} next transition task {transition['goto']} does not exist"
                            )
                    else:
                        self.errors.append(f"{key} transition is missing")
        return self.errors

    def variable_checker(self):
        for key, value in self.variables_dict.items():
            if "type" in value:
                if value["type"] not in [
                    "int",
                    "str",
                    "float",
                    "bool",
                    "list",
                    "dict",
                    "enum",
                ]:
                    self.errors.append(f"{key} type is not valid")
            else:
                self.errors.append(f"{key} type is missing")
        self.dfs_check_variables()
        self.undeclared_variables()

    def checker(
        self,
    ):
        self.variable_checker()

        for key, value in self.dsl_dict.items():
            if value["task_type"] == "print":
                if "message" in value:
                    if not isinstance(value["message"], str):
                        self.errors.append(f"{key} message is not a string")
                else:
                    self.errors.append(f"{key} message is missing")

                if "goto" in value:
                    if isinstance(value["goto"], str):
                        if value["goto"] not in self.dsl_dict:
                            self.errors.append(
                                f"{key} next transition task {value['goto']} does not exist"
                            )
                else:
                    self.errors.append(f"{key} goto is missing")

            if value["task_type"] == "input":

                has_transition = False
                if "goto" in value:
                    if isinstance(value["goto"], str):
                        if value["goto"] not in self.dsl_dict:
                            self.errors.append(
                                f"{key} goto task {value['goto']} does not exist"
                            )
                        else:
                            has_transition = True

                if "error_goto" in value:
                    if isinstance(value["error_goto"], str):
                        if value["error_goto"] not in self.dsl_dict:
                            self.errors.append(
                                f"{key} error_goto task {value['error_goto']} does not exist"
                            )
                        else:
                            has_transition = True

                if not has_transition:
                    self.errors.append(f"{key} error_goto is missing")

                if "options" in value:
                    if not isinstance(value["options"], list):
                        self.errors.append(f"{key} options is not a list")
                    else:
                        for option in value["options"]:
                            if not isinstance(option, str):
                                self.errors.append(f"{key} option is not a string")


            if value["task_type"] == "plugin":
                if "plugin" in value:
                    if not isinstance(value["plugin"], dict):
                        self.errors.append(f"{key} plugin is not a dict")
                    # how to check if the plugin exists
                    # how to check if the plugin has the correct input and output variables

                else:
                    self.errors.append(f"{key} plugin is missing")

                if "message" in value:
                    if not isinstance(value["message"], str):
                        self.errors.append(f"{key} message is not a string")

                if "transitions" in value:
                    self.transition_checker(key)
                else:
                    self.errors.append(f"{key} transitions is missing")

            if value["task_type"] == "condition":
                if "read_variables" in value:
                    if not isinstance(value["read_variables"], list):
                        self.errors.append(f"{key} read_variables is not a list")
                    else:
                        for read_variable in value["read_variables"]:
                            if read_variable not in self.variables_dict:
                                self.errors.append(
                                    f"{key} read_variable {read_variable} does not exist in variables"
                                )
                else:
                    self.errors.append(f"{key} read_variables is missing")

                if "conditions" in value:
                    self.transition_checker(key, "conditions")
                else:
                    self.errors.append(f"{key} transitions is missing")

        return self.errors


if __name__ == "__main__":
    with open("bandhu/step1/gold.json") as f:
        data = json.load(f)
    tasks = data["dsl"]
    config_var_names = [var["name"] for var in data["config_variables"]]
    checker = Checker(tasks, data["variables"], data["config_variables"])
    result = checker.checker()
    print(result)