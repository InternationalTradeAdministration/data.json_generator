import json

import msal

import requests


SCOPE = ["https://graph.microsoft.com/.default"]
AUTHORITY = "https://login.microsoftonline.com/a1d183f2-6c7b-4d9a-b994-5f2f31b3f780"

SELECT_FIELDS = [
    "Title", "DatasetDescription", "DatasetOwner", "BusinessUnit", "Keywords_x002f_Tags",
    "Language", "LocationofData", "Landing_x0020_Page", "FrequencyofUpdates",
    "Last_x0020_Known_x0020_Update", "Machine_x002d_ReadableFormat_x00", "ProgramCode",
    "Identifier", "PublicAccessLevel", "ContainsGeospatialData", "Format_x0020_of_x0020_Data",
    "Last_x0020_Validated", "conformsTo", "publisher", "bureauCode", "systemOfRecords",
    "SORNNumber", "accessURL", "temporal", "rights", "references", "dataQuality", "describedBy",
    "issued", "licene", "primaryITInvestmentUI", "categoryMarkingCUI", "Modified"
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


def get_formatted_items():
    all_items = []
    for item in get_public_datasets():
        i = item["fields"]
        dataset = {}
        dataset["title"] = i.get("Title")
        dataset["description"] = i.get("DatasetDescription")
        dataset["contactPoint"] = i.get("DatasetOwner")
        dataset["businessUnit"] = i.get("BusinessUnit")
        dataset["keyword"] = i.get("Keywords_x002f_Tags")
        dataset["language"] = i.get("Language")
        dataset["downloadURL"] = i.get("LocationofData")
        dataset["landingPage"] = i.get("Landing_x0020_Page")
        dataset["accrualPeriodicity"] = i.get("FrequencyofUpdates")
        dataset["datasetModified"] = i.get("Last_x0020_Known_x0020_Update")
        dataset["machineReadable"] = i.get("Machine_x002d_ReadableFormat_x00")
        dataset["programCode"] = i.get("ProgramCode")
        dataset["identifier"] = i.get("Identifier")
        dataset["accessLevel"] = i.get("PublicAccessLevel")
        dataset["spatial"] = i.get("ContainsGeospatialData")
        dataset["mediaType"] = i.get("Format_x0020_of_x0020_Data")
        dataset["lastValidated"] = i.get("Last_x0020_Validated")
        dataset["conformsTo"] = i.get("conformsTo")
        dataset["publisher"] = i.get("publisher")
        dataset["bureauCode"] = i.get("bureauCode")
        dataset["systemOfRecords"] = i.get("systemOfRecords")
        dataset["SORNNumber"] = i.get("SORNNumber")
        dataset["accessURL"] = i.get("accessURL")
        dataset["temporal"] = i.get("temporal")
        dataset["rights"] = i.get("rights")
        dataset["references"] = i.get("references")
        dataset["dataQuality"] = i.get("dataQuality")
        dataset["describedBy"] = i.get("describedBy")
        dataset["issued"] = i.get("issued")
        dataset["license"] = i.get("licene")  # this misspelling is consistent with SharePoint
        dataset["primaryITInvestmentUI"] = i.get("primaryITInvestmentUI")
        dataset["categoryMarkingCUI"] = i.get("categoryMarkingCUI")
        dataset["modified"] = i.get("Modified")
        dataset["modifiedBy"] = item["lastModifiedBy"]["user"]["displayName"]
        all_items.append(dataset)
    return all_items


def handler():
    datasets = get_formatted_items()
    with open('data.json', 'w') as f:
        print(f"📊 Found {len(datasets):d} public datasets")
        json.dump(datasets, f)


handler()
