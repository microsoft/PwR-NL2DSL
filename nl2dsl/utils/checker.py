from collections import defaultdict
import json
class Checker:
    def __init__(
        self,
        json_data
    ):
        
        self.issues = {"errors": [], "warnings": [], "info": []}
        self.dsl = json_data["dsl"]
        self.variables = json_data["variables"]
        self.defined_variables = {var['name'] for var in self.variables}
        self.config_variables = json_data["config_vars"]
        
        self.dsl_dict = {}
        for task in self.dsl:
            self.dsl_dict[task["name"]] = task
        
        self.variables_dict = {}
        for variable in self.variables:
            self.variables_dict[variable["name"]] = variable

    def transition_checker(self, state_name, condition_key=None):
        state = self.dsl_dict[state_name]
        if state["task_type"] == "condition":
            if "else_goto" not in state:
                self.issues["errors"].append(f"{state_name} else_goto is missing")
            else:
                if state["else_goto"] == None:
                    self.issues["warnings"].append(f"{state_name} else_goto is set None")
                if state["else_goto"] not in self.dsl_dict:
                    self.issues["errors"].append(
                        f"{state_name} else_goto task {state['else_goto']} does not exist"
                    )
            if "conditions" not in state:
                self.issues["errors"].append(f"{state_name} conditions is missing")
            else:
                for condition in state["conditions"]:
                    if not isinstance(condition, dict):
                        self.issues["errors"].append(f"{state_name} condition is not a dict")
                    else:
                        if "condition" not in condition:
                            self.issues["errors"].append(f"{state_name} condition is missing")
                        
                        if "goto" not in condition:
                            self.issues["errors"].append(f"{state_name} goto is missing")
                        else:
                            if condition["goto"] == None:
                                self.issues["warnings"].append(f"{state_name} goto is set None")
                            
                            if condition["goto"] not in self.dsl_dict:
                                self.issues["errors"].append(
                                    f"{state_name} next transition task {condition['goto']} does not exist"
                                )
        if state["task_type"] == "plugin":
            if "transitions" not in state:
                self.issues["errors"].append(f"{state_name} transitions is missing")
            else:
                for transition in state["transitions"]:
                    if not isinstance(transition, dict):
                        self.issues["errors"].append(f"{state_name} transition is not a dict")
                    else:
                        if "code" in transition:
                            if not isinstance(transition["code"], str):
                                self.issues["errors"].append(
                                    f"{state_name} transition code is not a string"
                                )
                        else:
                            self.issues.append(f"{state_name} transition code is missing")

                        if "goto" in transition:
                            if transition["goto"] == None:
                                self.issues["warnings"].append(f"{state_name} goto is set None")
                            if transition["goto"] not in self.dsl_dict:
                                self.issues["errors"].append(
                                    f"{state_name} next transition task {transition['goto']} does not exist"
                                )
                        else:
                            self.issues["errors"].append(f"{state_name} transition is missing")
        if state["task_type"] == "operation":
            if "goto" not in state:
                self.issues["errors"].append(f"{state_name} goto is missing")
            else:
                if state["goto"] == None:
                    self.issues["warnings"].append(f"{state_name} goto is set None")
                if state["goto"] not in self.dsl_dict:
                    self.issues["errors"].append(
                        f"{state_name} next transition task {state['goto']} does not exist"
                    )
        if state["task_type"] == "print":
            if "goto" not in state:
                self.issues["errors"].append(f"{state_name} goto is missing")
            else:
                if state["goto"] == None:
                    self.issues["warnings"].append(f"{state_name} goto is set None")
                if state["goto"] not in self.dsl_dict:
                    self.issues["errors"].append(
                        f"{state_name} next transition task {state['goto']} does not exist"
                    )
        if state["task_type"] == "input":
            if "goto" not in state:
                self.issues["errors"].append(f"{state_name} goto is missing")
            else:
                if state["goto"] == None:
                    self.issues["warnings"].append(f"{state_name} goto is set None")
                if state["goto"] not in self.dsl_dict:
                    self.issues["errors"].append(
                        f"{state_name} next transition task {state['goto']} does not exist"
                    )
            if "error_goto" not in state:
                self.issues["errors"].append(f"{state_name} error_goto is missing")
            else:
                if state["error_goto"] == None:
                    self.issues["warnings"].append(f"{state_name} error_goto is set None")
                if state["error_goto"] not in self.dsl_dict:
                    self.issues["errors"].append(
                        f"{state_name} next transition task {state['error_goto']} does not exist"
                    )

    def transition_loop_checker(self, state_name):
        value = self.dsl_dict[state_name]
        if value["task_type"] == "print":
            if "goto" in value:
                if value["goto"] == state_name:
                    self.issues["warnings"].append(f"Upon task completion, {state_name} transitions to itself, will result in infinite loop")
        if value["task_type"] == "input":
            if "goto" in value:
                if value["goto"] == state_name:
                    self.issues["warnings"].append(f"Upon task completion, {state_name} transitions to itself, will result in infinite loop")
            if "error_goto" in value:
                if value["error_goto"] == state_name:
                    self.issues["warnings"].append(f"Upon error in {state_name} task it transitions to itself, can result in infinite loop")
        if value["task_type"] == "plugin":
            if "transitions" in value:
                for transition in value["transitions"]:
                    if transition["goto"] == state_name:
                        self.issues["warnings"].append(
                            f"{state_name} transitions to itself if error code {transition.get('code')} "
                        )
        if value["task_type"] == "operation":
            if "goto" in value:
                if value["goto"] == state_name:
                    self.issues["warnings"].append(f"Upon task completion, {state_name} transitions to itself, will result in infinite loop")
        if value["task_type"] == "condition":
            if "else_goto" in value:
                if value["else_goto"] == state_name:
                    self.issues["warnings"].append(f"Upon unhandled condition, {state_name} transitions to itself, will result in infinite loop")
            if "conditions" in value:
                for condition in value["conditions"]:
                    if condition["goto"] == state_name:
                        self.issues["warnings"].append(
                            f"{state_name} transitions to itself in condition {condition.get('condition')}"
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
            if 'conditions' in task:
                for condition in task['conditions']:
                    graph[task['name']].append(condition['goto'])
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
                            self.issues["errors"].append(f"Variable {var} used in task {task_name} not found in dsl.")
                if task['task_type'] == 'operation':
                    written_variables.add(task['write_variable'])
                if 'read_variables' in task:
                    for var in task['read_variables']:
                        if var not in written_variables:
                            self.issues["errors"].append(f"Variable {var} used in task {task_name} not found in dsl.")
                stack.extend(graph[task_name])

    def undeclared_variables(self):
        if self.config_variables:
            config_var_names = [var["name"] for var in self.config_variables]
        else:
            config_var_names = []

        for task in self.dsl:
            if task['task_type'] == 'print':
                if "read_variables" in task:
                    for var in task['read_variables']:
                        if var not in self.defined_variables and var not in config_var_names:
                            self.issues["errors"].append(f"print task: {task['name']} contains undeclared variable {var}")
            
            if task['task_type'] == 'input':
                write_var = task.get('write_variable')
                if write_var not in self.defined_variables and write_var not in config_var_names:
                    self.issues["errors"].append(f"input task: {task['name']} contains undeclared variable {write_var}")
            
            if task['task_type'] == 'plugin':
                # Check read variables
                read_vars = task.get('read_variables', [])
                for i, var in enumerate(read_vars):
                    if var not in self.defined_variables and var not in config_var_names:
                        self.issues["errors"].append(f"plugin task: {task['name']} contains undeclared variable {var} in input")
                # Check write variables
                write_vars = task.get('write_variables', [])
                for i, var in enumerate(write_vars):
                    if var not in self.defined_variables and var not in config_var_names:
                        self.issues["errors"].append(f"plugin task: {task['name']} contains undeclared variable {var} in output")
            if task['task_type'] == 'operation':
                write_var = task.get('write_variable')
                if write_var not in self.defined_variables and var not in config_var_names:
                    self.issues["errors"].append(f"operation task: {task['name']} contains undeclared variable")
            
            if task['task_type'] == 'condition':
                for i, var in enumerate(task['read_variables']):
                    if var not in self.defined_variables and var not in config_var_names:
                        self.issues["errors"].append(f"condition task: {task['name']} contains undeclared variable")
        
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
                    self.issues["errors"].append(f"{key} type is not valid")
            else:
                self.issues["errors"].append(f"{key} type is missing")
        self.dfs_check_variables()
        self.undeclared_variables()

    def checker(
        self,
    ):
        self.variable_checker()

        for state_name, state in self.dsl_dict.items():
            self.transition_checker(state_name)
            self.transition_loop_checker(state_name)
            if state["task_type"] == "print":
                if "message" in state:
                    if not isinstance(state["message"], str):
                        self.issues["errors"].append(f"{state_name} message is not a string")
                else:
                    self.issues.append(f"{state_name} message is missing")

            if state["task_type"] == "input":

                if "write_variable" in state:
                    if not isinstance(state["write_variable"], str):
                        self.issues["errors"].append(f"{state_name} write_variable parameter is not string")
                    if state["write_variable"] not in self.variables_dict:
                        self.issues["errors"].append(
                            f"{state_name} write_variable {state['write_variable']} does not exist in variables"
                        )
                if "options" in state:
                    if not isinstance(state["options"], list):
                        self.issues["errors"].append(f"{state_name} options is not a list")

            if state["task_type"] == "plugin":
                if "plugin" in state:
                    if not isinstance(state["plugin"], dict):
                        self.issues["errors"].append(f"{state_name} plugin is not a dict")
                    # how to check if the plugin exists
                    # how to check if the plugin has the correct input and output variables
                else:
                    self.issues["errors"].append(f"{state_name} plugin is missing")

                if "message" in state:
                    if not isinstance(state["message"], str):
                        self.issues["errors"].append(f"{state_name} message is not a string")

            if state["task_type"] == "condition":
                if "read_variables" in state:
                    if not isinstance(state["read_variables"], list):
                        self.issues.append(f"{state_name} read_variables is not a list")
                    else:
                        for read_variable in state["read_variables"]:
                            if read_variable not in self.variables_dict:
                                self.issues.append(
                                    f"{state_name} read_variable {read_variable} does not exist in variables"
                                )
                else:
                    self.issues.append(f"{state_name} read_variables is missing")

                if "conditions" in state:
                    self.transition_checker(state_name, "conditions")
                else:
                    self.issues["errors"].append(f"{state_name} transitions is missing")

        return self.issues
