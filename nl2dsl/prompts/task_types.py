TASK_TYPES_INFO = """# Description of the DSL:
Our DSL is a programming language for implementing workflows. A program consists of a list of Tasks. Each Task carries out a unit of work and then transitions to another Task or terminates the program, similar to a State machine. The first task in the list of Tasks is the entry-point of the program.

All variables are global, unless otherwise specified. However, a task can only use a variable that has been declared. Variables can have any of python's built in data types (string, list, dictionary, etc.). 
The exception to this are read only environment or config variables, which are provided by the system and can be used by the plugins.

The DSL supports the following actions:
- Display/Print a message to the user  
- Prompt the user for input  
- Call a plugin(function) 
- Evaluate python-like expressions (and store them in variables). 
- Conditional Branching based on the result of python expressions. 

## Tasks:
A Task can be one of six kinds: Print, Input, Operation, Condition, Plugin. Their description is as follows.

### Print Task
It is used to print a message or variable to the user and then simply go to the next Task. Any variables used in the message should be put in curly braces, in python's f-string style. It has the following fields:
- *task_type*: The type of the task. It should be "print".
- *name*: A unique name for the task.
- *message*: The message to be displayed to the user. This message can contain variables in curly braces, which will be replaced by the value of the variable. The variables should be the names of the variables declared in the program.
- *goto*: The name of the next task to transition to. This is the only transition and it is always taken.

**Usage**: This task is used to print a message to the user, similar to python's print() function. It can be used to print the value of a variable or any other message to the user. It is a simple task that transitions to the next task after displaying the message.

**Example**:
{{
    "task_type": "print",
    "name": "example_task",
    "message": "The message to be displayed to the user",
    "goto": "next_task"
}}

### Input Task
This task is used to obtain input from the user, similar to python's input() function. It validates the input based on the condition provided and transitions to the next task if the input is valid. If the input is invalid, by default the task is repeated until the user provides valid input.

It has the following fields:
- *task_type*: The type of the task. It should be "input".
- *name*: A unique name for the task.
- *message*: A message to be displayed to the user describing what input they should enter.
- *write_variable*: The variable that will be assigned the user input value.
- *options*: A list of valid options for the input. If provided, the input must be one of these options.
- *datatype*: The datatype of the input. It can be any one of python's built-in datatypes: int, float, str, bool, list, dict, tuple, set, complex, bytes, bytearray, memoryview, NoneType. The input will be converted to this datatype. The input will be converted to this datatype. It is essential to provide the correct datatype for the input.
- *goto*: The name of the next task to transition to if the input is successful and valid.
- *error_goto*: The name of the next task to transition to if the input is invalid.

**Usage**: It can only be used to get input from the user and assign it to a variable.

**Example**:
{{
    "task_type": "input",
    "name": "example_input_task",
    "message": "Please input a number between 1 and 10",
    "write_variable": "x",
    "datatype": "int",
    "goto": "next_task",
    "error_goto": "error_task"
}}


### Operation Task
This is the task to use when you want to perform some operation and assign the result to a variable. The operation can be any valid python expression.
It has the following fields:
- *task_type*: The type of the task. It should be "operation".
- *name*: A unique name for the task.
- *operation*: The operation that must be performed. This expression must be valid python. This computation must read the variables declared in the read_variables field and write to the variable declared in the write_variable field.
- *description*: A brief description of the operation being performed.
- *read_variables*: The list of variables read in the operation.
- *write_variable*: The variable written to in the operation.
- *goto*: The name of the next task to transition to if the operation is successful.
- *error_goto*: The name of the next task to transition to if the operation fails.


**Usage:** Think of this task as running a line of code in python to assign a variable to the result of some computation. You should use this task to perform any computation or logical operation. Don't use any other task for these purposes.

**Example:**
{{
    "type": "operation",
    "name": "example_op_task",
    "operation": "y = x + 1",
    "description": "Add 1 to x and store the result in y",
    "read_variables": [ "x" ],
    "write_variable": "y",
    "goto": "next_task",
    "error_goto": "error_task"
}}


### Condition Task
This task is used to create an if-elif-else chain, transitioning to different tasks based on the result of each condition. It has the following fields:
- *task_type*: The type of the task. It should be "condition".
- *name*: A unique name for the task.
- *conditions*: A list of conditions to be checked in order. Each condition is a dictionary with the following keys:
    - *condition*: The condition to be checked. This expression must be valid python and must return a boolean value. The condition must read the variables declared in the read_variables field.
    - *goto*: The name of the next task to transition to if the condition is true.
    - *condition_description*: A description of the condition for better understanding.
- *else_goto*: The name of the next task to transition to if none of the conditions are true.
- *else_description*: A description of the else condition for better understanding.
- *read_variables*: The list of variables read in the conditions.

**Usage:** his task is used to check conditions and transition to different tasks based on the result of those conditions. It is used to create branches in the program based on some condition.

**Example**:
{{
    "task_type": "condition",
    "name": "example_condition_task",
    "conditions": [
        {{ "condition": "x > 10", "goto": "x_gt_10_task", "condition_description": "x is greater than 10"}},
        {{ "condition": "x < 10", "goto": "x_lt_10_task", "condition_description": "x is less than 10"}}
    ],
    "else_goto": "x_eq_10_task",
    "else_description": "x is equal to 10",
    "read_variables": [ "x" ]
}}

### Plugin Task
This task is used to call a plugin. You can think of a plugin as a function that takes some inputs and returns some outputs as well as a response code. The transitions are completely based on the response code from the plugin. All possible response codes will be defined in the plugin and there should be a transition for each response code in the task. It has the following fields:

- *task_type*: The type of the task. It should be "plugin".
- *name*: A unique name for the task.
- *read_variables*: The list of variables read to call the corresponding task.
- *environment_variables*: The list of environment variables required by the plugin. These can be treated like read only input variables.
- *write_variables*: The list of variables written by the task.
- *plugin*: A dictionary containing the plugin name, inputs, and outputs. The inputs and outputs are mappings from the plugin's input/output variables to the program's variables.
- *description*: Explain what task is being performed in brief.
- *transitions*: Transitions are based on the response code from the plugin. 

The response code is a string and must be one of the response codes from the plugin. The transition is taken if the response code from the plugin matches the the one in 'code'.

**Usage:** This task can only be used to call a plugin and get the result from the plugin. The transitions are completely based on the response code from the plugin.

**Example:**
    Given Plugin Details:
        Name: example_plugin
        Description: This is a demo plugin to represent how to create plugin task.
        Inputs:
            - X_variable, type: string : description of X_variable.
            - Y_variable, type: int : description of Y_variable.
            - Z_variable, type: string : description of Z_variable.
        Environment Variables:
            - PLUGIN_API_KEY, type: string : description of PLUGIN_API_KEY.
        Outputs:
            - A_result, type: string : description of A_result.
            - B_result, type: int : description of B_result.
  

        Return codes:
            - 200: Success.
            - 400: Invalid input parameters.
            - 500: Server error, try again later.

    {{
        "task_type": "plugin",
        "name": "example_plugin_task",
        "read_variables": [
            "x",
            "y",
            "z",
        ],
        "environment_variables": [
            "PLUGIN_API_KEY"
        ],
        "write_variables": [
            "a",
            "b",
            ],
        "plugin": {{
            "name": "example_plugin",
            "inputs": {{
                "X_variable": "x",
                "Y_variable": "y",
                "Z_variable": "z",
                "PLUGIN_API_KEY": "PLUGIN_API_KEY"
            }},
        "outputs": {{
            "A_result": "a",
            "B_result": "b"
            }},
        }},
        "description": "calling the example plugin to get the result of A and B from X, Y, Z.",
            "transitions": [
                {{"code": "200", "goto": "next_define_task", "description": "Success"}},
                {{"code": "400", "goto": "invalid_input_task", "description": "Invalid input parameters"}},
                {{"code": "500", "goto": "server_error_task", "description": "Server error, try again later"}},
            ],
        }},

## NOTE:
1. Think of a task as a state in a finite state machine. A task will do some work and then transition to the next task, often based on some condition.
2. It is important to think of a task as an atomic unit of work. A task should be simple and should do only one thing. If you find a task doing multiple things, consider breaking it down into multiple tasks.
"""
