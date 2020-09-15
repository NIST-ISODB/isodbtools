# -*- coding: utf-8 -*-
"""Module to provide operations related to adsorbent objects
"""
import os
import json
import time
import copy
import requests

from .config import API_HOST, HEADERS, JSON_FOLDER, json_writer


def fix_adsorbent_id(adsorbent_input):
    """Lookup hashkey from name"""
    output = copy.deepcopy(adsorbent_input)
    material_name = adsorbent_input['name'].lower().replace('%',
                                                            '%25').replace(
                                                                ' ', '%20')
    url = API_HOST + '/matdb/api/material/' + material_name + '.json&k=dontrackmeplease'
    # Attempt to resolve the name using the MATDB API
    try:
        material_info = json.loads(requests.get(url, headers=HEADERS).content)
        output['hashkey'] = material_info['hashkey']
        output['name'] = material_info['name']
        check = True
    except ValueError:
        check = False
    return output, check


def regenerate_adsorbents():
    """Generate the entire ISODB library from the API"""
    # Create the JSON Library folder if necessary
    if not os.path.exists(JSON_FOLDER):
        os.mkdir(JSON_FOLDER)

    # Create subfolder for Adsorbents if necessary
    adsorbent_folder = JSON_FOLDER + '/Adsorbents'
    if not os.path.exists(adsorbent_folder):
        os.mkdir(adsorbent_folder)

    # Generate a list of adsorbents from the MATDB API
    url = API_HOST + '/matdb/api/materials.json'
    adsorbents = json.loads(requests.get(url, headers=HEADERS).content)
    print(len(adsorbents), 'Adsorbent Material Entries')

    # Extract each adsorbent in full form
    for (material_count, adsorbent) in enumerate(adsorbents):
        filename = adsorbent['hashkey'] + '.json'
        url = API_HOST + '/matdb/api/material/' + filename
        print(url)
        adsorbent_data = json.loads(requests.get(url, headers=HEADERS).content)
        # pprint.pprint(adsorbent_data)
        # Write to JSON
        json_writer(adsorbent_folder + '/' + filename, adsorbent_data)
        if material_count % 100 == 0:
            time.sleep(5)  # slow down API calls to not overwhelm the server
