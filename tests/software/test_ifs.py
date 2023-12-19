import os
import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

from simlab.software.ifs import IFS


class TestIFS(unittest.TestCase):
    def setUp(self):
        # Set up a mock environment for the test
        self.mock_cortex_dir = "/mock/cortex/dir"
        self.mock_build_type = "TestBuildType"

        # Set up environment variables
        os.environ["CORTEX_DIR"] = self.mock_cortex_dir

        # Create an instance of IFS
        self.ifs = IFS()

        # Mock the external dependencies
        self.ifs.read_config = MagicMock()
        self.ifs.config = {"IFS": {"BuildType": self.mock_build_type}}

    def test_setup(self):
        # Mock os.chdir and subprocess.run
        with mock.patch("os.chdir") as mock_chdir, mock.patch(
            "subprocess.run"
        ) as mock_run:
            # Call the setup method
            self.ifs.setup()

            # Ensure os.chdir was called with the correct arguments
            mock_chdir.assert_called_with(
                Path(f"{self.mock_cortex_dir}/JCT/IFS/PROJECTS/IFS")
            )

            # Ensure subprocess.run was called with the correct arguments
            expected_bootstrap_call = [
                Path(f"{self.mock_cortex_dir}/JCT/IFS/bootstrap.sh"),
                self.mock_build_type,
            ]
            mock_run.assert_any_call(expected_bootstrap_call, check=True)

    def test_run_program(self):
        # Mock os.chdir and subprocess.run
        with mock.patch("os.chdir") as mock_chdir, mock.patch(
            "subprocess.run"
        ) as mock_run:
            # Call the run_program method
            self.ifs.run_program(self.ifs.config)

            # Ensure os.chdir was called to change to the run directory
            mock_chdir.assert_called_with(self.ifs.run_path)

            # Assert that subprocess.run was called with expected arguments
            # You can build expected_run_command based on your ifs_config.ini
            expected_run_command = ["..."]  # Replace with the expected command
            mock_run.assert_called_with(expected_run_command, check=True)

    # Add more tests as needed...

    def tearDown(self):
        # Clean up any changes made to the environment
        del os.environ["CORTEX_DIR"]


if __name__ == "__main__":
    unittest.main()
