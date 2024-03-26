import os
from multiprocessing import Process, Queue
import subprocess
import time

def run_cpp_program(queue, run_directory, executable, *args):
    """
    Runs a C++ program from a given directory with optional arguments.
    """
    print(f"Starting {executable} in {run_directory}")
    # Change the current working directory to the run_directory
    os.chdir(run_directory)
    # Construct the command with the executable and any arguments
    command = [f"./{executable}"] + list(args)
    # Execute the command
    process = subprocess.Popen(command)
    # Send the PID to the main process
    queue.put(process.pid)
    # Wait for the process to complete
    process.wait()
    print(f"Process {executable} finished.")

def control_menu(programs, queues):
    while True:
        print("\nMenu:")
        print("1. Start all programs")
        print("2. Stop all programs")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            # Start all programs
            for program in programs:
                program.start()
            time.sleep(1)  # Give time for processes to start and send PIDs
        elif choice == "2":
            # Stop all programs
            for q in queues:
                while not q.empty():
                    pid = q.get()
                    try:
                        os.kill(pid, signal.SIGTERM)
                        print(f"Process with PID {pid} terminated.")
                    except Exception as e:
                        print(e)
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    import signal
    # Define your C++ programs' directories and command-line arguments
    program_details = [
        ("/path/to/dir1", "program1", "arg1", "arg2"),
        ("/path/to/dir2", "program2", "arg1"),
        ("/path/to/dir3", "program3"),
        ("/path/to/dir4", "program4", "arg1", "arg2", "arg3")
    ]

    queues = [Queue() for _ in program_details]
    programs = [Process(target=run_cpp_program, args=(q, *details)) for q, details in zip(queues, program_details)]

    control_menu(programs, queues)