To run your Python script at the same time every day on Windows using Task Scheduler, you can automate this in a few ways — including launching it through the Anaconda Prompt, just like you do manually.

Here’s how to set it up step-by-step, assuming:
	•	You have Anaconda installed.
	•	You normally open the Anaconda Prompt and type python script.py manually.
	•	You want this to happen automatically at a specific time every day.

⸻

✅ Option 1: Run Script Using conda Environment via Task Scheduler

🧩 Step 1: Create a .bat File

You’ll wrap your Python script in a batch file that:
	1.	Opens the Anaconda environment
	2.	Runs your script

Example run_my_script.bat:

@echo off
REM Activate your conda environment (replace "myenv" with your actual env name)
CALL "%USERPROFILE%\anaconda3\Scripts\activate.bat" myenv

REM Navigate to the script directory
cd /d "C:\path\to\your\script"

REM Run your Python script
python script.py

🔁 Replace:
	•	"myenv" with your environment name (e.g., base, datasci, etc.)
	•	"C:\path\to\your\script" with your actual script path

💡 You can test this batch file by double-clicking it to make sure it works.

⸻

⏰ Step 2: Create a Scheduled Task
	1.	Open Task Scheduler
	2.	Click Create Basic Task
	3.	Name it (e.g., Run My Python Script)
	4.	Choose Daily and set your desired time
	5.	Action: Select Start a program
	6.	In Program/script:
Type the path to the .bat file you just created, e.g.:

"C:\Users\YourName\Desktop\run_my_script.bat"


	7.	Finish setup

⸻

✅ Option 2: Directly Run Python from Conda Path (No .bat)

If you don’t want to use a .bat file, you can run Python from your conda environment directly in the scheduled task:
	1.	Find the full path to python.exe in your conda environment:

C:\Users\YourName\anaconda3\envs\myenv\python.exe


	2.	Create a task with:
	•	Program/script:

C:\Users\YourName\anaconda3\envs\myenv\python.exe


	•	Add arguments:

C:\path\to\your\script\script.py


	•	Start in:

C:\path\to\your\script\



⚠️ This bypasses conda activate, so make sure all necessary packages are installed in that env.

⸻

🔎 Troubleshooting Tips
	•	Log output: Add this to your .bat to see logs:

python script.py > log.txt 2>&1


	•	Check permissions: Make sure your user has permission to run at that time.
	•	Use full paths: Always use absolute paths in your script and .bat file to avoid issues.

⸻

🧪 Bonus: Use taskschd.msc (Advanced Options)
	•	Use “Create Task” instead of “Create Basic Task” if you want:
	•	To run even when not logged in
	•	To hide the window
	•	To add retry/restart settings

⸻

Would you like me to generate a .bat file or task XML for you automatically if you tell me your script path and environment name?