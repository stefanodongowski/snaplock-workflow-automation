import requests


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

    print(response.text)


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

    print(response.text)




if __name__ == '__main__':
    # get_licenses('snapmirror', ['name', "licenses"])
    get_version(['name', "version"])





