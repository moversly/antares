# Antares Service

Welcome to the Developer Guide for AWS Lambda Function! This guide will help you get started with development of lambda function in aws using python.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setting Up Your Development Environment](#setting-up-your-development-environment)
- [Testing the fuction locally](#testing-the-fuction-locally)
- [Deployment](#deployment)

## Prerequisites

Before you can work with this project, make sure you have the following prerequisites installed:

1. **AWS Command Line Interface (CLI)**: Install and configure the AWS CLI on your local machine. The AWS CLI allows you to interact with AWS services, including SAM and CDK.

   - **Install the AWS CLI**: Follow the instructions in the [AWS CLI documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).

   - **Configure the AWS CLI**: Use the `aws configure` command to set your AWS access key, secret access key, default region, and output format.

2. **Serverless Application Model (SAM)**: SAM is a framework for building serverless applications on AWS. Install SAM using the official instructions in the [SAM documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html).

3. **AWS CDK (Cloud Development Kit)**: CDK is a framework for defining cloud infrastructure as code. Install CDK using the official instructions in the [CDK documentation](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html).

4. **Docker**: If you plan to work with containers or run applications in Docker, install Docker by following the instructions on the [Docker website](https://docs.docker.com/get-docker/).

5. **Python and Node.js**: Ensure you have Python and Node.js installed on your development machine, as they are commonly used for CDK and SAM development.

6. **Virtual Environment (Python)**: For Python development, it's a good practice to create and activate a virtual environment using `virtualenv` or `venv` to manage dependencies.

Make sure to verify that you have met these prerequisites before working with the project. These tools are essential for developing, testing, and deploying serverless applications and cloud infrastructure.

## Setting Up Your Development Environment

Create a new CDK app by using the following command :

```shell
cdk init app --language python
```

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project. The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory. To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

### Useful commands

- `cdk ls` list all stacks in the app
- `cdk synth` emits the synthesized CloudFormation template
- `cdk deploy` deploy this stack to your default AWS account/region
- `cdk diff` compare deployed stack with current state
- `cdk docs` open CDK documentation

## Testing the fuction locally

Run the following command to locally invoke the lambda function.

```shell
sam loacl invoke -t ./cdk.out/your-local-stack.template.json
```

TO Generate a test event run the following command , example for sns notification :

```shell
sam local generate-event sns notification
```

Which will generate a test event and can be copied ,modified and stored in a file names as events as event_name.json.

To Run the function locally using the test event you created use the following command :

```shell
sam loacl invoke -t ./cdk.out/your-local-stack.template.json -e ./events/event_name.json
```

### Deployment

Use the following command to deploy your lambda function to AWS.

```shell
sam deploy --guided
```

we can type in the stack name, aws region etc in the cli and confirm the changes.
