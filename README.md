# Yourkit autoinstallation

The script automates the download/upkeep of the YourKit profiler, installing locally
and trying to inject the YJP path into a preexisting sh script file.

This script only automates download/suggestions of 32/64b x86 systems, which is
the major use case of a profile.

This is an very simple script due to the fact that more complexity is not needed for
my applications.

## Usage
`python3 yourkit-install.py [config file name]`

The script will detect and download the latest YourKit, unzip the archive, then attempt
to install the agentpath into the java start script.