import json

import msal

import requests


SCOPE = ["https://graph.microsoft.com/.default"]
AUTHORITY = "https://login.microsoftonline.com/a1d183f2-6c7b-4d9a-b994-5f2f31b3f780"

SELECT_FIELDS = [
    "Title", "DatasetDescription", "DatasetOwner", "Keywords_x002f_Tags", "Language",
    "LocationofData", "Landing_x0020_Page", "FrequencyofUpdates", "ProgramCode", "Identifier",
    "PublicAccessLevel", "ContainsGeospatialData", "Format_x0020_of_x0020_Data", "publisher",
    "bureauCode", "temporal", "dataQuality", "licene", "primaryITInvestmentUI",
    "Last_x0020_Known_x0020_Update"
]

SHAREPOINT_ENDPOINT = (
    "https://graph.microsoft.com/beta/sites/itaisinternationaltrade.sharepoint.com"
    ",c9cbc75a-c938-4fa7-bff1-7e60aa66b169,0ec156bc-3668-428a-80e8-fe0639999b70/"
    "lists/d966fffb-862a-4616-bcd5-10469ade35d5/items?expand=fields"
    "($select=" + ",".join(SELECT_FIELDS) + ")"
)


def get_sharepoint_graph_data():
    """Get new access_token from Azure, use it to make request to endpoint"""
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=AUTHORITY,
        client_credential=client_secret
    )
    result = app.acquire_token_for_client(scopes=SCOPE)

    graph_data = requests.get(
        SHAREPOINT_ENDPOINT,
        headers={"Authorization": "Bearer " + result["access_token"]}
    ).json()
    return graph_data


def get_public_datasets():
    for item in get_sharepoint_graph_data()["value"]:
        if (item["fields"].get("PublicAccessLevel") == "Public"):
            yield item


def convert_accrual_periodicity(word):
    switcher = {
        "Decennial": "R/P10Y",
        "Quadrennial": "R/P4Y",
        "Triennial": "R/P3Y",
        "Biennial": "R/P2Y",
        "Annual": "R/P1Y",
        "Semiannual": "R/P6M",
        "Three times per year": "R/P4M",
        "Quarterly": "R/P3M",
        "Bimonthly": "R/P2M",
        "Monthly": "R/P1M",
        "Semimonthly": "R/P0.5M",
        "Three times per month": "R/P0.33M",
        "Biweekly": "R/P2W",
        "Weekly": "R/P1W",
        "Three times per week": "R/P0.33W",
        "Semiweekly": "R/P3.5D",
        "Daily": "R/P1D",
        "Hourly": "R/PT1H",
        "Continuously": "R/PT1S",
    }
    return switcher.get(word, "irregular")


def make_array(things):
    try:
        return things.split("; ")
    except AttributeError:
        return None


def parse_name(email):
    return (" ").join(email.split("@")[0].split("."))


def convert_media_format(media):
    switcher = {
        "CSV": "text/csv",
        "HTML": "text/html",
        "PDF": "text/html",
        "TEXT": "text/html",
        "JSON": "application/json",
    }
    return switcher.get(media, media)


def convert_language_tag(input):
    languages = make_array(input)
    formatted_languages = []
    for language in languages:
        if (language == "English"):
            formatted_languages.append("en-US")
        elif (language == "Spanish"):
            formatted_languages.append("es-MX")
        else:
            formatted_languages.append(language)
    return formatted_languages


def clean_item(d):
    return {
        k: v
        for k, v in d.items()
        if v is not None
    }


def get_formatted_items():
    all_items = []
    for item in get_public_datasets():
        i = item["fields"]
        dataset = {}
        dataset["@type"] = "dcat:Dataset"
        dataset["title"] = i.get("Title")
        dataset["description"] = i.get("DatasetDescription")
        dataset["keyword"] = make_array(i.get("Keywords_x002f_Tags")) or ["Not Applicable"]
        dataset["modified"] = i.get("Last_x0020_Known_x0020_Update") or "2020-06-17"
        dataset["publisher"] = {
            "@type": "org:Organization",
            "name": i.get("publisher")
        }
        dataset["contactPoint"] = {
            "@type": "vcard:Contact",
            "fn": parse_name(i.get("DatasetOwner")),
            "hasEmail": "mailto:" + i.get("DatasetOwner")
        }
        dataset["identifier"] = i.get("Identifier")
        dataset["accessLevel"] = i.get("PublicAccessLevel").lower()
        dataset["bureauCode"] = make_array(i.get("bureauCode"))
        dataset["programCode"] = make_array(i.get("ProgramCode"))
        dataset["license"] = i.get("licene")  # this misspelling is consistent with SharePoint
        # dataset["spatial"] = i.get("ContainsGeospatialData") # Removed until corrected in SP
        dataset["temporal"] = i.get("temporal")
        dataset["mediaType"] = convert_media_format(i.get("Format_x0020_of_x0020_Data"))
        dataset["downloadURL"] = i.get("LocationofData")
        dataset["accrualPeriodicity"] = convert_accrual_periodicity(i.get("FrequencyofUpdates"))
        dataset["dataQuality"] = i.get("dataQuality")
        dataset["landingPage"] = i.get("Landing_x0020_Page")
        dataset["language"] = convert_language_tag(i.get("Language"))
        dataset["primaryITInvestmentUI"] = i.get("primaryITInvestmentUI")
        all_items.append(clean_item(dataset))
    return all_items


def handler():
    datasets = get_formatted_items()
    contents = {
        "@type": "dcat:Catalog",
        "describedBy": "https://project-open-data.cio.gov/v1.1/schema/catalog.json",
        "conformsTo": "https://project-open-data.cio.gov/v1.1/schema",
        "@context": "https://project-open-data.cio.gov/v1.1/schema/data.json",
        "dataset": datasets
    }
    with open('data.json', 'w') as f:
        print(f"📊 Found {len(datasets):d} public datasets")
        json.dump(contents, f)


handler()
