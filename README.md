# data.json_generator

## Purpose
The enclosed function generates the data.json file, which is to be hosted at www.trade.gov/data.json as required by Project Open Data.

It draws data from the [SharePoint list](https://itaisinternationaltrade.sharepoint.com/sites/DataPractitionersCommunityofPractice/Lists/Enterprise%20Data%20Inventory/AllItems.aspx) using the Microsoft Graph API, and standardizes the output to align with the [DCAT-US Schema v1.1 (Project Open Data Metadata Schema)](https://resources.data.gov/resources/dcat-us/)

Some notes and choices that may need revisiting later:
- The **`modified`** field is mandatory and must be a date string (`YYYY-MM-DDThh:mm:ss.sTZD`), and although it's uncommon for this field to be blank, the default value is hard-coded as `2020-06-17` (service.py#L125).
- Even though it's included in the API output, the **`spatial`** entry (service.py#L140) is commented out, because if present, must match one of several formats (a location that's recognized as a GeoName, coordinates, bounds or similar). It's ready to be re-activated in case it becomes useful.

## Prerequisites
This project requires Python 3.x

## Getting Started
Make a virtual environment using the packages defined in `requirements-test.txt`. One way is like this:  
```
mkvirtualenv -p /usr/local/bin/python3.8 -r requirements-test.txt errors
```

Linting is enabled by running `python3 -m flake8`.

## How to use
Replace the client_id (service.py#L29) and client_secret (service.py#L31) with the correct values, and run it with
```
python3 service.py
```
It will generate the output in a file titled "data.json" in the root of the project.
