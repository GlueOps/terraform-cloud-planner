

import requests
import json
import os

TFC_TOKEN = os.environ['TFC_TOKEN']
TFC_ORGANIZATION_NAME = os.environ['TFC_ORGANIZATION_NAME']

TFC_API_BASE_URL = "https://app.terraform.io/api/v2"
headers = {
    'Authorization': 'Bearer ' + TFC_TOKEN,
    'Content-Type': 'application/vnd.api+json'
}

WORKSPACES = []


def run_plan_on_workspace(ws):
    """
     this function takes a workspace name and runs the plan on that workspace 
    """
    url = TFC_API_BASE_URL + "/runs"
    payload = json.dumps(
        {
            "data": {
                "attributes": {
                    "message": "Triggered to ensure to no IaC drift occurred",
                    "plan-only": False
                },
                "type": "runs",
                "relationships": {
                    "workspace": {
                        "data": {
                            "type": "workspaces",
                            "id": ""+ws+""
                        }
                    },
                }
            }
        }

    )
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def does_workspace_need_to_be_planned(workspace_id):
    """
    Check if the workspace needs to be planned. If it does, return true. Otherwise, return false.
    @param workspace_id - the workspace id
    @return True if the workspace needs to be planned, false otherwise
    """
    url = TFC_API_BASE_URL + "/workspaces/" + \
        workspace_id + "/runs?page[size]=1"
    response = requests.request("GET", url, headers=headers)
    response = json.loads(response.text)
    for x in response['data']:
        return True if x['attributes']['status'] in ["planned_and_finished", "applied"] else False


def get_all_workspaces(page_number=1):
    """
    Get all the workspaces from the TFC API.
    @param page_number - the page number to get from the API.
    @returns the workspaces
    """
    url = TFC_API_BASE_URL + \
        "/organizations/" + TFC_ORGANIZATION_NAME + "/workspaces?page[size]=100&page[number]="+str(
            page_number)
    global WORKSPACES

    response = requests.request("GET", url, headers=headers)
    response = json.loads(response.text)
    if response['meta']['pagination']['total-count'] > 0:
        for ws in response['data']:
            WORKSPACES.append(ws['id'])

    if response['meta']['pagination']['next-page'] != None:
        next_page = response['meta']['pagination']['next-page']
        get_all_workspaces(page_number=next_page)


if __name__ == '__main__':
    get_all_workspaces()
    for ws in WORKSPACES:
        if does_workspace_need_to_be_planned(ws):
            run_plan_on_workspace(ws)
