Great use case! Since you’re trying to find the threshold number where the bug starts (not a specific commit), we can hack git bisect to binary search on a number, rather than commits.

Even though git bisect is designed for commits, you can still use it by combining it with a script that:
	1.	Changes the number in the file to a test value.
	2.	Runs your program and checks for the bug.
	3.	Exits with code 0 if good (no bug), 1 if bad (bug), and 125 to skip.

⸻

Step-by-Step Solution

1. Create a temporary test script (call it check_bug.sh):

#!/bin/bash

NUMBER=$1
FILE=your_file_with_the_number.txt  # Change this to your actual file

# Update the file with the test number
sed -i "s/^NUMBER=.*/NUMBER=$NUMBER/" "$FILE"

# Run your program or test
./run_program.sh  # Replace this with the actual command to run

# Check the output to determine if the bug is present
# You need to customize this part:
if grep -q "BUG DETECTED" output.log; then
    exit 1  # Bad (bug present)
else
    exit 0  # Good (bug not present)
fi

Make sure to:
	•	Make it executable: chmod +x check_bug.sh
	•	Define NUMBER=... on a separate line in your file for easy replacement, or adjust sed accordingly.

⸻

2. Write a wrapper script to use git bisect-style search (call this number_bisect.sh):

#!/bin/bash

LOW=0
HIGH=377

while [[ $LOW -lt $HIGH ]]; do
  MID=$(( (LOW + HIGH) / 2 ))
  echo "Testing with NUMBER=$MID"
  
  ./check_bug.sh $MID
  RESULT=$?

  if [ $RESULT -eq 1 ]; then
    # Bug is present, search lower
    HIGH=$MID
  else
    # No bug, search higher
    LOW=$((MID + 1))
  fi
done

echo "Smallest number where bug appears: $LOW"

Make this script executable too.

⸻

Then run it:

./number_bisect.sh



⸻

This script mimics git bisect, but for numeric thresholds, and automates the process of changing the file, testing, and narrowing the range.

Want help modifying it to suit your exact file format or output format of your program?