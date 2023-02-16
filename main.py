#!/usr/bin/env python
import http.client
import json
import os
import sys
from contextlib import suppress
from functools import reduce
from random import randint, random
from time import sleep, time

import requests
from tqdm import tqdm

T = 0.5

with open("cookies.json") as f:
    cookies = json.load(f)


def get_response(url: str) -> requests.models.Response:
    j = 0
    try:
        response = requests.get(url, cookies=cookies)
    except Exception:
        sleep(random() + 10)
        response = requests.get(url, cookies=cookies)
    while not response.ok:
        sleep(random() + 0.5 + randint(0, min(j, 60)))
        with suppress(http.client.RemoteDisconnected):
            response = requests.get(url, cookies=cookies)
        j += 1
        print(j)
    sleep(random() + T)
    return response


def dump_json(uid: int) -> None:
    fname = os.path.join("data", str(uid) + "-data.json")
    if not os.path.isfile(fname):
        data = []
        i = 1
        while True:
            url = (
                "https://www.weibo.com/ajax/friendships/friends?relate=fans&page="
                + str(i)
                + "&uid="
                + str(uid)
                + "&type=all&newFollowerCount=0"
            )
            response = get_response(url)
            try:
                data += json.loads(response.text)["users"]
            except KeyError:
                break
            i += 1
        data = reduce(lambda l, x: l if x in l else l + [x], data, [])
        with open(fname, "w") as f:
            json.dump(data, f)
    else:
        with open(fname, "r") as f:
            data = json.load(f)

    fname = os.path.join("data", str(uid) + "-detail.json")
    if os.path.isfile(fname):
        return

    users = []
    for datum in tqdm(data):
        url = "https://weibo.com/ajax/profile/detail?uid=" + str(datum["id"])
        response = get_response(url)
        d = json.loads(response.text)["data"]

        users += [d]
        if len(users) % 500 == 0:
            with open(fname, "w") as f:
                json.dump(users, f)

    with open(fname, "w") as f:
        json.dump(users, f)


if __name__ == "__main__":
    t0 = time()
    for uid in map(int, sys.argv[1:]):
        dump_json(uid)
    dt = time() - t0
    print(dt / 3600)
    print("OK!")
