from termcolor import cprint
import json

from nl2dsl.prompts.atomic import (
    SYSTEM_PROMPT as atomic_system_prompt,
    USER_PROMPT as atomic_user_prompt,
)

from nl2dsl.prompts.plan import (
    SYSTEM_PROMPT as plan_system_prompt,
    USER_PROMPT as plan_user_prompt,
)

from nl2dsl.prompts.plugin import (
    SYSTEM_PROMPT as plugin_system_prompt,
)

from nl2dsl.prompts.global_variables import (
    SYSTEM_PROMPT as global_variables_system_prompt,
    USER_PROMPT as global_variables_user_prompt,
)

from nl2dsl.prompts.config_vars import (
    SYSTEM_PROMPT as config_vars_system_prompt,
    USER_PROMPT as config_vars_user_prompt,
)

from nl2dsl.prompts.task_types import TASK_TYPES_INFO as task_types_info

from nl2dsl.utils.mini_llm import chat_completion_request, call_llm_for_json


def update_flow(step, plugins={}, flow=[], debug=False):

    flow = json.dumps(flow)

    step_type = step["type"]
    if step_type == "add" or step_type == "edit":
        try:
            dsl_list = json.loads(flow)

            sys_prompt = atomic_system_prompt.format(
                dsl=flow, plugins=plugins, task_types_info=task_types_info
            )
            user_prompt = atomic_user_prompt.format(plan=step)
            llm_response = call_llm_for_json(sys_prompt, user_prompt)

            if debug:
                cprint(json.dumps(llm_response, indent=4), "light_yellow")
            if step_type == "add":
                dsl_list.append(llm_response)
            elif step_type == "edit":
                edited_task = llm_response
                edited = False
                for i, task in enumerate(dsl_list):
                    if task["name"] == edited_task["name"]:
                        dsl_list[i] = edited_task
                        edited = True
                        break
                if not edited:
                    dsl_list.append(edited_task)
        except TypeError as e:
            cprint(f"TypeError: {e}")
            cprint(
                f"It is likely that the assistant failed to return a valid json.", "red"
            )
            dsl_list = json.loads(flow)

    if step_type == "delete":
        dsl_list = json.loads(flow)
        delete_task_plan = step
        deleted = False
        for i, task in enumerate(dsl_list):
            if task["name"] == delete_task_plan["task_id"]:
                dsl_list.pop(i)
                deleted = True
                break
        if not deleted:
            cprint(
                f"Task with id {delete_task_plan['task_id']} does not exist in the flow.",
                "red",
            )
            dsl_list = json.loads(flow)

    if debug:
        cprint(f"Intermediate DSL: {json.dumps(dsl_list, indent=4)}", "light_red")
    return dsl_list


def update_global_variables(flow, plugins={}, debug=False):
    sys_prompt = global_variables_system_prompt.format(task_types_info=task_types_info)
    user_prompt = global_variables_user_prompt.format(
        dsl=flow, plugins=json.dumps(plugins)
    )

    variables_list = call_llm_for_json(sys_prompt, user_prompt)

    if debug:
        cprint(variables_list, "light_green")
    return variables_list["variables"]


def update_config_vars(dsl, plugins={}, existing_env_vars=[], debug=False):
    sys_prompt = config_vars_system_prompt.format(task_types_info=task_types_info)
    user_prompt = config_vars_user_prompt.format(
        dsl=dsl,
        plugins=json.dumps(plugins),
        existing_env_vars=json.dumps(existing_env_vars),
    )

    config_vars_dict = call_llm_for_json(sys_prompt, user_prompt)
    if debug:
        cprint(config_vars_dict, "light_green")

    return config_vars_dict["config_variables"]
