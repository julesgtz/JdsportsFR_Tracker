import requests
import csv
import pandas as pd
import time
import os



csvfilename = "order.csv"
if not os.path.exists(csvfilename):
    with open(csvfilename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["numero de commande","code postal","status","suivi"])




headers = {
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
}


def process_order(order_number, postal_code):
    payload = {
        "orderNumber": order_number,
        "facia": "jdsportsfr",
        "postcode": postal_code,
    }
    response = requests.get("https://data.smartagent.io/v1/jdsports/track-my-order", headers=headers, params=payload)
    if response.status_code == 200:
        response_json = response.json()
        codes = [item["code"] for item in response_json["status"]["short"] if item.get("state") == "done"]
        if codes:
            dernier_code = codes[-1]
            if dernier_code == "ON_ITS_WAY":
                tracking_url = response_json.get("delivery", {}).get("trackingURL")
                if tracking_url:
                    return dernier_code, tracking_url.split("://", 1)[-1]
                else:
                    return "Pas de URL de suivi disponible."
            else:
                return dernier_code
        else:
            return "Error Payment"
    else:
        dernier_code = "Aucune info sur le suivi , surement cancel / loan"
        return dernier_code

with open(csvfilename, 'r') as csvfile:
    df = pd.read_csv(csvfilename)
    reader = csv.DictReader(csvfile)
    for row in reader:
        order_number = row['numero de commande']
        postal_code = row['code postal']
        dernier_code  = process_order(order_number, postal_code)
        time.sleep(1)
        order_number = int(order_number)
        if type(dernier_code)== tuple:
            status = dernier_code[0]
            url = dernier_code[1]
            df.loc[df["numero de commande"] == order_number, "status"] = status
            df.loc[df["numero de commande"] == order_number, "suivi"] = url
            df.to_csv(csvfilename, index=False)
            print(f"Commande #{order_number}, status {status}, url de suivi {url}")
        else:
            df.loc[df["numero de commande"] == order_number, "status"] = dernier_code
            df.to_csv(csvfilename, index=False)
            print(f"Commande #{order_number}, status {dernier_code}")