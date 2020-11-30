# NIST/ARPA-E Database of Novel and Emerging Adsorbent Materials

The [NIST/ARPA-E Database of Novel and Emerging Adsorbent Materials](https://adsorption.nist.gov/isodb) is a free, web-based catalog of adsorbent materials and measured adsorption properties of numerous materials obtained from article entries from the scientific literature.
The database also contains adsorption isotherms digitized from the cataloged articles, which can be compared visually online in the web application, analyzed online with available tools, or exported for offline analysis.

This repository contains tools that are used for:
1. Post-processing, sanitizing, and organizing isotherm files
2. Generating bibliography files from packages of isotherm files
3. Creating submission files for new adsorbates and adsorbents
4. Generating database update instructions for isotherm and bibliography submissions

## Contributing

Contributions to the script code base are welcome.

## Repository Use

To use this repository:
1. Clone the repository locally
2.. Enable pre-commit hooks
    ```
    pip install -r .github/requirements.txt
    pre-commit install
    ```

Note: The pre-commit hooks will auto-format your code contributions and perform basic consistency checks.

## Installation as a Python Package

To install this package locally:
    ```
    pip install git+https://github.com/NIST-ISODB/isodbtools.git#egg=isodbtools
    ```
Then the package can be import via
    ```
    import isodbtools
    ```
