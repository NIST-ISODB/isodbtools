# -*- coding: utf-8 -*-
"""Module to provide operations related to adsorbate objects
"""
import os
import json
import time
import copy
import requests

from .config import API_HOST, HEADERS, JSON_FOLDER, json_writer


def fix_adsorbate_id(adsorbate_input):
    """Lookup InChIKey from name"""
    output = copy.deepcopy(adsorbate_input)
    gas_name = adsorbate_input['name'].lower().replace(' ', '%20')
    url = API_HOST + '/isodb/api/gas/' + gas_name + '.json&k=dontrackmeplease'
    # Attempt to resolve the name using the ISODB API
    try:
        gas_info = json.loads(requests.get(url, headers=HEADERS).content)
        output['InChIKey'] = gas_info['InChIKey']
        output['name'] = gas_info['name']
        check = True
    except ValueError:
        check = False
    return output, check


def regenerate_adsorbates():
    """Generate the entire ISODB library from the API"""
    # Create the JSON Library folder if necessary
    if not os.path.exists(JSON_FOLDER):
        os.mkdir(JSON_FOLDER)

    # Create subfolder for Adsorbates if necessary
    adsorbate_folder = JSON_FOLDER + '/Adsorbates'
    if not os.path.exists(adsorbate_folder):
        os.mkdir(adsorbate_folder)

    # Generate a list of adsorbents from the MATDB API
    url = API_HOST + '/isodb/api/gases.json'
    adsorbates = json.loads(requests.get(url, headers=HEADERS).content)
    print(len(adsorbates), 'Adsorbate Species Entries')

    # Extract each adsorbate in full form
    for (adsorbate_count, adsorbate) in enumerate(adsorbates):
        filename = adsorbate['InChIKey'] + '.json'
        url = API_HOST + '/isodb/api/gas/' + filename
        print(url)
        try:
            adsorbate_data = json.loads(
                requests.get(url, headers=HEADERS).content)
            # pprint.pprint(adsorbate_data)
            # Write to JSON
            json_writer(adsorbate_folder + '/' + filename, adsorbate_data)
        except ValueError:
            print('ERROR: ', adsorbate)
        # if adsorbate_count > 5: break
        if adsorbate_count % 100 == 0:
            time.sleep(5)  # slow down API calls to not overwhelm the server
