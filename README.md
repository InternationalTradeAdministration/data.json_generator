# data.json_generator

## Purpose
The enclosed function will eventually be deployed as an Azure function to generate the data.json file hosted at www.trade.gov/data.json as required by Project Open Data.

## Prerequisites
This project was developed in Python 3.7.7

## Getting Started
Make a virtual environment using the packages defined in `requirements-test.txt`. One way is like this:  
  * `mkvirtualenv -p /usr/local/bin/python3.8 -r requirements-test.txt errors`

### Tests
Coming soon. Meanwhile, linting is enabled by running `flake8`.

## Invoke
Add the client_id and client_secret, and run it with `python3 service.py`
