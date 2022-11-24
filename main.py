#!/usr/bin/env python
from contextlib import suppress
from functools import reduce
import http.client
import json
import os
from random import randint, random
from time import sleep, time

import requests
from tqdm import tqdm

T = 0.5

cookies = {
    "_s_tentry": "passport.weibo.com",
    "ALF": "1699608779",
    "Apache": "8299455135346.2705.1638959679478",
    "cross_origin_proto": "SSL",
    "login_sid_t": "4b917bd89ec5e1ef39fe8c41fb741fc0",
    "PC_TOKEN": "b8816542d9",
    "SCF": "Aqu9EpHWJO_tfcs5RlPDAY1rk5Ak1eaE4fItGIWdKQ3h7VfbvCtj4zMmVucFecWFf1DVmAwU--qiW-g3aEfPdgA.",
    "SINAGLOBAL": "8299455135346.2705.1638959679478",
    "SSOLoginState": "1665137199",
    "SUB": "_2A25OaLUEDeRhGeNP4loX9y7LyD2IHXVtH6HMrDV8PUNbmtAKLU7VkW9NTlu_2yYmd4V4cqZ3VQVORGLel6l4-gc8",
    "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WFVySww9wXXWoLfijNv8KiL5JpX5KMhUgL.Fo-p1KncS05Ne022dJLoI7LJMJHL9h57eh5t",
    "ULV": "1638959679479:1:1:1:8299455135346.2705.1638959679478:",
    "WBPSESS": "j6tioVbCBSNDSDeYczb8JsDMiVglMcEn53xad8obbDAR20Lha-bLe-SODNPFDWvvA2yLZujF2Obu0bddvtonvztIU51T0FiNTHA23y6vm1U0KoFP-Gl3TAcmJ77jA6iqBqwKBWQAkatNx9CiCcshXg==",
    "XSRF-TOKEN": "6O6BVzPiSvLEIXnObxidFBLI",
}


def get_response(url):
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


def dump_json(uid):
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
    uids = [3766748450]
    for uid in uids:
        dump_json(uid)
    dt = time() - t0
    print(dt / 3600)
    print("OK!")
