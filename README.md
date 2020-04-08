# labs/tools/github-pr-closer

See [T249703](https://phabricator.wikimedia.org/T249703).

## Creating a GitHub app for this tool
1. Go to organization settings -> github apps -> new github apps
2. Fill in the page. Pay attention to the following settings:
    * **Webhook**: active=true, url=https://(base-url)/github, secret=(random string here)
    * **Repository permissions**:  Pull requests=read and write,  Single file=read-only for `.gitreview`
    * **Subscribe to events**: Pull request=true
3. Create the app
4. Create a private key under "Private keys" and add it to this deployment's root with name `github-app-key.pem`
5. Install app to all repositories

## Resources
- https://developer.github.com/v3/activity/events/types/#pullrequestevent
- https://fedoramagazine.org/continuous-deployment-github-python/

## License
This tool is licensed under the MIT license. See `LICENSE` for more details.