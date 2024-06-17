class Checker:
    def __init__(
        self,
        dsl,
        variables,
    ):
        self.errors = []
        self.dsl = dsl
        self.dsl_dict = {}
        self.defined_variables = {var['name'] for var in variables}
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
    
    def undeclared_variables(self):
        for task in self.dsl:
            if task['task_type'] == 'print':
                # No variable validation required for print tasks
                continue
            
            if task['task_type'] == 'input':
                write_var = task.get('write_variable')
                if write_var not in self.defined_variables:
                    self.errors.append(f"input {task} contains undeclared variable {write_var}")
            
            if task['task_type'] == 'plugin':
                # Check read variables
                read_vars = task.get('read_variables', [])
                for i, var in enumerate(read_vars):
                    if var not in self.defined_variables:
                        self.errors.append(f"plugin {task} contains undeclared variable {var} in input")
                # Check write variables
                write_vars = task.get('write_variables', [])
                for i, var in enumerate(write_vars):
                    if var not in self.defined_variables:
                        self.errors.append(f"plugin {task} contains undeclared variable in output")
            if task['task_type'] == 'operation':
                write_var = task.get('write_variable')
                if write_var not in self.defined_variables:
                    self.errors.append(f"operation {task} contains undeclared variable")
            
            if task['task_type'] == 'condition':
                for i, var in enumerate(task['read_variables']):
                    if var not in self.defined_variables:
                        self.errors.append(f"condition {task} contains undeclared variable")
        
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
                                f"{key} goto task {value['goto']} does not exist"
                            )
                        else:
                            self.transition_loop_checker(key)
                    # else:
                    #     self.errors.append(f"{key} goto is not a string")
                else:
                    self.errors.append(f"{key} goto is missing")

            if value["task_type"] == "input":

                if "goto" in value:
                    if isinstance(value["goto"], str):
                        if value["goto"] not in self.dsl_dict:
                            self.errors.append(
                                f"{key} goto task {value['goto']} does not exist"
                            )
                        else:
                            self.transition_loop_checker(
                                key,
                            )
                    # else:
                    #     self.errors.append(f"{key} goto is not a string")
                else:
                    self.errors.append(f"{key} goto is missing")

                if "error_goto" in value:
                    if isinstance(value["error_goto"], str):
                        if value["error_goto"] not in self.dsl_dict:
                            self.errors.append(
                                f"{key} error_goto task {value['error_goto']} does not exist"
                            )
                        else:
                            self.transition_loop_checker(key)
                    # else:
                    #     self.errors.append(f"{key} error_goto is not a string")

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

                if "write_variable" in value:
                    if not isinstance(value["write_variable"], str):
                        self.errors.append(f"{key} write_variable is not a string")

                    if value["write_variable"] not in self.variables_dict:
                        self.errors.append(
                            f"{key} write_variable {value['write_variable']} does not exist in variables"
                        )

                    if (
                        self.variables_dict[value["write_variable"]]["type"]
                        != value["datatype"]
                    ):
                        self.errors.append(
                            f"{key} write_variable {value['write_variable']} datatype does not match"
                        )

                    # how to identify if the validation on the variable is correct
                else:
                    self.errors.append(f"{key} write_variable is missing")

            if value["task_type"] == "plugin":
                if "plugin" in value:
                    if not isinstance(value["plugin"], dict):
                        self.errors.append(f"{key} plugin is not a dict")
                    # how to check if the plugin exists
                    # how to check if the plugin has the correct input and output variables

                    if "input_variables" in value:
                        if not isinstance(value["input_variables"], dict):
                            self.errors.append(f"{key} input_variables is not a dict")
                        else:
                            for plugin_var, task_var in value[
                                "input_variables"
                            ].items():
                                if task_var not in self.variables_dict:
                                    self.errors.append(
                                        f"{key} input_variable plugin {task_var} does not exist in variables"
                                    )

                    if "output_variables" in value:
                        if not isinstance(value["output_variables"], dict):
                            self.errors.append(f"{key} output_variables is not a dict")
                        else:
                            for plugin_var, task_var in value[
                                "output_variables"
                            ].items():
                                if task_var not in self.variables_dict:
                                    self.errors.append(
                                        f"{key} output_variable plugin {task_var} does not exist in variables"
                                    )
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

                if "transitions" in value:
                    self.transition_checker(key)
                else:
                    self.errors.append(f"{key} transitions is missing")

        return self.errors
