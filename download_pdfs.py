#!/bin/env python

import requests
import shutil
import os
import json

def download_file(url,dst):
    with requests.get(url, stream=True) as r:
        with open(dst, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return dst

try:
    os.mkdir("output")
except OSError:
    pass

url_base = "https://api.cqc.org.uk/public/v1"
url = "/locations?page=1&perPage=50&inspectionDirectorate=Hospitals&partnerCode=DU"
while url != "":
    try:
        print(url)
        res = requests.get(url_base + url)
        providers = res.json()
        url = providers["nextPageUri"]
        for provider in providers["locations"]:
            #provider = {"locationId":"1-129389306"}
            print("\t",provider["locationId"])
            provider_data = requests.get("https://api.cqc.org.uk/public/v1/locations/"+provider["locationId"]).json()
            if "reports" in provider_data.keys() and "currentRatings" in provider_data.keys() \
            and provider_data["currentRatings"]["overall"]["rating"] != "No published rating" \
            and len(provider_data["inspectionAreas"]) > 0:
                areas = []
                for a in provider_data["inspectionAreas"]:
                    # Find Score for each area
                    scores = [p for p in provider_data["currentRatings"]["serviceRatings"] if p["name"] in a["inspectionAreaId"]]
                    if len(scores) == 0:
                        scores = [p for p in provider_data["currentRatings"]["serviceRatings"] if a["inspectionAreaId"] in p["name"]]
                    if len(scores) != 0:
                        scores = scores[0]

                        keyQuestionRatings = {p["name"]:p["rating"] for p in scores["keyQuestionRatings"]}
                        areas.append({
                            "name": a["inspectionAreaName"],
                            "rating": scores["rating"],
                            "keyQuestionRatings":keyQuestionRatings
                        })
                json.dump(areas,open(os.path.join("output",provider["locationId"]+".labels"),'w'))
                report_url = "https://api.cqc.org.uk/public/v1"+provider_data["reports"][0]["reportUri"]
                download_file(report_url,os.path.join("output",provider["locationId"]+".pdf"))
            else:
                pass
    except:
        print("\n\n\n", "There was an error! :(")
