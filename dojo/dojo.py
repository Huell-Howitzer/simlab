import importlib
from pathlib import Path
from simple_term_menu import TerminalMenu
from rich.console import Console
from rich.markdown import Markdown

BASE_DIR = Path(__file__).parent.resolve()
LEVELS_DIR = BASE_DIR / "levels"

console = Console()

def list_levels():
    levels = []
    for belt in sorted(LEVELS_DIR.iterdir()):
        if belt.is_dir():
            for challenge in sorted(belt.iterdir()):
                if challenge.is_dir():
                    levels.append((belt.name, challenge.name))
    return levels

def load_module(belt, challenge, module_name):
    module_path = f"levels.{belt}.{challenge}.{module_name}"
    return importlib.import_module(module_path)

def show_instructions(belt, challenge):
    instr_path = LEVELS_DIR / belt / challenge / "instructions.md"
    if not instr_path.exists():
        console.print("[red]instructions.md not found.[/red]")
        return
    with instr_path.open("r") as f:
        md = Markdown(f.read())
        console.print(md)

def run_level_script(belt, challenge, script_name):
    try:
        module = load_module(belt, challenge, script_name)
        if hasattr(module, "main"):
            module.main()
        else:
            console.print(f"[red]{script_name}.py missing main()[/red]")
    except ModuleNotFoundError:
        console.print(f"[red]{script_name}.py not found for {belt}/{challenge}[/red]")

def main():
    console.print("[bold cyan]Welcome to Git Dojo![/bold cyan]")

    main_menu = TerminalMenu(
        ["Select Level", "Quit"],
        title="Main Menu"
    )

    while True:
        choice = main_menu.show()
        if choice == 0:
            levels = list_levels()
            level_menu = TerminalMenu(
                [f"{belt}/{challenge}" for belt, challenge in levels],
                title="Select Level"
            )
            selected_index = level_menu.show()
            if selected_index is None:
                continue  # back to main menu

            belt, challenge = levels[selected_index]

            action_menu = TerminalMenu(
                ["Show Instructions", "Run Setup", "Run Check", "Back"],
                title=f"{belt}/{challenge} Actions"
            )
            action_choice = action_menu.show()

            if action_choice == 0:
                show_instructions(belt, challenge)
            elif action_choice == 1:
                run_level_script(belt, challenge, "setup")
            elif action_choice == 2:
                run_level_script(belt, challenge, "check")
            elif action_choice == 3:
                continue
        elif choice == 1:
            console.print("👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
