# PWR NL2DSL

Robust NL2DSL for workflows. This package converts natural language (NL) instructions into a fixed domain specific language (DSL).

## DSL

DSL describes an extended finite state machine with the following fields:

1. `Display` shows a message to the user
2. `Input` asks the user for an input
3. `Operation` processes local variables and assigns the value to a variable.
4. `Condition` for conditional branching
5. `Plugin` to make a plugin call.

## Examples

1. A simple instruction:

```bash
python3 cli.py --instruction "Greet the user"
```

```json
{
    "fsm_name": "welcome_bot",
    "config_vars": [],
    "variables": [],
    "dsl": [
        {
            "task_type": "print",
            "name": "greet_user",
            "message": "Welcome to the workflow! How can I help you today?",
            "goto": null
        }
    ]
}
```

2. A complex instruction that uses a plugin
```bash
cat tests/plugins.yaml | head -n 10
payment: |
    The name of the plugin is payment. This plugin helps in collecting a payment from the user by generating a payment link.

    The inputs needed are:
        - mobile_number (type:str) : The mobile number of the user
        - name (type:str) : Name of the user
        - CLIENT_ID (type:str) : API secret key for the payment gateway
        - CLIENT_SECRET (type:str) : API secret key for the payment gateway
        - AMOUNT (type:int) : The amount to be collected from the user
        - REASON (type:str) : The reason for the payment


python3 cli.py --instruction "Tell the user we are going to help them book an appointment. For this we need to collect Rs 600. Collect the users mobile number and name. Then collect the amount using the payment plugin" --plugin tests/plugins.yaml
```

```json
{
    "fsm_name": "unnamed_fsm",
    "config_vars": [
        {
            "name": "CLIENT_ID",
            "type": "string",
            "description": "API secret key for the payment gateway",
            "plugins": [
                "payment"
            ]
        },
        {
            "name": "CLIENT_SECRET",
            "type": "string",
            "description": "API secret key for the payment gateway",
            "plugins": [
                "payment"
            ]
        }
    ],
    "variables": [
        {
            "name": "mobile_number",
            "type": "str",
            "validation": "re.match(r'^\\d{10}$', mobile_number) is not None",
            "description": "mobile_number should be a 10 digit number"
        },
        {
            "name": "name",
            "type": "str",
            "validation": "len(name) > 0 and all(x.isalnum() or x.isspace() for x in name)",
            "description": "name should be a non-empty string containing only alphanumeric characters and spaces"
        },
        {
            "name": "TXN_ID",
            "type": "str",
            "validation": "len(TXN_ID) > 0",
            "description": "TXN_ID should be a non-empty string"
        }
    ],
    "dsl": [
        {
            "task_type": "print",
            "name": "inform_booking_appointment",
            "message": "We are going to help you book an appointment.",
            "goto": "collect_mobile_task"
        },
        {
            "task_type": "input",
            "name": "collect_mobile_task",
            "message": "Please enter your mobile number:",
            "write_variable": "mobile_number",
            "datatype": "str",
            "goto": "collect_name_task",
            "error_goto": "collect_mobile_task"
        },
        {
            "task_type": "input",
            "name": "collect_name_task",
            "message": "Please enter your name:",
            "write_variable": "name",
            "datatype": "str",
            "goto": "payment_task",
            "error_goto": "collect_name_task"
        },
        {
            "task_type": "plugin",
            "name": "payment_task",
            "read_variables": [
                "mobile_number",
                "name"
            ],
            "environment_variables": [
                "CLIENT_ID",
                "CLIENT_SECRET"
            ],
            "write_variables": [
                "TXN_ID"
            ],
            "plugin": {
                "name": "payment",
                "inputs": {
                    "mobile_number": "mobile_number",
                    "name": "name",
                    "CLIENT_ID": "CLIENT_ID",
                    "CLIENT_SECRET": "CLIENT_SECRET",
                    "AMOUNT": 600,
                    "REASON": "Appointment Booking Charge"
                },
                "outputs": {
                    "TXN_ID": "TXN_ID"
                }
            },
            "description": "Collecting a payment of Rs 600 from the user for booking appointment.",
            "transitions": [
                {
                    "code": "SUCCESS",
                    "goto": "payment_success_print_task",
                    "description": "The payment was successfully collected."
                },
                {
                    "code": "CANCELLED_BY_USER",
                    "goto": "payment_cancelled_print_task",
                    "description": "The payment was cancelled by the user."
                },
                {
                    "code": "EXPIRED",
                    "goto": "payment_expired_print_task",
                    "description": "The payment link has expired."
                },
                {
                    "code": "SERVER_DOWNTIME",
                    "goto": "payment_server_downtime_print_task",
                    "description": "The server is currently down."
                },
                {
                    "code": "SERVER_ERROR",
                    "goto": "payment_server_error_print_task",
                    "description": "There was an error on the server."
                }
            ]
        }
    ]
}
```

3. Edit on an existing DSL. (We store the above dsl as `sample.json`)
```bash
python3 cli.py -i "On success, tell the user that their appointment is booked and they will receive an SMS on their mobile number" -d sample.json --debug
```

```json
{
    ...
        {
            "task_type": "plugin",
            "name": "payment_task",
            "read_variables": [
                "mobile_number",
                "name"
            ],
            "environment_variables": [
                "CLIENT_ID",
                "CLIENT_SECRET"
            ],
            "write_variables": [
                "TXN_ID"
            ],
            "plugin": {
                "name": "payment",
                "inputs": {
                    "mobile_number": "mobile_number",
                    "name": "name",
                    "CLIENT_ID": "CLIENT_ID",
                    "CLIENT_SECRET": "CLIENT_SECRET",
                    "AMOUNT": 600,
                    "REASON": "Appointment Booking Charge"
                },
                "outputs": {
                    "TXN_ID": "TXN_ID"
                }
            },
            "description": "Collecting a payment of Rs 600 from the user for booking an appointment.",
            "transitions": [
                {
                    "code": "SUCCESS",
                    "goto": "appointment_success_print_task",
                    "description": "The payment was successfully collected."
                },
                {
                    "code": "CANCELLED_BY_USER",
                    "goto": "payment_cancelled_print_task",
                    "description": "The payment was cancelled by the user."
                },
                {
                    "code": "EXPIRED",
                    "goto": "payment_expired_print_task",
                    "description": "The payment link has expired."
                },
                {
                    "code": "SERVER_DOWNTIME",
                    "goto": "payment_server_downtime_print_task",
                    "description": "The server is currently down."
                },
                {
                    "code": "SERVER_ERROR",
                    "goto": "payment_server_error_print_task",
                    "description": "There was an error on the server."
                }
            ]
        },
        {
            "task_type": "print",
            "name": "appointment_success_print_task",
            "message": "Your appointment is booked. You will receive an SMS on your mobile number shortly.",
            "goto": null
        }
    ]
}
```

## Developer

Setup [poetry](https://python-poetry.org/docs/#installation) shell and `.env` file

```bash
poetry shell
poetry install
```

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
