"""
Download the latest versions of all installed VSCode extensions with cURL.
TODO: Add option to automatically install all the downloaded extensions.
TODO: Add option to provide any list of extensions, not just the installed ones.
TODO: Update to allow for specifying extension version (but default to latest version).
TODO: Update to check for directory existence (and make one if it doesn't exist).
"""

import os

def vsix_url(extension):
    """
    Gets the URL for a .vsix VSCode extension, given the full name
    of the extension in the format of {publish}.{package}
    ex: ms-python.python
    """
    publisher, package = extension.split('.')
    return 'https://{publisher}.gallery.vsassets.io/_apis/public/gallery/publisher/{publisher}/extension/{package}/latest/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage'.format(publisher=publisher, package=package)

def vsix_curl(extension, url, output_dir):
    """
    Builds and returns the cURL command to download a vscode extension 
    to a spexified directory and filename.
    """
    return 'curl {} -o {}/{}.vsix'.format(url, output_dir, extension)


#
# Example Usage
#

# get a list of all installed extensions
extensions = os.popen('code --list-extensions').read().splitlines()
output_dir = './extensions'

# download each of the extensions and place them in a specified directory.
for ext in extensions:
    url = vsix_url(ext)
    cmd = vsix_curl(ext, url, output_dir)
    os.system(cmd)