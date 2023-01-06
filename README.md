# pokemon_tcg_collection_manager
A cli tool/library to manage, store and analyze a pokemon card collection
## Prerequisits:
* python3.10 or greater
* pip3 in path
* python3.10 in path
## Installation:
* run `pip3 install pokemonCardLogger` 
* or download zip and run `python3 setup.py install` in the directory you unzipped the zip file
## Use as a library:
* `from pokemonCardLogger import clss_pickle as pcl`
## Use as a program
* zipped install version is required
* in the install directory:
  * run `python3 pokemonCardLogger/main.py` for unix/mac 
  * run `python3.exe pokemonCardLogger\main.py` for windows
## To permannently set your api key:
* method 1:
  * make a file in the main package called "config.py"
  * enter in the file `API_KEY = "<your api key here>"`
  * save
* method 2:
  * set a enviroment variable: `API_KEY='<your api key here>'`
