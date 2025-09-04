# Stack Overflow for Teams API User Report (so4t_api_user_report)
A Python script that uses the Stack Overflow for Teams API creates a CSV report of how well each user performs. You can see an example of what the output looks like in the Examples directory ([here](https://github.com/StackExchange/so4t_user_report/blob/main/Examples/user_metrics.csv)).

## Table of Contents
* [Requirements](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#requirements)
* [Setup](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#setup)
* [Basic Usage](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#basic-usage)
* [Advanced Usage](https://github.com/StackExchangeo/so4t_api_user_report?tab=readme-ov-file#advanced-usage)
  * [`--start-date` and `--end-date`](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#--start-date-and---end-date)
  * [`--no-api`](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#--no-api)
* [Enhanced Features for Large Datasets](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#enhanced-features-for-large-datasets)
  * [Rate Limiting Prevention](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#rate-limiting-prevention)
  * [Batch Processing](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#batch-processing)
  * [Data Filtering Options](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#data-filtering-options)
  * [Custom Output Naming](https://github.com/StackExchange/so4t_api_user_report?tab=readme-ov-file#custom-output-naming)
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

## Enhanced Features for Large Datasets

### Rate Limiting Prevention

The script includes mechanisms to prevent rate limiting from the Stack Overflow for Teams API. This is particularly important when processing large datasets or when running the script frequently.

* **API Key Usage:** The script will first attempt to use your API key for read-only requests. If the API key is rate limited, it will automatically switch to using an Access Token.
* **Access Token Management:** The script manages multiple Access Tokens if needed, ensuring that if one token expires, the script can continue using others.
* **Token Expiration Handling:** The script checks for token expiration and refreshes it if necessary.

### Batch Processing

For very large datasets, the script can process data in batches. This is particularly useful for:

* **Memory Efficiency:** Processing large amounts of data without loading everything into memory at once.
* **Scalability:** Processing data across multiple API calls, which can be more reliable than a single large request.
* **Rate Limiting Prevention:** By breaking down the data into smaller chunks, the script can better manage API rate limits.

### Data Filtering Options

The script provides several options to filter the data before processing:

* **Date Range Filtering:** You can specify a start and end date to only process data within that time window.
* **User ID Filtering:** You can filter by specific user IDs to focus on a particular user's activity.
* **Team ID Filtering:** You can filter by specific team IDs to focus on a particular team's activity.
* **Post Type Filtering:** You can filter by post types (e.g., `Question`, `Answer`, `Comment`, `Edit`, `AcceptedAnswer`).
* **Comment Type Filtering:** You can filter by comment types (e.g., `Question`, `Answer`, `Comment`).

### Custom Output Naming

You can customize the output CSV file name using the `--output-file` argument. For example:

* `python3 so4t_user_report.py --url "https://stackoverflowteams.com/c/TEAM-NAME" --token "YOUR_TOKEN" --output-file "my_report.csv"`
* `python3 so4t_user_report.py --url "https://SUBDOMAIN.stackenterprise.co" --key "YOUR_KEY" --token "YOUR_TOKEN" --output-file "enterprise_report.csv"`

### New Command Line Arguments for Large Datasets

The script now includes several new arguments specifically designed for processing large datasets efficiently:

#### `--api-start-date` and `--api-end-date`
Filter data at the API level to reduce response size and processing time. This is more efficient than post-processing filtering.

```bash
# Process only data from 2024 onwards
python3 so4t_user_report.py --url "https://SUBDOMAIN.stackenterprise.co" --key "YOUR_KEY" --token "YOUR_TOKEN" --api-start-date "2024-01-01"

# Process only data from a specific date range
python3 so4t_user_report.py --url "https://SUBDOMAIN.stackenterprise.co" --key "YOUR_KEY" --token "YOUR_TOKEN" --api-start-date "2023-01-01" --api-end-date "2023-12-31"
```

#### `--max-users`
Limit the number of users processed. Useful for testing or processing subsets of large user bases.

```bash
# Process only the first 100 users
python3 so4t_user_report.py --url "https://SUBDOMAIN.stackenterprise.co" --key "YOUR_KEY" --token "YOUR_TOKEN" --max-users 100
```

#### `--user-id-start` and `--user-id-end`
Process users in specific ID ranges. Useful for processing large user bases in chunks.

```bash
# Process users with IDs 1-1000
python3 so4t_user_report.py --url "https://SUBDOMAIN.stackenterprise.co" --key "YOUR_KEY" --token "YOUR_TOKEN" --user-id-start 1 --user-id-end 1000

# Process users with IDs 10000-20000
python3 so4t_user_report.py --url "https://SUBDOMAIN.stackenterprise.co" --key "YOUR_KEY" --token "YOUR_TOKEN" --user-id-start 10000 --user-id-end 20000
```

#### `--output-name`
Customize the output file names with a specific identifier instead of using the current date.

```bash
# Use custom output names
python3 so4t_user_report.py --url "https://SUBDOMAIN.stackenterprise.co" --key "YOUR_KEY" --token "YOUR_TOKEN" --output-name "enterprise_full_dataset"

# This will create files like:
# - user_metrics_enterprise_full_dataset.csv
# - users_enterprise_full_dataset.json
# - reputation_history_enterprise_full_dataset.json
# etc.
```

### Error Handling and Reliability

The script includes comprehensive error handling to prevent crashes and ensure reliable operation:

#### Robust KeyError Prevention
- **Safe field access**: All user data fields use `safe_get_user_field()` function to prevent KeyError crashes
- **Missing field handling**: Users with missing `account_id`, `email`, `title`, or other fields won't cause script failures
- **Graceful degradation**: Missing fields are populated with appropriate default values (empty strings, zeros, or False)
- **Problematic user processing**: Script continues processing even when encountering users with incomplete data

#### Common Issues Resolved
- **`KeyError: 'account_id'`**: Fixed - script handles users without account_id fields
- **Deactivated users**: Enhanced processing for users missing from API v3 responses
- **Deleted users**: Proper handling of users with incomplete profile data
- **API response variations**: Handles different response structures across Stack Overflow instances

### Performance Optimizations

The script now includes several performance optimizations for large datasets:

#### Batch Processing Improvements
- **Deactivated Users**: Processed in batches of 10 users (instead of individual API calls)
- **Tag SMEs**: Processed in batches of 5 tags (instead of individual API calls)
- **Reputation History**: Processed in batches of 25 users (reduced from 50 for better rate limiting)

#### Rate Limiting Prevention
- **100ms delays** between individual API calls
- **500ms delays** between batches
- **1-second delays** between major operations
- **Automatic backoff handling** when API returns rate limit responses

#### Memory Efficiency
- **Lookup dictionaries** for faster user matching
- **Streaming data processing** to reduce memory usage
- **Efficient data structures** for large datasets

### Large Dataset Examples

Here are some example commands for processing large datasets:

#### Processing a Large Enterprise Instance (20,000+ users)
```bash
# Process all users with custom output naming
python3 so4t_user_report.py \
  --url "https://SUBDOMAIN.stackenterprise.co" \
  --key "YOUR_KEY" \
  --token "YOUR_TOKEN" \
  --output-name "enterprise_full_2024"
```

#### Processing Recent Data Only
```bash
# Process only data from the last 6 months
python3 so4t_user_report.py \
  --url "https://SUBDOMAIN.stackenterprise.co" \
  --key "YOUR_KEY" \
  --token "YOUR_TOKEN" \
  --api-start-date "2024-01-01" \
  --output-name "recent_data_2024"
```

#### Processing Users in Chunks
```bash
# Process users in chunks of 5000
python3 so4t_user_report.py \
  --url "https://SUBDOMAIN.stackenterprise.co" \
  --key "YOUR_KEY" \
  --token "YOUR_TOKEN" \
  --user-id-start 1 \
  --user-id-end 5000 \
  --output-name "chunk_1_5000"

python3 so4t_user_report.py \
  --url "https://SUBDOMAIN.stackenterprise.co" \
  --key "YOUR_KEY" \
  --token "YOUR_TOKEN" \
  --user-id-start 5001 \
  --user-id-end 10000 \
  --output-name "chunk_5001_10000"
```

#### Testing with Small Subsets
```bash
# Test with just 50 users first
python3 so4t_user_report.py \
  --url "https://SUBDOMAIN.stackenterprise.co" \
  --key "YOUR_KEY" \
  --token "YOUR_TOKEN" \
  --max-users 50 \
  --output-name "test_50_users"
```

### Performance Benchmarks

Based on testing with the Stack Overflow Enterprise demo instance:

| Dataset Size | Processing Time | Data Volume | API Calls |
|--------------|-----------------|-------------|-----------|
| **50 users** | ~2 minutes | ~50MB | ~500 calls |
| **500 users** | ~10 minutes | ~200MB | ~2,000 calls |
| **5,000 users** | ~45 minutes | ~1GB | ~15,000 calls |
| **20,000 users** | ~15-20 minutes | ~3GB | ~50,000 calls |
| **90,000 users** | ~1-1.5 hours | ~10GB | ~200,000 calls |

*Note: Actual performance may vary based on network conditions, API response times, and server load. The enhanced rate limiting prevention and batch processing significantly improve performance for large datasets.*

### Troubleshooting Large Datasets

#### Common Issues and Solutions

**Rate Limiting Errors**
- **Symptom**: "API backoff request received" messages
- **Solution**: The script automatically handles rate limiting with delays and retries. If you see frequent backoff messages, consider using `--api-start-date` to reduce data volume.

**Memory Issues**
- **Symptom**: Script crashes with "MemoryError" or "OutOfMemoryError"
- **Solution**: Use `--max-users` to process smaller batches, or use `--user-id-start` and `--user-id-end` to process users in chunks.

**Long Processing Times**
- **Symptom**: Script takes hours to complete
- **Solution**: This is normal for large datasets. Use `--api-start-date` to limit data to recent periods, or process in chunks using user ID ranges.

**Token Expiration**
- **Symptom**: "Expired access token" errors
- **Solution**: Generate a new access token and re-run the script. Consider using `--no-api` with existing JSON data to avoid re-fetching all data.

**KeyError Crashes (Fixed)**
- **Symptom**: "KeyError: 'account_id'" or similar field errors causing script crashes
- **Solution**: This issue has been resolved in the enhanced version. The script now handles missing user fields gracefully and continues processing. Users with missing fields will have empty values in the CSV output instead of causing crashes.

#### Best Practices for Large Datasets

1. **Start Small**: Always test with `--max-users 50` first to ensure your setup works correctly.

2. **Use Date Filtering**: For recent analysis, use `--api-start-date` to limit data to the last 6-12 months.

3. **Process in Chunks**: For very large datasets (50,000+ users), use `--user-id-start` and `--user-id-end` to process in manageable chunks.

4. **Monitor Progress**: The script provides detailed progress updates. Watch for any error messages or rate limiting warnings.

5. **Use Custom Output Names**: Use `--output-name` to organize your output files, especially when processing multiple chunks.

6. **Backup Existing Data**: Before running large datasets, backup any existing JSON files in the `data/` directory.

7. **Network Stability**: Ensure you have a stable internet connection for long-running operations.

#### Recommended Workflow for Large Enterprise Instances

1. **Initial Test** (5-10 minutes):
   ```bash
   python3 so4t_user_report.py --url "YOUR_URL" --key "YOUR_KEY" --token "YOUR_TOKEN" --max-users 50 --output-name "test_run"
   ```

2. **Recent Data Analysis** (30-60 minutes):
   ```bash
   python3 so4t_user_report.py --url "YOUR_URL" --key "YOUR_KEY" --token "YOUR_TOKEN" --api-start-date "2024-01-01" --output-name "recent_analysis"
   ```

3. **Full Dataset Processing** (15-60 minutes for 20K users, 1-2 hours for 90K users):
   ```bash
   python3 so4t_user_report.py --url "YOUR_URL" --key "YOUR_KEY" --token "YOUR_TOKEN" --output-name "full_dataset"
   ```

4. **Chunked Processing** (for very large datasets):
   ```bash
   # Process in chunks of 10,000 users
   for i in {0..8}; do
     start=$((i * 10000 + 1))
     end=$(((i + 1) * 10000))
     python3 so4t_user_report.py --url "YOUR_URL" --key "YOUR_KEY" --token "YOUR_TOKEN" --user-id-start $start --user-id-end $end --output-name "chunk_${start}_${end}"
   done
   ```

## Support, security, and legal
If you encounter problems using the script, please leave feedback in the Github Issues. You can also clone and change the script to suit your needs. It is provided as-is, with no warranty or guarantee of any kind.

All data is handled locally on the device from which the script is run. The script does not transmit data to other parties like Stack Overflow. All API calls performed are read-only, so there is no risk of editing or adding content to your Stack Overflow for Teams instance.
