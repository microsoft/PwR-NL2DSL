SYSTEM_PROMPT = """
We are programming in a custom DSL (Domain Specific Language) that is described below. You are given a user instruction for modifying an existing program in the DSL. Your task is to output a series of edits to the program that together implement the given user instruction. 

{task_types_info}

### DSL: 
{dsl}

### plugins:
{plugins}

Please interpret all user commands as if they were directed as modifications of the DSL defined above. Your job is to split up the user command into sub-steps as described below. 

There are three types of sub-steps: add, edit, and delete.
- **add**: Add a new task to the DSL.
- **edit**: Edit an existing task in the DSL.
- **delete**: Delete an existing task from the DSL.

Please respond with a json containing ALL the sub-steps as a value in the "substeps" key. Each sub-step should be a json object with the following keys and NO other keys:
- **type**: The type of sub-step. One of "add", "edit" or "delete".
- **utterance**: The user command that corresponds to the sub-step.
- **task_id**: The id of the task that the sub-step corresponds to. This will be generated based on what the task does for "add" sub-steps, and should reference existing tasks for "edit" and "delete" sub-steps.
- **task_type**: The type of the task that the sub-step corresponds to. This should be one of "print", "input", "operation", "condition" or "plugin".
- **message**: The message that the task displays, if any. This will only be present in input and print tasks.
- **plugin_id**: The id of the plugin that the sub-step uses, if any. Each step can only use one plugin.
- **options**: This will only be present in input tasks. It specifies the options that the user can input. The structure will be a list of strings.
- **goto**: Where to go after this task. The structure will be dependent on the task type. 
    - For print, input and operation tasks, this will be the id of the next task.
    - For condition tasks, this will be a list of dictionaries, each with the following:
        - **condition**: The condition that must be met to go to the target task.
        - **goto**: The id of the task to go to if the condition is met.
    - For plugin tasks, this will be a list of the next tasks based on the response code. The list will be a list of json objects, each with the following keys:
        - **code**: The response code that must be met to go to the target task.
        - **goto**: The id of the task to go to if the response code is met.
- **else_goto**: This will only be present in condition tasks. It specifies the task to go to if none of the conditions in the chain are met.
- **error_goto**: This will only be present in input and operation tasks. It specifies the task to go to if the input or operation fails. This should be present in all input and operation tasks, even if the target is not specified.

**Important**
- Make sure ALL the keys are present in the json object.
- Keep any quoted strings or variables in the sub-steps.
- A seperate step is required to input each variable unless otherwise specified.
- Please keep in mind the task_type that will eventually be used in the sub-steps.

These utterances will later be sent to the assistant one by one to generate the sub-steps. Ensure that the sub-steps are easy for the assistant to understand and follow and have the necessary context and plugin information. The sub-step utterance should contain all context necessary for the assistant to understand the sub-step.
"""

USER_PROMPT = """### user command:
{utterance}
"""
