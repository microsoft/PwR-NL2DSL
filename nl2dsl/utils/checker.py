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

    def transition_checker(self, key):
        value = self.dsl_dict[key]
        if not isinstance(value["transitions"], list):
            self.errors.append(f"{key} transitions is not a list")
        else:
            for transition in value["transitions"]:
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
                        if transition["goto"] not in self.dsl_dict:
                            self.errors.append(
                                f"{key} next transition task {transition['goto']} does not exist"
                            )
                    else:
                        self.errors.append(f"{key} transition is missing")
        return self.errors

    def transition_loop_checker(self, key):
        value = self.dsl_dict[key]
        if "goto" in value:
            if value["goto"] == key:
                self.errors.append(f"{key} transitions to itself")

        if "error_goto" in value:
            if value["error_goto"] == key:
                self.errors.append(f"Upon error in {key} task it transitions to itself")
            if value["error_goto"] in self.dsl_dict:
                error_task = self.dsl_dict[value["error_goto"]]
                if error_task["task_type"] == "display":
                    # if task_type is logic, then check for goto and error_goto
                    # can we make sure that other task type will not have loop??
                    if "goto" in error_task:
                        if error_task["goto"] == key:
                            # self.errors.append(
                            #     f"{key} task error transition to {value['error_goto']} to itself"
                            # )
                            pass
            if "transitions" in value:
                for transition in value["transitions"]:
                    if transition["goto"] == key:
                        self.errors.append(
                            f"{key} transitions to itself if error code {transition.get('code')} "
                        )

            if "conditions" in value:
                for condition in value["conditions"]:
                    if condition["goto"] == key:
                        self.errors.append(
                            f"{key} transitions to itself in condition {condition.get('condition')}"
                        )       
    
    def build_graph(self,):
        graph = defaultdict(list)
        for task in self.dsl:
            if 'goto' in task:
                graph[task['name']].append(task['goto'])
            if 'error_goto' in task:
                graph[task['name']].append(task['error_goto'])
            if 'transitions' in task:
                for transition in task['transitions']:
                    graph[task['name']].append(transition['goto'])
        return graph
    
    def dfs_check_variables(self, start:str=None):
        graph = self.build_graph()
        visited = set()
        if self.config_variables:
            config_var_names = [var["name"] for var in self.config_variables]
        else:
            config_var_names = []
        written_variables = set(config_var_names)
        if start is None:
            start = self.dsl[0]['name']
        stack = [start]

        while stack:
            task_name = stack.pop()
            if task_name and task_name not in visited:
                visited.add(task_name)
                task = self.dsl_dict[task_name]
                if task['task_type'] == 'input':
                    written_variables.add(task['write_variable'])
                if task['task_type'] == 'plugin':
                    for var in task['plugin']['outputs'].values():
                        written_variables.add(var)
                    
                    for var in task['plugin']['inputs'].values():
                        if var not in written_variables:
                            self.errors.append(f"Variable {var} used in task {task_name} not found in dsl.")
                if task['task_type'] == 'operation':
                    written_variables.add(task['write_variable'])
                if 'read_variables' in task:
                    for var in task['read_variables']:
                        if var not in written_variables:
                            self.errors.append(f"Variable {var} used in task {task_name} not found in dsl.")
                stack.extend(graph[task_name])

    def undeclared_variables(self):
        for task in self.dsl:
            if task['task_type'] == 'print':
                # No variable validation required for print tasks
                continue
            
            if task['task_type'] == 'input':
                write_var = task.get('write_variable')
                if write_var not in self.defined_variables:
                    self.errors.append(f"input task: {task['name']} contains undeclared variable {write_var}")
            
            if task['task_type'] == 'plugin':
                # Check read variables
                read_vars = task.get('read_variables', [])
                for i, var in enumerate(read_vars):
                    if var not in self.defined_variables:
                        self.errors.append(f"plugin task: {task['name']} contains undeclared variable {var} in input")
                # Check write variables
                write_vars = task.get('write_variables', [])
                for i, var in enumerate(write_vars):
                    if var not in self.defined_variables:
                        self.errors.append(f"plugin task: {task['name']} contains undeclared variable {var} in output")
            if task['task_type'] == 'operation':
                write_var = task.get('write_variable')
                if write_var not in self.defined_variables:
                    self.errors.append(f"operation task: {task['name']} contains undeclared variable")
            
            if task['task_type'] == 'condition':
                for i, var in enumerate(task['read_variables']):
                    if var not in self.defined_variables:
                        self.errors.append(f"condition task: {task['name']} contains undeclared variable")
        
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
                            self.transition_loop_checker(key)
                else:
                    self.errors.append(f"{key} goto is missing")

            if value["task_type"] == "input":

                if "goto" in value:
                    if isinstance(value["goto"], str):
                        if value["goto"] not in self.dsl_dict:
                            self.errors.append(
                                f"{key} goto task {value['goto']} does not exist"
                            )
                        # else:
                        #     self.transition_loop_checker(
                        #         key,
                        #     )
                else:
                    self.errors.append(f"{key} goto is missing")

                if "error_goto" in value:
                    if isinstance(value["error_goto"], str):
                        if value["error_goto"] not in self.dsl_dict:
                            self.errors.append(
                                f"{key} error_goto task {value['error_goto']} does not exist"
                            )
                        # `else:
                        #     self.transition_loop_checker(key)`
                    error_task = self.dsl_dict[value["error_goto"]]
                    if "goto" in error_task:
                        if error_task["goto"] == key:
                            self.errors.append(
                                f"{key} error_goto is pointing to itself"
                            )

                else:
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
                if "transitions" in value:
                    self.transition_checker(key)
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