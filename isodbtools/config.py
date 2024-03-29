# -*- coding: utf-8 -*-
# pylint: disable-msg=unspecified-encoding
"""Module to provide global variables for isodb-tools
"""
import os
import json
import requests
import requests_cache

requests_cache.install_cache('api_map_cache')

# Global Variables
API_HOST = 'https://adsorption.nist.gov'
HEADERS = {'Accept': 'application/citeproc+json'}  # JSON Headers
TEXTENCODE = 'utf-8'
CANONICALIZE = 'NFKC'
TRACKER_SUFFIX = '&k=dontrackmeplease'

SCRIPT_PATH = os.path.split(os.path.realpath(__file__))[0]
ROOT_DIR = os.getcwd()
DOI_MAPPING_PATH = os.path.join(ROOT_DIR, 'DOI_mapping.csv')
JSON_FOLDER = os.path.join(ROOT_DIR, 'Library')

# Mapping rules
KEYS_API_MAPPING = {
    'isotherm_type': '/isotherm-type-map.json',
    'category': '/category-type-map.json',
    'concentrationUnits': '/concentration-unit-map.json',
    'compositionType': '/composition-type-map.json',
    'pressureUnits': '/pressure-units-map.json'
}

MAPS = {}
for item, url in KEYS_API_MAPPING.items():
    json_data = requests.get(API_HOST + '/isodb/api' + url).json()
    MAPS[item] = {'json': json_data}

# Character Substitution Rules for Converting the DOI to a stub
doi_stub_rules = [
    {
        'old': '/',
        'new': '-'
    },
    {
        'old': '(',
        'new': ''
    },
    {
        'old': ')',
        'new': ''
    },
    {
        'old': ':',
        'new': ''
    },
    {
        'old': ':',
        'new': ''
    },
    {
        'old': ' ',
        'new': ''
    },
    {
        'old': '+',
        'new': 'plus'
    },
    {
        'old': '-',
        'new': ''
    },
]

# Pressure Conversions (to bar units)
pressure_units = {
    'bar': 1.0,
    'Pa': 1.0e-05,
    'kPa': 1.0e-02,
    'MPa': 10.0,
    'atm': 1.01325e0,
    'mmHg': 1.333223684e-03,
    'Torr': 1.333223684e-03,
    'psi': 6.8947572932e-02,
    'mbar': 1.0e-03,
}

# Canonical Keys for Isotherm JSON (required keys for ISODB)
canonical_keys = [
    'DOI',
    'adsorbates',
    'adsorbent',
    'adsorptionUnits',
    'articleSource',
    'category',
    'compositionType',
    'concentrationUnits',
    'date',
    'digitizer',
    'filename',
    'isotherm_data',
    'isotherm_type',
    'pressureUnits',
    'tabular_data',
    'temperature',
]


# Function to generate a DOI stub from a DOI
def doi_stub_generator(input_doi):
    """Generate the DOI_stub for an input DOI"""
    doi_stub = input_doi
    for rule in doi_stub_rules:
        doi_stub = doi_stub.replace(rule['old'], rule['new'])
    doi_stub = doi_stub.lower()
    return doi_stub


# Wrapper function for JSON writes to ensure consistency in formatting
def json_writer(filename, data):
    """Format JSON according to ISODB specs"""
    with open(filename, mode='w') as output:
        json.dump(data, output, ensure_ascii=False, sort_keys=True,
                  indent=4)  # formatting rules
        output.write('\n')  # new line at EOF


def clean_json(filename):
    """Read in JSON and output according to ISODB specs"""
    print('operate on filename: ', filename)
    with open(filename, mode='r') as infile:
        isotherm_data = json.load(infile)
    os.rename(filename, filename + '.bak')
    json_writer(filename, isotherm_data)
    os.remove(filename + '.bak')
