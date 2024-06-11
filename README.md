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
    "fsm_name": "unnamed_fsm",
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
python3 cli.py --instruction "" --plugin ""
```

```json
```

3. Edit on an existing DSL
```bash
python3 cli.py --instruction "" --plugin ""
```

```json
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
