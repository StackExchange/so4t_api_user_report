# Stack Internal API User Report

**Use [index.html](index.html) for new reports.** It reads Stack Internal API v3 and downloads a CSV user report. Keep the `assets/` folder beside the HTML file so its bundled Stacks styles load. No Python installation or build step is needed. The Python scripts remain in this repository only for historical reference; the old report still depends on API v2 and should not be used for new reports.

## Run the report

1. Download this repository and open `index.html` in a current browser.
2. Enter your Enterprise site URL, such as `https://your-site.stackenterprise.co`, or your Basic/Business team URL, such as `https://stackoverflowteams.com/c/your-team`.
3. Enter an API v3 access token with permission to read the report data. The token is used in Bearer authentication for requests to the selected API and is not saved in the HTML file or CSV.
4. Optionally choose a UTC date range or a maximum number of users, then select **Create CSV report**. When it finishes, select **Download CSV**.

The page requests API v3 directly from the browser. Your Stack Internal API must allow requests from the page's browser origin. If your browser reports a CORS error when the file is opened locally, ask your site administrator to allow that origin or serve the HTML file and `assets/` folder from an allowed HTTPS origin. The page cannot override the API's CORS policy.

## Report fields and limits

The report counts questions, unanswered questions, answers, accepted answers, articles, and comments created in the selected date range. It calculates median answer time from each answer's creation time and its question's creation time. It includes user details, current reputation, SME tags, and current net post scores. All data is limited to content visible to the token.

API v3 reports a **net score** for each post, so the CSV has question, answer, article, and total post score columns. Separate upvote and downvote totals from the old v2 report cannot be calculated from v3 and are not included.

Historical **Net Reputation Change**, account dates, and account status use Enterprise API v3 endpoints. These cells are blank when the endpoint is unavailable or the token lacks permission. Basic/Business v3 does not expose those fields in the supplied schema. **Current Reputation** is a separate value available from the users endpoint. Optional comment and SME collection can be turned off to reduce API requests; skipped fields are blank. Large sites can take time because the page follows pagination and requests answers, comments, and SME assignments separately.

The page is read-only. It runs all report processing locally in the browser and downloads the CSV locally. The API v3 schema supplied for this update was used to map the endpoints and fields; the HTML page does not need the schema file at runtime.

## Historical files

`so4t_user_report.py`, `so4t_api_v2.py`, `so4t_api_v3.py`, `so4t_web_client.py`, `so4t_request_validate.py`, and `requirements.txt` are retained to explain the older implementation. The example CSV in `Examples/` was produced by that older implementation, so its columns differ from the API v3 HTML report.

## Support

Please use [GitHub Issues](https://github.com/StackExchange/so4t_api_user_report/issues) for feedback. This project is provided as-is under the [MIT License](LICENSE).
