Overview
========
Alexa skill for parsing data from the Fredericton francophone school district [web site](https://francophonesud.nbed.nb.ca/retards-et-fermetures) and reporting on bus delays and school closures.

Developer Notes
===============

Publishing
----------

To deploy the skill and the associated Python / AWS back end, you should use the ask-cli command line tool. Further, this tool generates an aws package for lambda function that drives the skill. Unfortunately, since this package is generated on the local machine you need to run this tool under the same environment (ie: os and runtime dependencies) as that used in the AWS cloud where the lambda is to be run. To compensate for this limitation you need to use a Docker container to run the tool. Thus, deploying the package must be done as follows

1. make sure you have Docker installed
2. run Docker build from the ./docker folder (ie: docker build -t alexa_test .)
3. from the root folder of the project, launch the docker container as follows: docker run -it -v $PWD/ask_config:/root/.ask -v $PWD:/workspace -w /workspace --rm  alexa-test /bin/bash.

   * this will make mount the current working folder to /workspace in the container, make that folder the default working folder, and mount a new ./ask_config folder from the local workspace to the /root/.ask folder, so that credentials for the ask-cli client can be preserved between runs
   
4. configure the ask-cli client with credentials for AWS: ask configure --no-browser (follow the prompt)
5. Initialize the project workspace: ask init

   * enter the ID for the skill as found in the Alexa Skills Console
   * skill package path: default (./skill-package)
   * lambda code path: default (./lambda)
   * Use AWS CloudFormation: no
   * Lambda Runtime: python3.8
   * Lambda Handler: index.handler

6. run the deploy operation: ask deploy 

More info can be found [here](https://developer.amazon.com/en-US/docs/alexa/smapi/quick-start-alexa-skills-kit-command-line-interface.html) and [here](https://developer.amazon.com/en-US/docs/alexa/smapi/manage-credentials-with-ask-cli.html#create-aws-credentials).

TIP: to deploy just the skill metadata do: ask deploy -t skill-metadata


Misc
----

Status info for the Alexa lambda functions can be seen [here](https://console.aws.amazon.com/lambda/home?region=us-east-1#/discover).

Status info for the Alexa skill can be seen [here](https://developer.amazon.com/alexa/console/ask)

if the lambda function gets broken and you need to redeploy, you'll need to do the following:

1. edit the skill-package/skill.json file
2. in the "apis" / "custom" node, delete the "endpoint" node
3. (needed?) rebuild ask-cli config: ask init (see above)
4. rerun publish: ask deploy
5. this should regenerate the lambda function and update the skill.json with the new endpoint URL

to publish a new interaction model without deploying everything, do the following:

publish interactions: ask smapi set-interaction-model -s <SKILL_ID> -l en-CA --interaction-model "$(cat ./skill-package/interactionModels/custom/en-CA.json)"

other helpful tools:

* AWS cli application (to upload lambda): https://aws.amazon.com/cli/
* AWS SAM cli application (to build lambda package): https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html


Notable Points
--------------
* the ask-cli prompts for a "handler" to use with your alexa skill. This name apparently maps, loosely, to the entrypoint script of your lambda function, with a ".handler" suffix. So if your entry point script is "fubar.py" then the associated handler for that is "fubar.handler"