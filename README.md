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
4. Go to app settings -> (in sidebar) general -> private keys -> generate a private key -> save as a file on Toolforge -> `toolforge envvars create GHPRC_JWT_SIGNING_KEY -- $(cat filenam)`
5. Go to app settings -> (in sidebar) install app -> select your organization and click install -> use all repositories -> install
6. Get the App ID (app settings -> general in sidebar -> about -> App ID) and create a envvar for it: `toolforge envvars create GHPRC_APP_ID app-id-here`
7. Create an envvar you chose when creating the app: `toolforge envvars create GHPRC_APP_SECRET app-secret-here`

## Useful resources

- https://developer.github.com/v3/activity/events/types/#pullrequestevent
- https://fedoramagazine.org/continuous-deployment-github-python/

## License

This tool is licensed under the MIT license. See `LICENSE` for more details.
