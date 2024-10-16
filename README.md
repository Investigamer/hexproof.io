# Hexproof API
Hexproof is a Django-Ninja REST API for Magic the Gathering data and resources that takes in bulk 
data sets from a variety of sources and synthesizes it into comprehensive models. In terms of 
nomenclature, Hexproof is more similar to Scryfall than it is MTGJSON (snake_case). You can 
access the official live version of this API at [api.hexproof.io](https://api.hexproof.io), and the
API docs can be found [here](https://api.hexproof.io/docs).

We are building out additional image resource endpoints that other APIs seem to miss, one such 
resource is our `/symbols/` route that provides set rarity icon and watermark SVG's from a 
catalogue maintained on the [mtg-vectors](https://github.com/Investigamer/mtg-vectors) repository.

## Setup Guide
1. [Install Poetry](https://python-poetry.org/docs/) if you don't have it. We use `poetry` for project management. If 
you write a lot of Python and have never tried Poetry... trust me, you'll thank me later.
2. Clone the `hexproof` repository somewhere on your system and install the Poetry environment.
    ```shell
    # 1: Clone and enter the project.
    git clone https://github.com/Investigamer/hexproof.io.git
    cd hexproof.io

    # 2: Install the poetry environment.
    poetry install
    ```
3. Initialize the database and run the django test server.
    ```shell
    # 1: Enter poetry environment
    poetry shell

    # 2: Initialize database
    python manage.py migrate

    # 3: Collect static files
    python manage.py collectstatic
   
    # 3: [Optional] Create an admin user for accessing admin page
    python manage.py createsuperuser # Follow the prompts
   
    # 4: Run django test server
    python manage.py runserver
    ```
4. The project is set up, the test server is running, and the site is accessible at 
[http://localhost:8000](http://localhost:8000). The auto-generated docs page (using SwaggerUI) is available at `/docs/`, 
and Django's database administration panel is available at `/admin/`.

## API Endpoints
### `/keys/{key-name}`
Endpoint for retrieving an API key (currently used by Proxyshop).

### `/meta/{source-name}`
Endpoint for fetching "Meta" objects tracking version data for a variety of sources. Omit source name to return all.

### `/sets/{set-code}`
Endpoint for accessing Magic the Gathering "Set" object data. Omit set code to return all.

### `/symbols/set/{set-code | icon-code}`
Endpoint for accessing "SymbolSet" object data (expansion symbols). Omit code to return all.

### `/symbols/watermark/{watermark-name}`
Endpoint for accessing "SymbolWatermark" object data (watermarks). Omit watermark name to return all.