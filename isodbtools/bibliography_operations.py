# -*- coding: utf-8 -*-
"""Module to provide operations related to bibliography
"""
import os
# import pprint
import json
import unicodedata
import time
import copy
import glob
import requests

from .config import API_HOST, HEADERS, JSON_FOLDER, TEXTENCODE, doi_stub_rules, json_writer


def regenerate_bibliography():
    """Generate the entire ISODB library from the API"""
    # Create the JSON Library folder if necessary
    if not os.path.exists(JSON_FOLDER):
        os.mkdir(JSON_FOLDER)

    # Create subfolder for Adsorbates if necessary
    biblio_folder = JSON_FOLDER + '/Bibliography'
    if not os.path.exists(biblio_folder):
        os.mkdir(biblio_folder)

    # Generate a list of adsorbents from the MATDB API
    url = API_HOST + '/isodb/api/biblios.json'
    bibliography = json.loads(requests.get(url, headers=HEADERS).content)
    print(len(bibliography), 'Bibliography Entries')

    # Extract each paper in full form
    for (biblio_count, biblio) in enumerate(bibliography):
        doi = biblio['DOI']
        doi_stub = biblio['DOI']
        for rule in doi_stub_rules:
            doi_stub = doi_stub.replace(rule['old'], rule['new'])
        doi_stub = doi_stub.lower()
        url = API_HOST + '/isodb/api/biblio/' + doi + '.json'
        url = url.replace('%', '%25')  # make this substitution first
        url = url.replace('+', '%252B')
        try:
            biblio_data = json.loads(
                requests.get(
                    url,
                    headers=HEADERS).content)[0]  # look at the API call here
            # pprint.pprint(biblio_data)
            # Write to JSON
            filename = doi_stub + '.json'
            json_writer(biblio_folder + '/' + filename, biblio_data)
        except ValueError:
            print('ERROR: ', doi)
            print(url)
        # if biblio_count > 5:
        #     break
        if biblio_count % 100 == 0:
            time.sleep(5)  # slow down API calls to not overwhelm the server


journal_fixes = {
    'angewandte chemie international edition':
    'angewandte chemie-international edition',
    'zeitschrift für anorganische und allgemeine chemie':
    'zeitschrift fur anorganische und allgemeine chemie',
    'the canadian journal of chemical engineering':
    'canadian journal of chemical engineering',
    'applied catalysis a: general': 'applied catalysis a-general',
    'applied catalysis b: environmental': 'applied catalysis b-environmental',
    'journal of molecular catalysis a: chemical':
    'journal of molecular catalysis a-chemical',
    'energy environ sci': 'energy and environmental science',
    'fullerenes, nanotubes and carbon nanostructures':
    'fullerenes nanotubes and carbon nanostructures',
    'environmental science: nano': 'environmental science-nano',
    'chimia international journal for chemistry': 'chimia',
    'journal of chemical technology & biotechnology':
    'Journal of Chemical Technology and Biotechnology',
    'colloids and surfaces a: physicochemical and engineering aspects':
    'Colloids and Surfaces A-Physicochemical and Engineering Aspects',
    'journal of environmental sciences':
    'Journal of Environmental Sciences-China'
}


def fix_journal(journal_in):
    """Point Corrections for journals with inconsistent naming"""
    output = journal_fixes.get(journal_in)
    if output is None:
        output = journal_in
    return output


def extract_names(string):
    """Convert name string to given and middle names"""
    if string.count('.') > 1:
        split_string = string.split('.', 1)
        given = split_string[0] + '.'
        middle = split_string[1].lstrip()
    elif ' ' in string:
        # print 'spaces', string
        split_string = string.split(' ', 1)
        given = split_string[0]
        middle = split_string[1]
    else:
        given = string
        middle = None
    # Remove preceding dash from middle
    if middle is not None and len(middle) > 0 and middle[0] == '-':
        middle = middle.split('-', 1)[1]
    return {'given': given, 'middle': middle}


def generate_bibliography(folder, simulate_api=False):
    # pylint: disable-msg=too-many-locals
    # pylint: disable-msg=too-many-branches
    # pylint: disable-msg=too-many-statements
    """Generate a bibliography entry given a set of isotherms"""
    # Generate a list of isotherms to process
    if folder[-1] != '/':
        folder += '/'
    filenames = glob.glob(folder + '*')
    filenames = [x for x in filenames if 'isotherm' in x or 'Isotherm' in x]
    # Extract the unique dois
    dois = []
    for filename in filenames:
        with open(filename, mode='r') as handle:
            isotherm = json.load(handle)
        if isotherm['DOI'].lower() not in [x.lower() for x in dois]:
            dois.append(isotherm['DOI'])
    # print(dois)

    for doi in dois:
        # Pull bibliographic metadata from the dx.doi.org API
        try:
            url = 'https://doi.org/' + doi
            bib_info = json.loads(requests.get(url, headers=HEADERS).content)
        except ValueError:
            raise RuntimeError('ERROR: DOI problem for:' + doi)
        title = bib_info['title'].encode(TEXTENCODE).decode()
        journal = (bib_info['container-title'].replace(
            '.', '').encode(TEXTENCODE).lower().decode())
        journal = fix_journal(journal)
        year = int(bib_info['issued']['date-parts'][0][0])

        # -----------------------------
        # Match Journal Name/Abbreviation to existing lookup
        url = API_HOST + '/isodb/api/journals-lookup.json'
        journals = json.loads(requests.get(url, headers=HEADERS).content)
        if journal in [x['name'].lower() for x in journals]:
            # Attempt to match journal by name (lower case)
            index = [x['name'].lower() for x in journals].index(journal)
            journal = {'journal_id': journals[index]['id']}
            journal['name'] = journals[index]['name']
        elif journal in [
                x['abbreviation'].lower().replace('.', '') for x in journals
        ]:
            # attempt to match journal by abbreviation (lower case, strip out periods)
            index = [
                x['abbreviation'].lower().replace('.', '') for x in journals
            ].index(journal.replace('.', ''))
            journal = {'journal_id': journals[index]['id']}
            journal['abbreviation'] = journals[index]['abbreviation']
        else:
            raise Exception('Unknown Journal: ', journal)
        # ------------------------------
        # Parse the author list
        authors = []
        for (i, author) in enumerate(bib_info['author']):
            block = {}
            block['order_id'] = i + 1
            block['family_name'] = unicodedata.normalize(
                'NFKC', author['family'])
            try:
                given_names = extract_names(author['given'])
                block['given_name'] = unicodedata.normalize(
                    'NFKC', given_names['given'])
            except ValueError:
                raise Exception('Error parsing author block: ' + author +
                                '\n for DOI: ' + doi)
            if given_names['middle'] is not None:
                block['middle_name'] = unicodedata.normalize(
                    'NFKC', given_names['middle'])
                if 'ORCID' in author:
                    block['orc_id'] = author['ORCID'].replace(
                        'http://orcid.org/', '')
            authors.append(block)
        # Collect metadata from the isotherms
        adsorbates = []
        adsorbents = []
        temperatures = []
        categories = []
        min_pressure = 1.0e10  # initialize this absurdly
        max_pressure = -1.0e10  # initialize this absurdly
        isotherms = []

        for filename in filenames:
            with open(filename, mode='r') as handle:
                isotherm = json.load(handle)
            if isotherm['DOI'].lower() == doi.lower():

                adsorbents.append(str(isotherm['adsorbent']['hashkey']))
                if str(isotherm['category']) != '':
                    categories.append(str(isotherm['category']))
                temperatures.append(int(isotherm['temperature']))
                for adsorbate in isotherm['adsorbates']:
                    adsorbates.append(adsorbate['InChIKey'])
                for point in isotherm['isotherm_data']:
                    min_pressure = min(min_pressure, point['pressure'])
                    max_pressure = max(max_pressure, point['pressure'])

                # Correction to pressure range
                if min_pressure < 0.0:
                    min_pressure = 0.00
                if max_pressure > 1000.0:
                    max_pressure = 1000.00

                isotherms.append(filename.split('/')[-1])

        # Reduce redundant lists to unique lists and convert to dictionaries
        adsorbents = [{'hashkey': x} for x in sorted(list(set(adsorbents)))]
        categories = [{'name': x} for x in sorted(list(set(categories)))]
        temperatures = list(set(temperatures))
        adsorbates = [{'InChIKey': x} for x in sorted(list(set(adsorbates)))]
        # This is an odd sorting algorithm, but is necessary to immitate the API
        #  Sort is case insensitive, but preserves filename case
        isotherms = sorted([x.replace('.json', '') for x in isotherms],
                           key=str.casefold)
        isotherms = [{'filename': x} for x in isotherms]

        # Build the JSON Structure
        biblio = {}
        biblio['DOI'] = doi
        biblio['categories'] = categories
        biblio['adsorbates'] = adsorbates
        biblio['adsorbents'] = adsorbents
        biblio['temperature'] = temperatures
        biblio['pressure_min'] = float('{0:.2f}'.format(min_pressure))
        biblio['pressure_max'] = float('{0:.2f}'.format(max_pressure))
        biblio['title'] = title
        biblio['year'] = year
        biblio['journal'] = journal
        biblio['authors'] = authors
        biblio['isotherms'] = isotherms

        # Write to disk
        doi_stub = doi
        for rule in doi_stub_rules:
            doi_stub = doi_stub.replace(rule['old'], rule['new'])
        doi_stub = doi_stub.lower()

        if not simulate_api:
            # Write the bibliography file for database admin
            json_writer(doi_stub + '.json', biblio)  # simulate_api=False
            # pprint.pprint(biblio)
        else:
            # Write the bibliography file to simulate the ISODB API
            biblio_api = copy.deepcopy(biblio)
            biblio_api['journal'] = biblio_api['journal']['name']
            biblio_api['categories'] = [
                x['name'] for x in biblio_api['categories']
            ]
            biblio_api['pressures'] = [min_pressure, max_pressure]
            del biblio_api['pressure_min']
            del biblio_api['pressure_max']
            biblio_api['temperatures'] = biblio_api.pop('temperature')
            # Simplify Authors
            authors = []
            for author in biblio_api['authors']:
                name = []
                for key in ['given_name', 'middle_name', 'family_name']:
                    if key in author:
                        name.append(author[key])
                name = ' '.join(name)
                authors.append(name)
            biblio_api['authors'] = authors
            # Adsorbates List
            biblio_api['adsorbateGas'] = []
            for adsorbate in biblio_api['adsorbates']:
                # Look up name associated with InChIKey
                url = (API_HOST + '/isodb/api/gas/' + adsorbate['InChIKey'] +
                       '.json&k=dontrackmeplease')
                info = json.loads(requests.get(url, headers=HEADERS).content)
                adsorbate['name'] = info['name']
                biblio_api['adsorbateGas'].append(info['name'])
            # Adsorbents List
            biblio_api['adsorbentMaterial'] = []
            for adsorbent in biblio_api['adsorbents']:
                # Look up name associated with hashkey
                url = (API_HOST + '/matdb/api/material/' +
                       adsorbent['hashkey'] + '.json&k=dontrackmeplease')
                info = json.loads(requests.get(url, headers=HEADERS).content)
                adsorbent['name'] = info['name']
                biblio_api['adsorbentMaterial'].append(info['name'])
            # to disk
            json_writer(doi_stub + '.json.API',
                        biblio_api)  # simulate_api=True
            # pprint.pprint(biblio_api)
