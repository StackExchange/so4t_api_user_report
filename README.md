# Stack Overflow for Teams API User Report (so4t_api_user_report)
A Python script that uses the Stack Overflow for Teams API creates a CSV report of how well each user performs. You can see an example of what the output looks like in the Examples directory ([here](https://github.com/StackExchange/so4t_user_report/blob/main/Examples/user_metrics.csv)).

## Table of Contents
* [Requirements](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#requirements)
* [Setup](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#setup)
* [Basic Usage](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#basic-usage)
* [Advanced Usage](https://github.com/StackExchangeo/so4t_api_user_report?tab=readme-ov-file#advanced-usage)
  * [`--start-date` and `--end-date`](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#--start-date-and---end-date)
  * [`--no-api`](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#--no-api)
* [Support, security, and legal](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#support-security-and-legal)

## Requirements
* A Stack Overflow for Teams instance (Basic, Business, or Enterprise); for Enterprise, version 2023.3 or later
* Python 3.8 or higher ([download](https://www.python.org/downloads/))
* Operating system: Linux, MacOS, or Windows

If using the `--web-client` argument, there are additional requirements (details in [Advanced Usage](https://github.com/StackExchange/so4t_api_user_report#--web-client) section)

## Setup

[Download](https://github.com/StackExchange/so4t_api_user_report/archive/refs/heads/main.zip) and unpack the contents of this repository

**Installing Dependencies**

* Open a terminal window (or, for Windows, a command prompt)
* Navigate to the directory where you unpacked the files
* Install the dependencies: `pip3 install -r requirements.txt`

**API Authentication**

For the Business tier, you'll need a [personal access token](https://stackoverflowteams.help/en/articles/4385859-stack-overflow-for-teams-api) (PAT). You'll need to obtain an API key and an access token for Enterprise. Documentation for creating an Enterprise key and token can be found within your instance at this url: `https://[your_site]/api/docs/authentication`

**Before proceeding, please note a critical step when creating your API Application in Stack Overflow Enterprise for Access Token generation:**

**Generating an Access Token**

To generate an Access Token for Enterprise, you must first ensure your API Application is correctly configured:

* **API Application "Domain" Field Requirement:** When creating your API Application (where you obtain your Client ID and Client Secret), the "Domain" field *must* be populated with the base URL of your Stack Overflow Enterprise instance (e.g., `https://your.so-enterprise.url`). **Although the UI may mark this field as 'Optional,' failure to populate it will prevent Access Token generation and lead to a `"redirect_uri is not configured"` error during the OAuth flow.**

Once your API Application is configured with a valid Domain, follow these steps to generate your Access Token:

* Go to the page where you created your API key. Take note of the "Client ID" associated with your API key.
* Go to the following URL, replacing the base URL, the `client_id`, and the base URL of the `redirect_uri` with your own:
`https://YOUR.SO-ENTERPRISE.URL/oauth/dialog?client_id=111&redirect_uri=https://YOUR.SO-ENTERPRISE.URL/oauth/login_success`
* You may be prompted to log in to Stack Overflow Enterprise if you're not already. Either way, you'll be redirected to a page that simply says "Authorizing Application"
* In the URL of that page, you'll find your access token. Example: `https://YOUR.SO-ENTERPRISE.URL/oauth/login_success#access_token=YOUR_TOKEN`

**Note on Access Token Requirements:**
While API v3 now generally allows querying with just an API key for most GET requests, certain paths and data (e.g., `/images` and the email attribute on a `User` object) still specifically require an Access Token for access. If you encounter permissions errors on such paths, ensure you are using an Access Token.

## Basic Usage

In a terminal window, navigate to the directory where you unpacked the script. 
Run the script using the following format, replacing the URL, token, and/or key with your own:
* For Basic and Business: `python3 so4t_user_report.py --url "https://stackoverflowteams.com/c/TEAM-NAME" --token "YOUR_TOKEN"`
* For Enterprise: `python3 so4t_user_report.py --url "https://SUBDOMAIN.stackenterprise.co" --key "YOUR_KEY" --token "YOUR_TOKEN"`

The script can take several minutes to run, particularly as it gathers data via the API. As it runs, it will continue to update the terminal window with the tasks it's performing.

When the script completes, it will indicate that the CSV has been exported, along with the file name. You can see an example of what the output looks like [here](https://github.com/StackExchange/so4t_api_user_report/blob/main/Examples/user_metrics.csv).

## Advanced Usage

As described below, you can add some additional arguments to the command line to customize the script's behavior. All arguments (and instructions) can also be found by running the `--help` argument: `python3 so4t_user_report.py --help` 

### `--start-date` and `--end-date`

By default, the CSV report aggregates all historical data for users. If you'd like to filter this based on a certain amount of history, the `--start-date` and `--end-date` arguments allow you to take a slice of that history. Using these arguments would look like this:
`python3 so4t_user_report.py --url "https://SUBDOMAIN.stackenterprise.co" --key "YOUR_KEY" --token "YOUR_TOKEN" --start-date "2022-01-01" --end-date "2022-12-31"`
* The date format is `YYYY-MM-DD`. 
* When using a start date without an end date, the script will use the current date as the end date.
* When using an end date without a start date, the script will use the earliest date available in the data as the start date.

### `--no-api`

In conjunction with the `--start-date` and `--end-date` arguments, `--no-api` allows you to leverage preexisting JSON data from previous executions of this script. This is significantly faster than running all the API calls again; in fact, it's nearly instantaneous. If you were looking to generate user metrics based on a variety of time ranges, using the `--no-api` argument significantly speeds up the process. 

Using `--no-api` would look like this: `python3 so4t_user_report.py --no-api --start-date "2022-01-01" --end-date "2022-12-31"`

> Note: when using `--no-api`, the `--url`, `--key`, and `--token` arguments are unecessary. When you'd like to update the JSON data via fresh API calls, simply remove the `no-api` argument and add back the required authentication arguments.

## Support, security, and legal
If you encounter problems using the script, please leave feedback in the Github Issues. You can also clone and change the script to suit your needs. It is provided as-is, with no warranty or guarantee of any kind.

All data is handled locally on the device from which the script is run. The script does not transmit data to other parties like Stack Overflow. All API calls performed are read-only, so there is no risk of editing or adding content to your Stack Overflow for Teams instance.
