import html
import feedparser
import requests, json

from email.utils import parsedate_to_datetime

# Notion Settings
token = '<YOUR NOTION TOKEN>'
databaseID ="<YOUR DATABASE ID>"
headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-02-22"
}

# RSS Settings
rss_url = 'https://dennikn.sk/minuta/feed/?cat=430'


def createPage(databaseID, headers, title, published, description, link):
    createUrl = 'https://api.notion.com/v1/pages'

    newPageData = {
        "parent": { "database_id": databaseID },
        "icon": {
            "emoji": "📰"
        },
        "properties": {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            "Published": {
                "date": {
                    "start": published,
                }
            },
            "Description": {
                "rich_text": [
                    {
                        "text": {
                            "content": description
                        },
                    }
                ]
            },
            "Link": {
                "type": "url",
                "url": link
            },
        }
    }

    data = json.dumps(newPageData)
    res = requests.request("POST", createUrl, headers=headers, data=data)
    # print(res.text)
    print(f"createPage {res.status_code}")

def deletePage(databaseID, headers, pageID):
    updateUrl = f'https://api.notion.com/v1/pages/{pageID}'

    newPageData = {
        "archived": True
    }

    data = json.dumps(newPageData)
    res = requests.request("PATCH", updateUrl, headers=headers, data=data)
    print(f"deletePage {res.status_code}")

def readDatabase(databaseID, headers):
    readUrl = f"https://api.notion.com/v1/databases/{databaseID}/query"
    res = requests.request("POST", readUrl, headers=headers)
    data = res.json()
    print(f"readDatabase {res.status_code}")

    with open('./full-properties.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)
    return data


if __name__ == "__main__":
    feed = feedparser.parse(rss_url)

    if feed.status == 200:
        for page in readDatabase(databaseID, headers)["results"]:
            deletePage(databaseID, headers, page["id"])

        for entry in feed.entries:
            createPage(databaseID, headers, entry.title, parsedate_to_datetime(entry.published).isoformat(), html.unescape(entry.description), entry.link)
    else:
        print("Failed to get RSS feed. Status code:", feed.status)
