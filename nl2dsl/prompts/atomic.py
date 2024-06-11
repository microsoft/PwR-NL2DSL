SYSTEM_PROMPT = """
{task_types_info}

Current Program:
```JSON
{dsl}
```

Plugins:
{plugins}

Only add `plugin` to any task if there is plugin specified and details provided with the plan else never add `plugin` to any task. Prefer to use a plugin task over a logic task if the computation is complex and can be done using a plugin.

Never set the transition/goto a task that is not defined in DSL. If you don't know what to set it to, set it to None.

Your work involves creating a specific task based solely on the provided plan. If the plan is an addition, you will add a new task. If the plan is a modification, you will edit an existing task. Your response should be complete a task, with all necessary context and plugin information included. You must return a JSON object.
Carefully proofread the plan to ensure clarity and verbosity, making the task's objectives and requirements explicit and understandable.
"""

USER_PROMPT = """
Follow the following plan:
{plan}
"""
