from __future__ import print_function
import os.path
from googleapiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
import requests
import pandas as pd
import numpy as np
import math
import time
SPREADSHEET_ID = None
service = None
sheet = None
url = "https://api.opensea.io/api/v1/assets"


def multiply(l):
    m = 1
    for i, el in enumerate(l):
        m *= el

    return m


def ab_for_sale(collection_name, collection_number, collection_size):
    iter_num = math.floor(collection_size/25)
    num = collection_number*1000000
    extra_nums = collection_size - iter_num*25
    trait_val_list = []
    id_trait_list = []
    id_link_price = []
    for i in range(iter_num):
        querystring = {"asset_contract_address": "0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270",
                       "token_ids": list(range(num + i * 25, num + (i + 1) * 25)),
                       "order_direction": "desc",
                       "offset": "0",
                       "limit": "50"}

        headers = {"Accept": "application/json", "X-API-KEY": "0fba3b6165af43ffb8a9c295f1d8beb5"}

        response = requests.request("GET", url, headers=headers, params=querystring)
        temp_list = list(response.json()['assets'])
        for j, el in enumerate(temp_list):
            if str(el['sell_orders']) != "None" and float(el['sell_orders'][0]['current_price']) / 1e18 < 500:
                current_price = float(el['sell_orders'][0]['current_price'])/ 1e18
                link = el["permalink"]
                last_price = "None"
                last_sale_date = "None"
                if str(el['last_sale']) != "None":
                    last_sale_date = el['last_sale']['event_timestamp']
                    last_price = float(el['last_sale']['total_price']) / 1e18
                created_date = el['sell_orders'][0]['created_date']
                timestamp = el['sell_orders'][0]['listing_time']
                id_link_price.append(["Art Blocks " + collection_name,
                                      int(el['token_id'])-num,
                                      current_price,
                                      link,
                                      created_date,
                                      timestamp,
                                      last_price, last_sale_date])
            id_traits = []
            for k, element in enumerate(el['traits']):
                id_traits.append(element['value'])
                if not trait_val_list:
                    trait_val_list.append([element['value'], 1])
                else:
                    recognized = 0
                    for l, e in enumerate(trait_val_list):
                        if element['value'] == e[0]:
                            e[1] += 1
                            recognized = 1
                            break
                    if recognized == 0:
                        trait_val_list.append([element['value'], 1])
            id_trait_list.append([int(el['token_id'])-num, id_traits])

    if extra_nums > 0:
        querystring = {"asset_contract_address": "0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270",
                       "token_ids": list(range(num + iter_num * 25, num + collection_size)),
                       "order_direction": "desc",
                       "offset": "0",
                       "limit": "50"}

        response = requests.request("GET", url, params=querystring)
        temp_list = list(response.json()['assets'])
        for j, el in enumerate(temp_list):
            if str(el['sell_orders']) != "None" and float(el['sell_orders'][0]['current_price']) / 1e18 < 500:
                current_price = float(el['sell_orders'][0]['current_price']) / 1e18
                link = el["permalink"]
                last_price = "None"
                last_sale_date = "None"
                if str(el['last_sale']) != "None":
                    last_sale_date = el['last_sale']['event_timestamp']
                    last_price = float(el['last_sale']['total_price']) / 1e18
                created_date = el['sell_orders'][0]['created_date']
                timestamp = el['sell_orders'][0]['listing_time']
                id_link_price.append(["Art Blocks " + collection_name,
                                      int(el['token_id']) - num,
                                      current_price,
                                      link,
                                      created_date,
                                      timestamp,
                                      last_price, last_sale_date])
            id_traits = []
            for k, element in enumerate(el['traits']):
                id_traits.append(element['value'])
                if not trait_val_list:
                    trait_val_list.append([element['value'], 1])
                else:
                    recognized = 0
                    for l, e in enumerate(trait_val_list):
                        if element['value'] == e[0]:
                            e[1] += 1
                            recognized = 1
                            break
                    if recognized == 0:
                        trait_val_list.append([element['value'], 1])
            id_trait_list.append([int(el['token_id']) - num, id_traits])

    for i, el in enumerate(trait_val_list):
        el[1] /= collection_size
    id_rarity_list = []
    for i, el in enumerate(id_trait_list):
        trait_vals = []
        trait_str = []
        for j, trait in enumerate(el[1]):
            for k, t in enumerate(trait_val_list):
                if t[0] == trait:
                    trait_vals.append(round(t[1], 5))
                    trait_str.append(str(round(t[1], 7)))
        trait_mult = multiply(trait_vals)
        min_trait = min(trait_vals)
        trait_str.sort()
        id_rarity_list.append([el[0], trait_mult, min_trait, '|| ' + ' || '.join(trait_str), len(trait_vals)])
    id_rarity_list.sort(key=lambda x: x[1])

    mult_rank_list = []
    rank_num = 1
    for i, el in enumerate(id_rarity_list):
        if i > 0 and id_rarity_list[i-1][1] == id_rarity_list[i][1]:
            mult_rank_list.append([id_rarity_list[i][0], mult_rank_list[i-1][1]])
        else:
            mult_rank_list.append([id_rarity_list[i][0], rank_num])

        rank_num += 1

    id_rarity_list.sort(key=lambda x: x[2])

    min_rank_list = []
    rank_num = 1
    for i, el in enumerate(id_rarity_list):
        if i > 0 and id_rarity_list[i - 1][2] == id_rarity_list[i][2]:
            min_rank_list.append([id_rarity_list[i][0], min_rank_list[i-1][1]])
        else:
            min_rank_list.append([id_rarity_list[i][0], rank_num])

        rank_num += 1

    min_rank_list.sort(key=lambda x: x[0])
    mult_rank_list.sort(key=lambda x: x[0])
    id_rarity_list.sort(key=lambda x: x[0])
    id_link_price.sort(key=lambda x: x[1])
    final_rarity_list = []
    for j, e in enumerate(id_link_price):
        for i, el in enumerate(id_rarity_list):
            if el[0] == e[1]:
                final_rarity_list.append([e[0],
                                          e[1],
                                          e[2],
                                          str(mult_rank_list[i][1]),
                                          str(min_rank_list[i][1]),
                                          el[4],
                                          e[3],
                                          e[4],
                                          e[6],
                                          e[7],
                                          str(round(el[1]*collection_size, 10)),
                                          str(el[3]),
                                          e[5]])

    return final_rarity_list


def other_for_sale(collection_name, collection_contract, collection_size):
    iter_num = math.floor(collection_size/25)
    extra_nums = collection_size - iter_num*25
    trait_val_list = []
    id_trait_list = []
    id_link_price = []
    for i in range(iter_num):
        querystring = {"asset_contract_address": collection_contract,
                       "token_ids": list(range(i * 25, (i + 1) * 25)),
                       "order_direction": "desc",
                       "offset": "0",
                       "limit": "50"}

        headers = {"Accept": "application/json", "X-API-KEY": "0fba3b6165af43ffb8a9c295f1d8beb5"}

        response = requests.request("GET", url, headers=headers, params=querystring)
        temp_list = list(response.json()['assets'])
        for j, el in enumerate(temp_list):
            if str(el['sell_orders']) != "None" and float(el['sell_orders'][0]['current_price']) / 1e18 < 500:
                current_price = float(el['sell_orders'][0]['current_price'])/ 1e18
                link = el["permalink"]
                last_price = "None"
                last_sale_date = "None"
                if str(el['last_sale']) != "None":
                    last_sale_date = el['last_sale']['event_timestamp']
                    last_price = float(el['last_sale']['total_price']) / 1e18
                created_date = el['sell_orders'][0]['created_date']
                timestamp = el['sell_orders'][0]['listing_time']
                id_link_price.append([collection_name,
                                      int(el['token_id']),
                                      current_price,
                                      link,
                                      created_date,
                                      timestamp,
                                      last_price, last_sale_date])
            id_traits = []
            for k, element in enumerate(el['traits']):
                id_traits.append(element['value'])
                if not trait_val_list:
                    trait_val_list.append([element['value'], 1])
                else:
                    recognized = 0
                    for l, e in enumerate(trait_val_list):
                        if element['value'] == e[0]:
                            e[1] += 1
                            recognized = 1
                            break
                    if recognized == 0:
                        trait_val_list.append([element['value'], 1])
            id_trait_list.append([int(el['token_id']), id_traits])

    if extra_nums > 0:
        querystring = {"asset_contract_address": "0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270",
                       "token_ids": list(range(iter_num * 25, collection_size)),
                       "order_direction": "desc",
                       "offset": "0",
                       "limit": "50"}

        response = requests.request("GET", url, params=querystring)
        temp_list = list(response.json()['assets'])
        for j, el in enumerate(temp_list):
            if str(el['sell_orders']) != "None" and float(el['sell_orders'][0]['current_price']) / 1e18 < 500:
                current_price = float(el['sell_orders'][0]['current_price']) / 1e18
                link = el["permalink"]
                last_price = "None"
                last_sale_date = "None"
                if str(el['last_sale']) != "None":
                    last_sale_date = el['last_sale']['event_timestamp']
                    last_price = float(el['last_sale']['total_price']) / 1e18
                created_date = el['sell_orders'][0]['created_date']
                timestamp = el['sell_orders'][0]['listing_time']
                id_link_price.append([collection_name,
                                      int(el['token_id']),
                                      current_price,
                                      link,
                                      created_date,
                                      timestamp,
                                      last_price, last_sale_date])
            id_traits = []
            for k, element in enumerate(el['traits']):
                id_traits.append(element['value'])
                if not trait_val_list:
                    trait_val_list.append([element['value'], 1])
                else:
                    recognized = 0
                    for l, e in enumerate(trait_val_list):
                        if element['value'] == e[0]:
                            e[1] += 1
                            recognized = 1
                            break
                    if recognized == 0:
                        trait_val_list.append([element['value'], 1])
            id_trait_list.append([int(el['token_id']), id_traits])

    for i, el in enumerate(trait_val_list):
        el[1] /= collection_size
    id_rarity_list = []
    for i, el in enumerate(id_trait_list):
        trait_vals = []
        trait_str = []
        for j, trait in enumerate(el[1]):
            for k, t in enumerate(trait_val_list):
                if t[0] == trait:
                    trait_vals.append(round(t[1], 5))
                    trait_str.append(str(round(t[1], 7)))
        trait_mult = multiply(trait_vals)
        min_trait = min(trait_vals)
        trait_str.sort()
        id_rarity_list.append([el[0], trait_mult, min_trait, '|| ' + ' || '.join(trait_str), len(trait_vals)])
    id_rarity_list.sort(key=lambda x: x[1])

    mult_rank_list = []
    rank_num = 1
    for i, el in enumerate(id_rarity_list):
        if i > 0 and id_rarity_list[i-1][1] == id_rarity_list[i][1]:
            mult_rank_list.append([id_rarity_list[i][0], mult_rank_list[i-1][1]])
        else:
            mult_rank_list.append([id_rarity_list[i][0], rank_num])

        rank_num += 1

    id_rarity_list.sort(key=lambda x: x[2])

    min_rank_list = []
    rank_num = 1
    for i, el in enumerate(id_rarity_list):
        if i > 0 and id_rarity_list[i - 1][2] == id_rarity_list[i][2]:
            min_rank_list.append([id_rarity_list[i][0], min_rank_list[i-1][1]])
        else:
            min_rank_list.append([id_rarity_list[i][0], rank_num])

        rank_num += 1

    min_rank_list.sort(key=lambda x: x[0])
    mult_rank_list.sort(key=lambda x: x[0])
    id_rarity_list.sort(key=lambda x: x[0])
    id_link_price.sort(key=lambda x: x[1])
    final_rarity_list = []
    for j, e in enumerate(id_link_price):
        for i, el in enumerate(id_rarity_list):
            if el[0] == e[1]:
                final_rarity_list.append([e[0],
                                          e[1],
                                          e[2],
                                          str(mult_rank_list[i][1]),
                                          str(min_rank_list[i][1]),
                                          el[4],
                                          e[3],
                                          e[4],
                                          e[6],
                                          e[7],
                                          str(round(el[1]*collection_size, 10)),
                                          str(el[3]),
                                          e[5]])

    return final_rarity_list


def update_sheet(collection_list_ab, collection_list):
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = 'keys.json'
        credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=scope)

        # If modifying these scopes, delete the file token.json.
        SPREADSHEET_ID = '1UXmle5eN7s7_FBz1NolTBtLL5u2clYnCXt1OM2j5jdE'

        service = build('sheets', 'v4', credentials=credentials)

        final_list = []
        for i, l in enumerate(collection_list_ab):
            final_list += ab_for_sale(l[0], l[1], l[2])

        for i, l in enumerate(collection_list):
            final_list += other_for_sale(l[0], l[1], l[2])
        final_list.sort(key=lambda x: float(x[12]), reverse=True)
        final_list.insert(0, ['Collection Name',
                                     'Id',
                                     'Current Price',
                                     'Rarity Rank',
                                     'Individual Trait Rank',
                                     'Number of Traits',
                                     'Link',
                                     'Listing Date',
                                     'Last Sale Price',
                                     'Last Sale Date',
                                     'Rarity',
                                     'Rarities of Traits',
                                     'Timestamp'])
        body = {}
        service.spreadsheets().values().clear(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A:Z",
                                              body=body).execute()
        resource = {
            "majorDimension": "ROWS",
            "values": final_list
        }
        range = "Sheet1!A:A"
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=range,
            body=resource,
            valueInputOption="USER_ENTERED"
        ).execute()

coll_list_ab = [
   # ["Elevated Deconstructions", 7, 200],
    ["720 Minutes", 27, 720],
    ["Meridian", 163, 1000],
    ["Ecumenopolis", 119, 676],
    ["Algorhythms", 64, 1000],
    ["Watercolor Dreams", 59, 600],
    ["HyperHash", 11, 369]
]
coll_list_ab = [["Chimera", 320, 987]]
coll_list = [
    #["Loot", "0xff9c1b15b16263c61d017ee9f65c50e4ae0113d7", 7800]
             #["Dope Wars", "0x8707276df042e89669d69a177d3da7dc78bd8723", 8000]
             ]

update_sheet(coll_list_ab, coll_list)
