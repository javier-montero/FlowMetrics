# Self-review
## Infrastructure
* Make sure to use non-root user for running containers, this will reduce issue with file permissions (and is often the recommended and more secure way of running containers)
## Devops
* Make ci/cd pipeline
  * Use environment based parameters
  * Use a set list of secure (and reviewed) docker containers