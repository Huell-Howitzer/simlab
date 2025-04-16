from rich.console import Console
from rich.table import Table
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import Application
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout import Layout, HSplit
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.eventloop import use_asyncio_event_loop
import asyncio
import subprocess

console = Console()

# Get git tags
def get_git_tags():
    result = subprocess.run(["git", "tag"], stdout=subprocess.PIPE, text=True)
    return result.stdout.strip().split('\n')

all_tags = get_git_tags()
filtered_tags = all_tags.copy()

# Rich table renderer
def render_table(tags):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Tag")
    for tag in tags:
        table.add_row(tag)
    console.clear()
    console.print(table)

# Prompt_toolkit setup
search_buffer = Buffer()

# Custom key bindings
kb = KeyBindings()
selected_tag = {"tag": None}

@kb.add("enter")
def _(event):
    # Pick the first result from filtered list
    if filtered_tags:
        selected_tag["tag"] = filtered_tags[0]
        event.app.exit()

@search_buffer.on_text_changed
def on_text_change(_):
    global filtered_tags
    text = search_buffer.text
    filtered_tags = [tag for tag in all_tags if text.lower() in tag.lower()]
    render_table(filtered_tags)

# Main function
def main():
    use_asyncio_event_loop()
    render_table(filtered_tags)

    input_area = TextArea(
        height=1,
        prompt="Filter tags: ",
        multiline=False,
        wrap_lines=False,
        buffer=search_buffer
    )

    layout = Layout(HSplit([input_area]))

    app = Application(layout=layout, key_bindings=kb, full_screen=False)
    asyncio.run(app.run_async())

    if selected_tag["tag"]:
        print(f"Selected tag: {selected_tag['tag']}")
        # Chop the selected tag (example action)
        subprocess.run(["git", "tag", "-d", selected_tag["tag"]])
        print(f"Deleted tag: {selected_tag['tag']}")

if __name__ == "__main__":
    main()