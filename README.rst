===============
aws-assume-role
===============

Build
=====

**Requirements before build**

* Python + 3.9 (can use pyenv)
* Poetry + 1.3 (can install using pip on venv)

**Build steps**

* Clone the project using ``git clone git@github.com:amoncusir/aws-assume-role.git``
* Install project dependencies with poetry ``poetry install``
* Run build process using Make (only can build in our same arch)
    * In MacOS x86: ``make build_mac_x86``
    * In MacOS ARM: ``make build_mac_arm``
* Copy the folder ``dist/<OS>/<ARCH>/main`` on our local home path, like
  ``cp dist/mac/arm/aws-assume-role $HOME/.aws-assume-role/bin``
* Create a link to point the *aws-assume-role* binary to the classpath (Warning! Isn't recommend to add the complete folder to the
  classpath!)
* Run ``aws-assume-role -h`` and verify it is installed!

TBD: Upload builds on GitHub

Usage
=====

Program Help ::

    usage: main.py [-h] [-s] [--configure] [-l] [-r REGION]
                   [--config-path CONFIG_PATH]
                   [profile]

    positional arguments:
      profile               The profile name on your config file

    optional arguments:
      -h, --help            show this help message and exit
      -s, --session         Not modify the aws config file and export the aws
                            credentials variables
      --configure           Start the configuration process and ignore other
                            parameters
      -l, --list            List all profiles
      -r REGION, --region REGION
                            Override the region parameter over the configuration
                            file
      --config-path CONFIG_PATH
                            Set the configuration file path (default:
                            /Users/<home_dir>/.aws_assume_role.config)

Configuration
=============

TBD

Environment Variables
=====================

* **ASSUME_AWS_SHARED_CREDENTIALS_FILE**
    * TBD
* **ASSUME_AWS_CONFIG_FILE**
    * TBD
* **ASSUME_AWS_PROFILE**
    * TBD

