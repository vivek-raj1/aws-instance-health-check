# AWS Instance Health Check 
This script appears to be a Python script that uses the Boto3 library to manage AWS resources. Specifically, it checks the health status of EC2 instances, takes actions based on the status, and sends alerts to a Slack channel via a webhook URL.

The script first imports the necessary modules such as Boto3, urllib3, json, and os. Then, it defines several variables by getting the values of environment variables that contain Slack webhook URLs and channel names. The script then initializes the EC2 client using the Boto3 session client.

The main function of the script, check_instance(), retrieves the instance status using the describe_instance_status() method of the EC2 client. It checks if the instance status is not 'ok', 'initializing', or 'insufficient-data'. If so, it appends the instance information, such as its ID, private IP address, and instance and system status, to a list of failed status instances.

The script then calls another function, describe_instance(), which retrieves instance information using the describe_instances() method of the EC2 client. It checks the instance tag and determines the instance's role as either an 'eks-node' or 'standalone-node'. It then appends the instance information to a list of alerts.

Another function, stop_instance(), is called for each alert in the list of alerts. This function stops the instance using the stop() method of the EC2 instance resource. If the instance is an 'eks-node', it simply stops the instance. If the instance is a 'standalone-node', it first waits for the instance to stop and then starts it again using the start() method of the EC2 instance resource.

Finally, the alert_trigger() function sends a Slack alert containing the instance information to the specified channel using the webhook URL.

- `Up-to-date dependencies`
- Python
- boto3
- slack

  

## ✨ Start the app

> **Step 1** - Download the code from the GH repository (using `GIT`) 

```bash
$ # Get the code
$ git clone https://github.com/vivek-raj-1/aws-instance-health-check.git
$ cd aws-instance-health-check
```

<br />

> **Step 2** - mv `env.sample` to `.env` and change value accordingly . 

```txt
mv env.sample .env

```

<br />

> **Step 3** - Run the APP in `Unix`/`Docker`/`Kubernetes`

>> Install modules via `VENV`  For unix

```bash
$ virtualenv env
$ source env/bin/activate
$ pip3 install -r requirements.txt
```

<br />

>> Run Script

```bash
$ python app.py
```

<br />

>> Build Docker image for docker & Kubernetes

```bash
$ docker build -t aws-instance-health-check .
$ docker run -e SLACK_WEBHOOK_URL=<your_slack_webhook_url> -e CHANNEL_NAME=<your_slack_channel_name> <image_name>
```

<br />



## ✨ Set up the crontab

> **Step 1** - Open the terminal on your Linux system.

<br />

> **Step 2** - Type the following command to open the crontab file

```
crontab -e
```

<br />

> **Step 3** - Enter the command or script that you want to schedule and specify the time and frequency you want it to run using the crontab syntax. For example, the following line will run the script /home/user/my-script.sh every day at 2 min:

```
*/2 * * * * /home/user/aws-instance-health-check/app.py
```

<br />

> **Step 4** - Save the file and exit the editor and Verify that the cron job has been added by running the following command:

```
crontab -l
```

<br />


## ✨ Code-base structure

The project is coded using a simple and intuitive structure presented below:

```bash
< PROJECT ROOT >
    ├── Dockerfile
    ├── README.md
    ├── app.py                                      # Instance Health Check Script
    ├── env.sample                                  # Inject Configuration via Environment
    └── requirements.txt                            # Development modules
    |-- ************************************************************************
```

<br />

