import requests
import os

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_ENDPOINT = "https://api.github.com/graphql"

GITHUB_HEADERS = {
    "Authorization": "bearer " + GITHUB_TOKEN
}

HASURA_ENDPOINT = "http://localhost:8080/v1/query"
HASURA_HEADERS = {}

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
        print('failed', res.status_code, res.json())
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
        print('failed', res.status_code, res.json())
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

def main(startCursor=None):
    gazers_raw_response = get_stargazers(startCursor)
    stars = gazers_raw_response["totalCount"]
    pageInfo = gazers_raw_response["pageInfo"]
    nodes = gazers_raw_response["nodes"]
    edges = gazers_raw_response["edges"]

    data = combineNodesAndEdges(nodes, edges)
    save_stargazers(data)

    if pageInfo["hasNextPage"]:
        main(pageInfo["endCursor"])



main()