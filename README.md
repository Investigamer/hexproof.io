# Hexproof API
Hexproof is a Django-Ninja REST API for Magic the Gathering data and resources that takes in bulk 
data sets from a variety of sources and synthesizes it into comprehensive models. In terms of 
nomenclature, Hexproof is more similar to Scryfall than it is MTGJSON (snake_case). You can 
access the official live version of this API at [api.hexproof.io](https://api.hexproof.io), and the
API docs can be found [here](https://api.hexproof.io/docs).

We are building out additional image resource endpoints that other APIs seem to miss, one such 
resource is our `/symbols/` route that provides set rarity icon and watermark SVG's from a 
catalogue maintained on the [mtg-vectors](https://github.com/Investigamer/mtg-vectors) repository.

# Setup Guide
1. We use `poetry` for managing dependencies and packaging. To install poetry:
    ```shell
    # 1: Install pipx and ensure path.
    py -m pip install --user pipx
    py -m pipx ensurepath
    
    # 2: Install poetry.
    pipx install poetry

    # 3: [Optional] Configure poetry to create virtual environments in-project
    poetry config virtualenvs.in-project true
    ```
2. Clone the `hexproof` repository somewhere on your system and install the project environment with Poetry.
    ```shell
    # 1: Clone and enter the project.
    git clone https://github.com/Investigamer/hexproof.git
    cd hexproof

    # 2: Install the poetry environment.
    poetry install
    ```
3. Initialize the database and run the django test server:
    ```shell
    # 1: Enter poetry environment
    poetry shell

    # 2: Initialize database
    python manage.py migrate

    # 2.A: [Optional] Create an admin user for accessing admin page
    python manage.py createsuperuser # Follow the prompts
   
    # 3: Run django test server
    python manage.py runserver
    ```
4. The project is set up and the test server is running! You can check out the admin page
at `http://127.0.0.1:8000/admin` or view the API docs at `http://127.0.0.1:8000/docs`.