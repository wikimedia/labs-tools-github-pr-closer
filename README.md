# labs/tools/github-pr-closer

See [T249703](https://phabricator.wikimedia.org/T249703).

## Creating a GitHub app for this tool

1. Go to organization settings -> (under developer settings) github apps -> new github apps
2. Fill in the page. Pay attention to the following settings:
    * **GitHub app name, Description, Homepage URL**: these are displayed to the user, so please put something helpful here. app name is used for when naming the bot account.
    * **Webhook**: active=true, url=https://(base-url)/github, secret=(generate random string here)
    * **Repository permissions**: Enable Pull requests as read and write and Single file as read-only for `.gitreview`. This will enable Metadata, leave it as is.
    * **Subscribe to events**: Enable event "Pull request", leave everything else disabled
3. Create the app
4. Go to app settings -> (in sidebar) general -> private keys -> generate a private key -> save file `/data/project/github-pr-closer/data/github-app-key.pem`
5. Go to app settings -> (in sidebar) install app -> select your organization and click install -> use all repositories -> install
6. Create `/data/project/github-pr-closer/data/github-app-id.txt` with the app ID (app settings -> general in sidebar -> about -> App ID)
7. Create `/data/project/github-pr-closer/data/github-app-secret.txt` with the webhook secret you chose when creating the application.

## Useful resources

- https://developer.github.com/v3/activity/events/types/#pullrequestevent
- https://fedoramagazine.org/continuous-deployment-github-python/

## License

This tool is licensed under the MIT license. See `LICENSE` for more details.
