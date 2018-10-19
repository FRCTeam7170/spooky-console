
"""
TODO
"""

import asyncio
import click
import pycmds
import prompt_toolkit as pt
from prompt_toolkit.eventloop import use_asyncio_event_loop
from prompt_toolkit.patch_stdout import patch_stdout
from spookyconsole.exceptions import AbortPromptLoop


PROG_NAME = "spooky-console"
PROMPT = "> "


class Application:

    def __init__(self, root_cmd):
        self.commander = pycmds.Commander(root_cmd, name=PROG_NAME, suppress_aborts=True)
        self.prompt_session = pt.PromptSession(message=PROMPT,
                                               completer=pycmds.CmdCompleter(root_cmd, prog_name=PROG_NAME))

    async def loop(self):
        try:
            while True:
                cmd = await self.prompt_session.prompt(async_=True)
                result = self.commander.exec(cmd)
                if result is not None:
                    print(result)
        except AbortPromptLoop:
            print("Aborting prompt loop.")


@click.group(cls=pycmds.AliasGroup)
def cli():
    pass


@cli.command()
@click.option("opt", "--opt")
def other(opt):
    return "modified:{}".format(opt)


def print_banner():
    from colorama import colorama_text, Fore, Back, Style
    with colorama_text():
        print(Back.WHITE + Fore.BLACK)
        print("""\
           __.---.__                                                                                        
       .-''   ___   ''-.                                                                                    
     .'   _.-' __'-._   '.                                                                                  
   .'   .'     \ \   '.   '.                             _                                          _       
  /    /    /\  \ \    '----'      ___ _ __   ___   ___ | | ___   _        ___ ___  _ __  ___  ___ | | ___  
 /    '----/ /   \ \--------.     / __| '_ \ / _ \ / _ \| |/ / | | |_____ / __/ _ \| '_ \/ __|/ _ \| |/ _ \\ 
 | SPOOKY   /     |  ACTION  |    \__ \ |_) | (_) | (_) |   <| |_| |_____| (_| (_) | | | \__ \ (_) | |  __/ 
 '-------/ /      `-   ---.  |    |___/ .__/ \___/ \___/|_|\_\\\\__, |      \___\___/|_| |_|___/\___/|_|\___| 
  ----  / /    .    \ \  /   /        |_|                     |___/                                         
  \   \ \/   :(o).   \/ /   /                    - Team 7170 console-based control utility -                
   '.  ''._     `    _.'  .'                                                                                
     '.    '-.____.-'    .'                                                                                 
       '-.._ROBOTICS_..-'                                                                                   
            ''----''                                                                                        
""", end="")
        print(Style.RESET_ALL)


async def my_coroutine():
    for i in range(15):
        await asyncio.sleep(1)
        print(i)


async def main():
    from spookyconsole.commands.generic import quit_, quit_aliases
    cli.add_command(quit_, aliases=quit_aliases)
    app = Application(cli)
    print_banner()
    with patch_stdout():
        await asyncio.gather(app.loop(), my_coroutine())


if __name__ == '__main__':
    use_asyncio_event_loop()
    # use_asyncio_event_loop creates a new event loop, so we mustn't use asyncio.run
    asyncio.get_event_loop().run_until_complete(main())
