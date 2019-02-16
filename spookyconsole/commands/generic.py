
"""
TODO
"""

import click
from spookyconsole.exceptions import AbortPromptLoop


quit_aliases = ["exit"]


@click.command("quit")
def quit_():
    """Exit the prompt loop."""
    raise AbortPromptLoop
