import json
import os
from http.client import HTTPSConnection
from base64 import b64encode

environment = "development"
url = os.getenv("PACT_BROKER_BASE_URL")
user = os.getenv("PACT_BROKER_HTTP_AUTH_USER")
password = os.getenv("PACT_BROKER_HTTP_AUTH_PASS")

c = HTTPSConnection(url)
userAndPass = b64encode(bytes(user + ":" + password, encoding="ascii")).decode("ascii")
headers = {"Authorization": "Basic %s" % userAndPass}
c.request("GET", "/pacticipants/OPG%20Data/versions", headers=headers)
res = c.getresponse()


providerjson = json.loads(res.read())
versionlist = []
for versions in providerjson["_embedded"]["versions"]:
    version = versions["number"]
    for tags in versions["_embedded"]["tags"]:
        if tags["name"] == environment:
            versionlist.append(version)

versionlist.sort(reverse=True)

if len(versionlist) > 0:
    print("setting DEPLOYABLE_VER env var to latest deployable version")
    os.environ["DEPLOYABLE_VER"] = versionlist[0]
else:
    print("no provider versions deployed to prod")
