Let’s gooo—here’s your full working MVP for cmdvault.

⸻

Setup Instructions

1. Install dependencies (just once)

pip3 install --user rich

2. Save the script

Save this as cmdvault.py in a shared or user-specific path:

mkdir -p /nfs/home/$USER/.cmdvault
nano /nfs/home/$USER/.cmdvault/cmdvault.py

Paste the script below:

⸻

cmdvault.py

#!/usr/bin/env python3

import argparse
import sqlite3
import os
import datetime
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Location: /nfs/home/$USER/.cmdvault/cmdvault.db
VAULT_DIR = Path(os.getenv("CMDVAULT_HOME", f"/nfs/home/{os.getenv('USER')}/.cmdvault"))
VAULT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = VAULT_DIR / "cmdvault.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            command TEXT NOT NULL,
            tags TEXT,
            notes TEXT,
            output TEXT
        )
        """)
        conn.commit()

def save_command(args):
    output = None
    if args.capture_output:
        try:
            output = subprocess.check_output(args.command, shell=True, stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            output = e.output

    timestamp = datetime.datetime.now().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
        INSERT INTO commands (timestamp, command, tags, notes, output)
        VALUES (?, ?, ?, ?, ?)
        """, (timestamp, args.command, args.tag, args.note, output))
        conn.commit()
        console.print(f"[green]Saved command:[/green] {args.command}")

def list_commands(args):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, timestamp, command, tags FROM commands ORDER BY id DESC LIMIT ?", (args.limit,))
        rows = c.fetchall()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim")
        table.add_column("Time", width=19)
        table.add_column("Command")
        table.add_column("Tags", style="cyan")

        for row in rows:
            table.add_row(str(row[0]), row[1][:19], row[2], row[3] or "")
        console.print(table)

def view_command(args):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, timestamp, command, tags, notes, output FROM commands WHERE id = ?", (args.id,))
        row = c.fetchone()
        if not row:
            console.print(f"[red]No command found with ID {args.id}[/red]")
            return

        console.print(Panel.fit(
            f"[bold]Command:[/bold] {row[2]}\n"
            f"[bold]Tags:[/bold] {row[3]}\n"
            f"[bold]Notes:[/bold] {row[4]}\n"
            f"[bold]Time:[/bold] {row[1]}\n\n"
            f"[bold]Output:[/bold]\n{row[5] or '[dim]No output captured[/dim]'}",
            title=f"Command #{row[0]}"
        ))

def search_commands(args):
    term = f"%{args.query}%"
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
        SELECT id, timestamp, command, tags FROM commands
        WHERE command LIKE ? OR tags LIKE ? OR notes LIKE ?
        ORDER BY id DESC
        """, (term, term, term))
        rows = c.fetchall()

        if not rows:
            console.print("[yellow]No matching commands found.[/yellow]")
            return

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("ID", style="dim")
        table.add_column("Time", width=19)
        table.add_column("Command")
        table.add_column("Tags", style="cyan")

        for row in rows:
            table.add_row(str(row[0]), row[1][:19], row[2], row[3] or "")
        console.print(table)

# --- CLI Setup ---

def main():
    init_db()
    parser = argparse.ArgumentParser(description="Command Vault — Save and annotate shell commands")
    subparsers = parser.add_subparsers(dest="command")

    # save
    save = subparsers.add_parser("save", help="Save a command to the vault")
    save.add_argument("command", help="Command to save")
    save.add_argument("--tag", help="Optional tags")
    save.add_argument("--note", help="Optional note")
    save.add_argument("--capture-output", action="store_true", help="Capture stdout of command")
    save.set_defaults(func=save_command)

    # list
    list_cmds = subparsers.add_parser("list", help="List recent saved commands")
    list_cmds.add_argument("--limit", type=int, default=10, help="Number of entries to show")
    list_cmds.set_defaults(func=list_commands)

    # view
    view = subparsers.add_parser("view", help="View a specific command by ID")
    view.add_argument("id", type=int, help="ID of the command")
    view.set_defaults(func=view_command)

    # search
    search = subparsers.add_parser("search", help="Search saved commands")
    search.add_argument("query", help="Search term")
    search.set_defaults(func=search_commands)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()



⸻

Optional: Add alias

To make it easier to use:

echo "alias vault='python3 /nfs/home/$USER/.cmdvault/cmdvault.py'" >> ~/.bashrc
source ~/.bashrc

Then just run:

vault save "docker restart nginx" --tag prod --note "fixes config"
vault list
vault view 1
vault search nginx



⸻

Want to Add Next?
	•	Support for vault export
	•	Auto-tagging by project directory
	•	Fuzzy finder (fzf) search
	•	Daily/weekly digest
	•	Sharing vault entries via NFS

Let me know how you want to expand it—and I’ll drop in the next module.