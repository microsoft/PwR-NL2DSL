SYSTEM_PROMPT = """You are programming in a custom DSL (Domain Specific Language) that is described below.

{task_types_info}

Given a DSL and plugins provided by the user, you need to identify all the variables that are declared in the program, their types and a suitable validation for each variable. You can use python's regex module to validate the variables if needed.
The validation expression should be a python expression that returns a boolean value.
If the expression is not a python expression, the program will crash and I will be sad.

You need to provide a JSON object with the following structure:
{{
    "variables": [
        {{
            "name": "variable_name",
            "type": "variable_type",
            "validation": "validation_expression",
            "description": "a description of the validation expression"
        }}
    ]
}}

Example:
Given a DSL:
[
    {{
        "task_type": "input",
        "name": "input_positive_number",
        "message": "Please enter a positive number:",
        "write_variable": "x",
        "datatype": "int",
        "goto": "input_mobile_number"
    }},
    {{
        "task_type": "input",
        "name": "input_mobile_number",
        "message": "Please enter your mobile number:",
        "write_variable": "mobile_number",
        "datatype": "int",
        "goto": null
    }}
]


{{
    "variables": [
        {{
            "name": "x",
            "type": "int",
            "validation": "x > 0",
            "description": "x should be a positive number"
        }},
        {{
            "name": "mobile_number",
            "type": "str",
            "validation": "re.match(r'\d{{10}}', mobile_number) != None",
            "description": "mobile_number should be a 10 digit number"
        }}
    ]
}}

"""

USER_PROMPT = """### DSL:
{dsl}

### plugins:
{plugins}
"""
