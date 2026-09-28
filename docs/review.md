# Self-review
## Infrastructure
* Make sure to use non-root user for running containers, this will reduce issue with file permissions (and is often the recommended and more secure way of running containers)
* Make sure to use non-root user for db user
* Environment based configuration, for example:
  * Dev may only have the vite-based web server and python debugger
  * Prod may have compiled react or even compiled python

## Devops
* Make ci/cd pipeline
  * Use environment based parameters
  * Use a set list of secure (and reviewed) docker containers
  * Security checks: Include DAST/SAST/SCA and secret scanning
  * Access controls to protect main/val branches
  * General checsk: formatting/linting, type checks, unit tests, dependency scanning

## DB
* Configure proper roles/permission following principle of least privelege
* Decompose tables into schemas as appropriate

## Misc
* The project as a whole should be decomposed both structurally (BE/FE) and conceptually (give some thought to the directory structure/linting/formatting)