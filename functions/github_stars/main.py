import requests
import os

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_ENDPOINT = "https://api.github.com/graphql"

GITHUB_HEADERS = {
    "Authorization": "bearer " + str(GITHUB_TOKEN)
}

HASURA_ENDPOINT = os.getenv('HASURA_ENDPOINT')
HASURA_HEADERS = {
    "X-Hasura-Access-Key": str(os.getenv('HASURA_ACCESS_KEY'))
}

STARGAZERS_QUERY = """
query getStargazers(
  $owner: String!
  $name: String!
  $startCursor: String
) {
  repository(
    owner: $owner
    name: $name
  ) {
    stargazers(
      orderBy: {field: STARRED_AT, direction: ASC}
      after: $startCursor
      first: 100
    ) {
      totalCount
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      nodes {
        name
        login
        followers {
         totalCount
        }
      }
      edges {
        starred_at: starredAt
        cursor
      }
    }
  }
}
"""

def get_stargazers(startCursor=None):
    print('getting stargazers from {}'.format(startCursor))
    query = {
        "query": STARGAZERS_QUERY,
        "variables": {
            "owner": "hasura",
            "name": "graphql-engine"
        }
    }

    if startCursor:
        query["variables"]["startCursor"] = startCursor

    res = requests.post(GITHUB_ENDPOINT, json=query, headers=GITHUB_HEADERS)
    if res.status_code != 200:
        print('failed: {} {}'.format(res.status_code, res.json()))
        return None
    return res.json()["data"]["repository"]["stargazers"]

def save_stargazers(data):
    # starred_at
    # cursor
    # login
    # name
    # followers
    payload = {
        "type": "insert",
        "args": {
            "table": "github_stars",
            "objects": data
        }
    }

    print('inserting {} objects'.format(len(data)))
    res = requests.post(HASURA_ENDPOINT, json=payload, headers=HASURA_HEADERS)
    if res.status_code != 200:
        print('failed: {} {}'.format(res.status_code, res.json()))
        return None
    print('{} objects inserted'.format(res.json()["affected_rows"]))
    return

def combineNodesAndEdges(nodes, edges):
    data = []
    for i in range(len(nodes)):
        data.append({**nodes[i], **edges[i]})

    for e in data:
        e["followers"] = e["followers"]["totalCount"]

    return data

def getLastCursor():
    payload = {
        "type": "select",
        "args": {
            "table": "github_stars",
            "columns": ["cursor"],
            "order_by": "-id",
            "limit": 1
        }
    }
    print('getting last cursor')
    res = requests.post(HASURA_ENDPOINT, json=payload, headers=HASURA_HEADERS)
    if res.status_code != 200:
        print('failed: '.format(res.status_code, res.json()))
        return None
    data = res.json()
    if len(data) != 1:
        print('invalid response: {}'.format(data))
        return None
    return data[0]["cursor"]


def populate(startCursor=None):
    gazers_raw_response = get_stargazers(startCursor)
    stars = gazers_raw_response["totalCount"]
    pageInfo = gazers_raw_response["pageInfo"]
    nodes = gazers_raw_response["nodes"]
    edges = gazers_raw_response["edges"]

    data = combineNodesAndEdges(nodes, edges)
    save_stargazers(data)

    if pageInfo["hasNextPage"]:
        populate(pageInfo["endCursor"])

def main():
    cursor = getLastCursor()
    if cursor:
        populate(cursor)
    else:
        print('empty cursor')

def github_stars(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """
    if request.headers.get('x-github-event') == "watch":
        cursor = getLastCursor()
        if cursor:
            populate(cursor)
            return 'ok'
        else:
            print('empty cursor')

    return 'ignored'