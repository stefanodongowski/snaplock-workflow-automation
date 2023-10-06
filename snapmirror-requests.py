import requests
import json
import warnings

warnings.filterwarnings('ignore') 


def get_licenses(volume_name, fields):
    url = f"https://10.62.217.230/api/cluster/licensing/licenses?name={volume_name}&fields={','.join(fields)}"

    payload={}
    headers = {
        'accept': 'application/json',
        'return_timeout': '15',
        'return_records': 'true',
        'Authorization': 'Basic ZHN0ZWZhbm86Q2FjaW9lUGVwZTE='
    }

    response = requests.request("GET", url, headers=headers, data=payload, verify=False)

    json.loads(response.text)

def get_version(fields):
    url = f"https://10.62.217.230/api/cluster?fields={','.join(fields)}"

    payload={}
    headers = {
        'accept': 'application/json',
        'return_timeout': '15',
        'return_records': 'true',
        'Authorization': 'Basic ZHN0ZWZhbm86Q2FjaW9lUGVwZTE='
    }

    response = requests.request("GET", url, headers=headers, data=payload, verify=False)

    return json.loads(response.text)

def get_volumes():
    url = "https://10.62.217.230/api/storage/volumes?type=rw&fields=name,type&return_records=true&return_timeout=15"

    payload = {}
    headers = {
    'accept': 'application/json',
    'authorization': 'Basic ZHN0ZWZhbm86Q2FjaW9lUGVwZTE='
    }

    response = requests.request("GET", url, headers=headers, data=payload, verify=False)

    volume_names = []
    volumes = json.loads(response.text)["records"]
    for volume in volumes:
        volume_names.append(volume["name"])

    return sorted(volume_names)

def get_volumes_in_relationships():
    url = "https://10.62.217.230/api/snapmirror/relationships?return_timeout=15&return_records=true"

    payload = {}
    headers = {
    'accept': 'application/json',
    'authorization': 'Basic ZHN0ZWZhbm86Q2FjaW9lUGVwZTE='
    }

    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    volumes = set()
    for record in json.loads(response.text)["records"]:
        source = record["source"]["path"].split('/')[-1]
        destination = record["destination"]["path"].split('/')[-1]
        volumes.add(source)
        volumes.add(destination)
        
    return sorted(list(volumes))
    
def get_volumes_not_in_relationships():
    all_volumes = get_volumes()
    volumes_in_relationships = get_volumes_in_relationships()

    for volume in all_volumes:
        if volume in volumes_in_relationships:
            all_volumes.remove(volume)

    return all_volumes



if __name__ == '__main__':
    print(get_volumes_not_in_relationships())





