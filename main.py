# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import bs4
import pyttsx3
import requests
from bs4 import BeautifulSoup
import re
import json
from pathlib import Path

dataDirectory = "mp3files/"
prefix = "https://old.reddit.com"


def saveAsMp3(text: str, fileName: str, subreddit: str):
    engine = pyttsx3.init()


    """ RATE"""
    rate = engine.getProperty('rate')  # getting details of current speaking rate
    # engine.setProperty('rate', 160)  # setting up new voice rate

    """VOICE"""
    voices = engine.getProperty('voices')  # getting details of current voice
    engine.setProperty('voice', voices[1].id)  # changing index, changes voices. 1 for female

    subredditPath = re.sub(pattern=r"[^\w\s]+", repl="", string=subreddit)
    Path(dataDirectory+subredditPath).mkdir(parents=True, exist_ok=True)
    print("saved")
    engine.save_to_file(text, dataDirectory+subredditPath+"/"+fileName + ".mp3")
    engine.runAndWait()


def savePostAsMP3(postURL: str, subreddit: str, headers):
    response = requests.get(prefix + postURL, headers=headers)
    soup = BeautifulSoup(response.content, features="html.parser")
    div = soup.find_all("div", {"class": "md"})[1]
    title = soup.find("a", {"data-event-action": "title"}).text
    title = re.sub(pattern=r"[^\w\s]+", repl="", string=title)
    saveAsMp3(div.text, title, subreddit)


def scrapePost(subreddit: str):
    headers = {
        'User-Agent': 'PostToTTS/0.1 by jjrryyaa',
    }
    response = requests.get(prefix + subreddit, headers=headers)
    soup = BeautifulSoup(response.content, features="html.parser")
    titles = soup.find_all("a", {"class": "title"})
    title: bs4.Tag

    listOfPostUrls: list[str] = []
    for title in titles:
        prev: bs4.ResultSet[bs4.Tag] = title.fetchPreviousSiblings(limit=1)
        subText: bs4.Tag = title.fetchParents(limit=4)[-1]
        if not ("stickied" in subText.attrs["class"]):
            listOfPostUrls.append(title.attrs["href"])
    try:
        with open('data.json', encoding='utf-8') as f:
            existingPosts = json.load(f)
    except:
        existingPosts = []

    postsToScrape = set(listOfPostUrls).difference(set(existingPosts))
    post: str
    for post in postsToScrape:
        savePostAsMP3(post, subreddit, headers)
    existingPosts = list(set(listOfPostUrls).union(set(existingPosts)))
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(existingPosts, f, ensure_ascii=False, indent=4)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with open('subreddits.json', encoding='utf-8') as f:
        subreddits = json.load(f)
        for sub in subreddits:
            scrapePost(sub)

# TODO
# 1. replace acronyms (eg AITA, F25)
