from dotenv import load_dotenv
import requests
import argparse
import github

load_dotenv()

parser = argparse.ArgumentParser(description="Closes down oll pull requests in a given GitHub organization.")
parser.add_argument('organization', type=str, help="GitHub organization name to process")
args = parser.parse_args()

DO_NOT_CLOSE_REPOS = []
REPO_CACHE = {}

jwt = github.get_jwt()

print("Retrieving install id")
install_id = github.get_install_id(jwt, 'orgs', args.organization)

print("Got install id, retrieving access token")
access_token = github.get_access_token(jwt, install_id)

print("Got access token, searching")
search_results = requests.get('https://api.github.com/search/issues',
                              params={
                                  "q": "is:pr is:open org:{}".format(args.organization)
                              }).json()

print("Got {} results out of {} total".format(len(search_results['items']), search_results['total_count']))

for result in search_results['items']:
    repo_name = '/'.join(result['repository_url'].split('/')[-2:])

    if repo_name in DO_NOT_CLOSE_REPOS:
        continue

    repo = None
    if repo_name in REPO_CACHE:
        repo = REPO_CACHE[repo_name]
    else:
        # repo_id is only used when fetching access tokens and we already have an access token
        repo = github.Repo(repo_name, None)
        repo.set_access_token(access_token)

        if not repo.should_close():
            DO_NOT_CLOSE_REPOS.append(repo_name)
            continue

        REPO_CACHE[repo_name] = repo
    print("Closing PR #{} in repo {}".format(result['number'], repo_name))
    repo.comment_and_close(result)
