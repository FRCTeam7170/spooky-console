
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


class Application:

    def __init__(self, root_cmd, prog_name, prompt=">", gui_interval=20):
        self.commander = pycmds.Commander(root_cmd, name=prog_name, suppress_aborts=True)
        self.prompt_session = pt.PromptSession(message=prompt,
                                               completer=pycmds.CmdCompleter(root_cmd, prog_name=prog_name))
        self.commander.obj.prog_name = prog_name
        self.commander.obj.gui_interval = gui_interval

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


async def main():
    from spookyconsole.commands.generic import quit_, quit_aliases
    from spookyconsole.commands.networktables import nt, get, set_, cd, list_, list_aliases, pwd
    cli.add_command(quit_, aliases=quit_aliases)
    cli.add_command(nt)
    nt.add_command(get)
    nt.add_command(set_)
    nt.add_command(cd)
    nt.add_command(list_, aliases=list_aliases)
    nt.add_command(pwd)
    app = Application(cli, "spooky-console")
    print_banner()
    with patch_stdout():
        await app.loop()


if __name__ == '__main__':

    use_asyncio_event_loop()
    # use_asyncio_event_loop creates a new event loop, so we mustn't use asyncio.run
    asyncio.get_event_loop().run_until_complete(main())
