You’re on the right track with measuring disk I/O via system calls. Here’s how you can approach this systematically on Linux:

1. Using strace (simplest and quickest):

strace will let you directly measure the number of disk-related system calls your program makes.

Run your program as follows:

strace -c ./your_program

This will show a summary table at the end of execution, something like:

% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 60.45    0.002349           3       832           read
 20.11    0.000781           5       164           write
...

	•	The calls column will indicate how many read and write syscalls your program makes.
	•	Large numbers of read calls typically mean data isn’t cached in RAM effectively.
	•	Small numbers could mean it is already cached or loaded into RAM effectively.

⸻

2. Using iotop (real-time monitoring):

iotop shows real-time disk usage of running processes:

sudo iotop -oP

	•	Run your program while monitoring to see if there’s heavy disk activity.
	•	Persistent, high disk activity confirms your data isn’t staying cached in RAM.

⸻

3. Using perf (advanced performance profiling):

perf allows more detailed profiling. First, install if not present:

sudo apt install linux-tools-common linux-tools-generic

Then profile your program’s system calls and cache misses:

sudo perf stat -e syscalls:sys_enter_read,syscalls:sys_enter_write ./your_program

You’ll get output like:

 Performance counter stats for './your_program':

             1,242      syscalls:sys_enter_read
               342      syscalls:sys_enter_write

      0.123456789 seconds time elapsed

This gives precise syscall counts.

⸻

4. Checking if your data file is cached in RAM directly:

Use vmtouch (install via package manager):

sudo apt install vmtouch

Check file cache status:

vmtouch /path/to/your/lookup_table

Example output:

           Files: 1
     Directories: 0
  Resident Pages: 500/500  1M/1M  100%
         Elapsed: 0.001 seconds

	•	100% means fully cached in RAM.
	•	Low percentage means it’s mostly staying on disk.

⸻

Recommendations to improve performance (if data isn’t cached):

If you see your data staying on disk and causing frequent reads:
	•	Load the data explicitly into RAM at startup by reading it into a memory structure.
	•	Use techniques like memory-mapped files (mmap()) to let the OS handle caching more efficiently.
	•	Consider an in-memory database or key-value store like Redis or SQLite with an in-memory option.

⸻

Which to use?
	•	Start with strace -c for immediate clarity on syscalls.
	•	Use vmtouch for direct cache verification.
	•	Use perf for deeper analysis and detailed insights.

This will clearly reveal if your large table is primarily stored in RAM or on disk, and whether explicitly loading it into RAM could significantly boost your performance.