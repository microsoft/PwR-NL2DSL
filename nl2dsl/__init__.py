import json
from termcolor import cprint
from typing import List, Dict, Callable

from .utils.mini_llm import call_llm_for_json, chat_completion_request
from .utils.dsl_utils import (
    update_flow,
    update_global_variables,
    update_config_vars,
)
from .utils.checker import Checker

from .prompts.plan import (
    SYSTEM_PROMPT as plan_system_prompt,
    USER_PROMPT as plan_user_prompt,
)

from .prompts.task_types import TASK_TYPES_INFO as task_types_info


class NL2DSL:
    utterance: str
    plugins: dict
    initial_dsl: str
    dsl: Dict[str, List[Dict]]
    plan: List[Dict] = []
    atomic_changes: List[Dict] = []
    debug: bool = False
    status_update_callback: callable = None

    def __init__(
        self,
        utterance: str,
        plugins: dict = None,
        dsl: dict = None,
        status_update_callback: Callable[[str, Dict], None] = None,
        debug: bool = False,
    ) -> None:

        self.utterance = utterance
        self.plugins = plugins or {}
        self.dsl = dsl or {
            "variables": [],
            "config_vars": [],
            "dsl": [
                {
                    "task_type": "start",
                    "name": "start",
                    "goto": "end",
                },
                {
                    "task_type": "end",
                    "name": "end",
                    "goto": None,
                },
            ],
            "fsm_name": "unnamed_fsm",
        }
        self.initial_dsl = self.dsl.copy()
        self.debug = debug
        self.status_update_callback = status_update_callback

    def nl2dsl(self) -> Dict[str, List[Dict]]:
        self._generate_plan_from_utterance()
        self._update_dsl_using_plan()
        return self.dsl

    def _generate_plan_from_utterance(self) -> List[Dict]:
        flow = self.dsl["dsl"]
        self.plan = call_llm_for_json(
            system_prompt=plan_system_prompt.format(
                dsl=json.dumps(flow),
                plugins=(self.plugins or "There are no plugins"),
                task_types_info=task_types_info,
            ),
            user_prompt=plan_user_prompt.format(utterance=self.utterance),
        )["substeps"]

        self.status_update_callback and self.status_update_callback(
            event="plan_generated", data=self.plan
        )

        if self.debug:
            cprint(f"Plan:\n{self.plan}", "light_yellow")
        return self.plan

    def _update_dsl_using_plan(self) -> Dict[str, List[Dict]]:
        flow = self.dsl["dsl"].copy()

        for i, step in enumerate(self.plan):

            self.status_update_callback and self.status_update_callback(
                event="step_update", data={"step":step, "step_number":(i+1), "flow":flow}
            )

            step_plugin = ""
            if step.get("plugin_id"):
                step_plugin = self.plugins[step["plugin_id"]]
            flow = update_flow(step, self.plugins, flow)

            
            if self.debug:
                cprint(f"Intermediate Flow:\n{flow}", "light_red")



        self.debug and print("Pruning transitions")
        self._prune_transitions(flow)
        self.debug and print("Pruned!!")

        self.status_update_callback and self.status_update_callback(
            event="flow_update_completed", data=flow
        )
        
        global_variables_list = update_global_variables(flow, self.plugins, self.debug)
        self.status_update_callback and self.status_update_callback(
            event="global_variables_updated", data=global_variables_list
        )
        
        new_env_vars = update_config_vars(
            flow, self.plugins, self.dsl["config_vars"], self.debug
        )

        self.status_update_callback and self.status_update_callback(
            event="config_vars_updated", data=new_env_vars
        )

        new_dsl = {
            "fsm_name": self.dsl["fsm_name"],
            "config_vars": new_env_vars,
            "variables": global_variables_list,
            "dsl": flow,
        }

        self.status_update_callback and self.status_update_callback(
            event="dsl_updated_successfully", data=new_dsl
        )

        self.dsl = new_dsl
        return self.dsl

    def validate_dsl(self):
        checker = Checker(self.dsl)
        errors = checker.checker()
        return errors

    def _prune_transitions(self, flow):
        # get list of tasks in the dsl
        task_names = [task["name"] for task in flow]
        for i, task in enumerate(flow):
            task_type = task.get("task_type")
            if task_type == "print":
                if task.get("goto") not in task_names:
                    flow[i]["goto"] = None

            elif task_type in ("input", "operation"):
                if task.get("goto") not in task_names:
                    flow[i]["goto"] = None
                if task.get("error_goto") not in task_names:
                    flow[i]["error_goto"] = None

            elif task_type == "condition":
                for j, condition in enumerate(task.get("conditions", [])):
                    if condition.get("goto") not in task_names:
                        flow[i]["conditions"][j]["goto"] = None
                if task.get("else_goto") not in task_names:
                    flow[i]["else_goto"] = None

            elif task_type == "plugin":
                # TODO: check and handle all the error codes from the plugin
                for j, transition in enumerate(task.get("transitions", [])):
                    if transition.get("goto") not in task_names:
                        flow[i]["transitions"][j]["goto"] = None
        return flow


__all__ = ["NL2DSL"]
