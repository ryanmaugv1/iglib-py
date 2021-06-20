# IGLIB-PY

> Unofficial Python Client For IG REST API.

This library stems from one of my own projects which I decided to rip out the client code and open-source.

It provides a variety of useful things, such as:

- IG Client (`ig_client.py`)
  - Robust implementation of IG REST client including most of the fundemental and core endpoints (found [here](https://labs.ig.com/rest-trading-api-reference)).
  - Feel free to contribute your implementation of unsupported endpoints or improve test.
- Data Wrappers (`wrappers/...`)
  - Custom data wrappers for common IG response objects e.g. `IGAccount`, `IGWatchlist`, `IGPosition` etc.
- Utility Classes (`utility/...`)
  - Utilities which make working with library and IG objects easier.
 
 ## Installation
 
 1. Ensure Python Version `>= 3`.
 2. Install Library Dependancies.
    - `pip install jsonpickle requests`
 3. Clone Repository.
    - `git clone https://github.com/ryanmaugv1/iglib-py`
 4. Move into project directory.
 5. Import client (`ig_client.py`) like you would any other local module.
 6. Done.
  
 ## Author
 
 Ryan Maugin (@ryanmaugv1)
 
 ryanmaugv1@gmail.com
