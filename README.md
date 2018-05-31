# Visualization of Metro Systems


## Fetching data

The script `parse_metros.py` downloads and parses the table from the
Wikipedia page: https://en.wikipedia.org/wiki/List_of_metro_systems

Then, it finds the population for each city in the table. This is done in
`dbpedia_loader.py` by downloading the city's page from DBpedia, in JSON
format.

Finally, the script saves an array of all the metro systems, along with their
city populations, to `metros.json`.

### Running

Install dependencies:

    sudo apt-get install python-lxml
    pip install bs4

This will download and parse data, generating `metros.json`:

    python parse_metros.py


## Visualization with D3

`viz.html` visualizes the data in `metros.json` using D3. Since D3 loads the
data using an ajax request, you cannot open `viz.html` directly from your
browser; `viz.html` must be loaded through a web server. You start a web server
locally by running

    python -m SimpleHTTPServer

from this directory.
