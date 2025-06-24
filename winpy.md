To run a Python script automatically at 5 AM Monday–Friday on Windows with Anaconda, you can use Task Scheduler and set it up to use your Anaconda environment.

⸻

✅ Step-by-step Instructions

1. Prepare Your Script

Let’s say your script is located at:

C:\Users\YourName\Documents\scripts\my_script.py

2. Find Your Anaconda Environment’s Python Path

Open Anaconda Prompt, activate your environment, and run:

where python

This gives you the full path to the python.exe inside your Anaconda environment, e.g.:

C:\Users\YourName\anaconda3\envs\myenv\python.exe


⸻

3. Open Task Scheduler
	•	Press Win + R, type taskschd.msc, and press Enter.
	•	In the right pane, choose Create Task.

⸻

4. Create the Task

📌 General Tab
	•	Name: Run Python Script at 5AM
	•	Run whether user is logged on or not
	•	Check “Run with highest privileges”

📌 Triggers Tab
	•	Click New…
	•	Begin the task: On a schedule
	•	Settings: Weekly
	•	Check: Monday, Tuesday, Wednesday, Thursday, Friday
	•	Start time: 5:00 AM
	•	Click OK

📌 Actions Tab
	•	Click New…
	•	Action: Start a program
	•	Program/script: Paste the full path to your python.exe (from step 2)

C:\Users\YourName\anaconda3\envs\myenv\python.exe


	•	Add arguments (optional):

"C:\Users\YourName\Documents\scripts\my_script.py"



📌 Conditions Tab

(optional, but helpful)
	•	Uncheck “Start the task only if the computer is on AC power” if using a laptop.

⸻

5. Test the Task
	•	Right-click your new task → Run to confirm it works.
	•	Check the script output (e.g. it logs to a file, updates something, etc.)

⸻

📝 Tips
	•	If your script uses environment variables or paths, use absolute paths in the script to avoid errors.
	•	If it writes logs, make sure the script has write permissions to the destination.
	•	You can also make the script output to a .log file to debug issues.

Let me know if you’d like a script that logs to a file or emails you when it runs.