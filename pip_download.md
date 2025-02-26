To download a package with pip for multiple versions, ensuring that only the source distribution (.tar.gz, .zip, etc.) is downloaded (no wheels), and including all dependencies recursively, follow these steps.

1. Download a Specific Version as Source Only

Use --no-binary :all: to force pip to download only the source distribution.

pip download --no-binary :all: package_name==version

Example:

pip download --no-binary :all: requests==2.25.1

This will download the source distribution for requests==2.25.1 along with its dependencies recursively.

2. Download Multiple Versions

You can specify multiple versions by running pip download multiple times.

Example:

pip download --no-binary :all: requests==2.25.1
pip download --no-binary :all: requests==2.26.0
pip download --no-binary :all: requests==2.27.1

Or use a loop in Bash:

for version in 2.25.1 2.26.0 2.27.1; do
    pip download --no-binary :all: requests==$version
done

3. Download a List of Packages and Versions from a File

If you have a list of package versions in a requirements.txt file:

requests==2.25.1
requests==2.26.0
requests==2.27.1

You can download all versions at once:

pip download --no-binary :all: -r requirements.txt

4. Verify Dependencies Are Downloaded

By default, pip download will fetch dependencies, but if you want to ensure recursive downloading:

pip download --no-binary :all: package_name==version --no-deps
pip download --no-binary :all: -r <(pip show package_name | awk '/Requires:/ {print $2}' | tr ',' '\n')

Or explicitly specify:

pip download --no-binary :all: package_name==version --no-deps
pip download --no-binary :all: -r <(pip show package_name | grep Requires | cut -d: -f2 | tr ',' '\n')

5. Store Downloads in a Specific Directory

By default, pip will download the packages to the current directory. If you want to store them in a folder, use:

pip download --no-binary :all: -r requirements.txt -d ./packages

6. Example: Download Different Versions of Flask

pip download --no-binary :all: flask==2.0.0
pip download --no-binary :all: flask==2.1.0
pip download --no-binary :all: flask==2.2.0

Or using a loop:

for version in 2.0.0 2.1.0 2.2.0; do
    pip download --no-binary :all: flask==$version
done

7. Check Available Versions Before Downloading

To check which versions of a package are available:

pip index versions package_name

Example:

pip index versions requests

Final Thoughts
	•	--no-binary :all: ensures only source distributions are downloaded.
	•	pip download downloads dependencies recursively.
	•	Looping or using requirements.txt allows handling multiple versions.

Would you like to automate this further with a script? Let me know how I can refine this for your use case!

---

Since you’re preparing packages for an air-gapped network, it’s critical to verify that you have downloaded everything correctly. Here’s how you can confirm that your downloaded packages include all required source distributions and dependencies.

1. Verify All Files Are Source Distributions (.tar.gz / .zip)

Run this command inside your download directory to check if any wheel files (.whl) were mistakenly downloaded:

ls -1 *.whl

If it returns any results, some wheels were downloaded. You need to re-download the packages using:

pip download --no-binary :all: -r requirements.txt -d ./packages

To list only source distributions, run:

ls -1 *.tar.gz *.zip

2. Verify Dependencies Were Downloaded

Run the following inside the directory where you downloaded the packages:

pip install --no-index --find-links=./packages package_name --dry-run

Example:

pip install --no-index --find-links=./packages flask --dry-run

If there are missing dependencies, it will show an error message.

To verify dependencies recursively:

for package in $(ls ./packages/*.tar.gz | xargs -n1 basename | cut -d'-' -f1 | sort -u); do
    pip install --no-index --find-links=./packages $package --dry-run
done

If no errors appear, all dependencies are present.

3. Verify Package Hashes (Optional but Recommended)

To ensure no corruption or tampering, generate hashes:

pip hash ./packages/*

Save the hashes:

pip hash ./packages/* > hashes.txt

After transferring files to the air-gapped network, re-run:

sha256sum -c hashes.txt

If all files match, they are intact.

4. Simulate Installation in an Isolated Environment

Before transferring, test in a clean virtual environment:

python -m venv test_env
source test_env/bin/activate  # On Windows, use `test_env\Scripts\activate`
pip install --no-index --find-links=./packages package_name

Example:

pip install --no-index --find-links=./packages flask

If everything installs successfully, you’re good to go!

5. Transfer and Install on the Air-Gapped Machine

Transfer Files

Use a USB drive, DVD, or secure file transfer (if available). Ensure all .tar.gz and .zip files are copied.

Install in the Air-Gapped Environment

On the air-gapped system, navigate to where you stored the packages and run:

pip install --no-index --find-links=./packages -r requirements.txt

Final Checklist

✅ All files are .tar.gz or .zip (No .whl files)
✅ Dependencies are fully downloaded (pip install --dry-run check)
✅ Hashes match before and after transfer (sha256sum -c hashes.txt)
✅ Test installation in a virtual environment before transferring
✅ Successful installation in the air-gapped system using --no-index

Do You Need an Offline PyPI Mirror?

If you need a full offline repository, consider using devpi or bandersnatch to create a local PyPI mirror.

Let me know if you need help with setting that up!