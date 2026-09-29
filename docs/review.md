# Self-review

## Production readiness
* This project is currently entirely "development" focused and to bring it up to a "production-ready" state you would need to do the following:
  * Backend
    * Gunicorn + Uvicorn, instead of what we currently do which is just Gunicorn (with live reload)
      * This is the suggested production stack
    * Some thought should also be given to things like directory strucutre, formatting, type checking (as much as you can for Python)
    * Configuration specifics, like:
      * CORS
      * Headers
      * Access controls
  * Frontend (including webserver):
    * Currently the frontend uses vite as a webserver, the way it should work is a proper webserver (like Caddy/Nginx/Apache) is setup to proxy request to the API application
      * Something like Caddy serving static content and proxying backend requests to Gunicorn/Uvicorn
    * Potentially, loadbalancer as well
  * DB
    * Follow the principle of least privelege, in other words, the following:
      * Service accounts
      * Proper roles
      * Proper permissions
      * Segregated schemas for given purpose
    * Version controlled migration scripts (my thoughts on this is that tables/schemas/grants/stored procs/etc should all be version controlled)
      * Including both create and rollback scripts
  * Devops:
    * CI/CD pipeline with the following:
      * Env based config (and static artifcats)
      * Managed secrets
      * Standardized docker images (ideally that have been reviewed for security vulnerabilites)
      * Security: DAST/SAST/SCA scans
      * Testing: automated unit/integration/end-to-end testing as well as frontend testing
      * Other: I'm not exactly a devops expert there is more than can go into this
    * Use non-root users
      * There are many many reasons to do this, for example:
        * Escalation of priveleges
        * File permission issues
        * Increased attack surface
* This project is essentially just a demo, it doesn't include any actual ingestion endpoints or functionality, we need for both SLURM and NextFlow.
* This project also doesn't include logs, metrics, or alerting which would all be desired features for a tool like this.
  * There are better tools for all of those features so it would likely be either linking in this interface or aggregation/display.

## Testing and QA
* So this project currently doesn't have any unit testing (testing was done manually given the time constraints). Alot of todos here:
  * Backend:
    * Run/sample filtering and pagination
    * Missing-resource responses
    * Workflow status aggregation
    * Sample-to-execution-to-SLURM relationships
  * Frontend:
    * Loading/error states
    * Main drill-down paths
  * DB:
    * Dev and/or val environment to test create and rollback procedure (ideally every change should be reversabile and tested as such)

## Readability and maintainability
* Typically I seperate backend and frontend repos but in this project the boundaries are easy to find.
* I organized the repo into a "domain-oriented" directory strutcure so it should be fairly readible at a glance. In other words, the backend and frontend are structured so that its clear where the script that you're looking for is (or belongs if you're writing).
* The seed data also makes the intended relationships between tables concrete (and I included an ERD diagram in the README if you disagree).
* Some functionality is shared between features but in general I hold to the idea that code should be kept simple. In other words, there is plenty of reusability but I didn't overly-constrain the project so there is some redundancy here (see run_workflow in backend or stylesheets in frontend). This would allow me to add features without having to worry that a change in one place is going to effect a different feature.
* There is also documentation for the backend http://localhost:8000/docs. 

## Strengths, weaknesses, and gaps
* Strength: The core model separates workflows, processes, runs, samples, task executions, and SLURM jobs. Task-to-sample-to-job relationships are explicit rather than inferred from timestamps (in an earlier version, before I read up on SLURM, relationships were derived from timestamps).
* Strength: The seeded dataset is reproducible and covers varied run states. This makes the UI easy to demonstrate without depending on a cluster.
* Strength: The API uses typed request/response models, bounded pagination, and a service/router split. The React app has feature-level organization and typed API data contracts.
* Strength: The runs, workflow, and samples views cover the main operator drill-downs. Loading, error, retry, search, and pagination states are present in the UI.
* Weakness: This is a very opinionate workflow, in other words, it depends on a hierarchical relationship between runs and samples and it expects the use of SLURM and Nextflow (specifically the SLURM executor, so this wouldn't work for a jerry-rigged solution)
* Gaps:
  * Not production ready at all (see above)
  * No automated testing
  * No CI/CD