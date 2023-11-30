import requests
import json
import warnings
from colorama import Fore
warnings.filterwarnings('ignore') 


class ValidationService():
    '''
    In order for a volume to be eligible for snapmirror, it must meet the following conditions:
    1) ONTAP 9.13+
    2) Has the snapmirror license installed
    3) Must not already be in a relationship

    select01 auth = TkFFQVNUREVNT1xkc3RlZmFubzpDYWNpb2VQZXBlMQ==
    select02 auth = ZHN0ZWZhbm86Q2FjaW9lUGVwZTE=
    '''

    def __init__(self):
        self.url = "https://rtp-sa-select01.naeastdemo.net/api"
        self.headers = {
            'accept': 'application/json',
            'return_timeout': '15',
            'return_records': 'true',
            'Authorization': 'Basic TkFFQVNUREVNT1xkc3RlZmFubzpDYWNpb2VQZXBlMQ=='
        }
        self.eligible_volumes = []


    def has_compliant_snaplock(self):
        # Returns whether the given cluster 
        url = f"{self.url}/cluster/licensing/licenses?fields=name,state&return_records=true&return_timeout=15"

        response = requests.request("GET", url, headers=self.headers, verify=False)

        licenses = json.loads(response.text)["records"]
        for license in licenses:
            if license['name'] == 'snaplock' and license['state'] == "compliant":
                return True
        return False

    def has_compliance_clock(self):
        url = f"{self.url}/storage/snaplock/compliance-clocks?fields=*"

        response = requests.request("GET", url, headers=self.headers, verify=False)

        compliance_clocks = json.loads(response)["records"]
        if compliance_clocks:
            return True
        return False

    def get_version(self):
        url = f"{self.url}/cluster"

        response = requests.request("GET", url, headers=self.headers, verify=False)

        version = json.loads(response.text)['version']
        return version

    def get_cgs(self):
        url = f"{self.url}/application/consistency-groups"
        response = requests.request("GET", url, headers=self.headers, verify=False)

        cgs = json.loads(response.text)["records"]
        return cgs


    def get_cg_volumes(self, uuid):
        url = f"{self.url}/application/consistency-groups/{uuid}?fields=volumes"
        response = requests.request("GET", url, headers=self.headers, verify=False)

        return [x["name"] for x in json.loads(response.text)["volumes"]]

    def get_rw_volumes(self):
        url = f"{self.url}/storage/volumes?type=rw&fields=name,type"

        response = requests.request("GET", url, headers=self.headers, verify=False)

        volume_names = []
        volumes = json.loads(response.text)["records"]
        for volume in volumes:
            volume_names.append(volume["name"])

        return sorted(volume_names)

    def get_volumes_in_relationships(self):
        url = f"{self.url}/snapmirror/relationships"

        response = requests.request("GET", url, headers=self.headers, verify=False)
        volumes = set()
        for record in json.loads(response.text)["records"]:
            source = record["source"]["path"].split('/')[-1]
            destination = record["destination"]["path"].split('/')[-1]
            volumes.add(source)
            volumes.add(destination)
            
        return json.loads(response.text)["records"]

    def run_validation(self):
        # Verify ONTAP version
        print("Checking if valid ONTAP version is available...")
        version = self.get_version()
        if int(version["generation"]) == 9 and int(version["major"]) >= 13:
            print(f"\t\U00002705 ONTAP version {version['generation']}.{version['major']} meets version requirement.")
        else:
            print(f"\t\U0000274C ONTAP {version['generation']}.{version['major']} does not meet version requirement. Please upgrade to a later ONTAP version.")
            exit()

        # Check whether snaplock is installed and is compatible
        print("Checking if valid snaplock license is installed...")
        license_installed = self.has_compliant_snaplock()
        if license_installed:
            print("\t\U00002705 Valid snaplock license found.")
        else:
            print("\t\U0000274C No valid license found. This may be due to a snaplock license not being installed or an existing one not being compliant. \n\t  Please follow these instructions to install a snaplock license <link to installation instructions>.")
            exit()

        # Check whether compliance clock is initialized
        print("Checking if a compliance clock has been initialized...")
        clock_initialized = self.has_compliant_snaplock()
        if clock_initialized:
            print("\t\U00002705 Initialized compliance clock found.")
        else:
            print("\t\U0000274C No initialized compliance clock found. Initialize a compliance clock to proceed.")
            exit()
        
        # TODO # Check whether FabricPool policy is set to none
        # print("Checking if FabricPool policy is set to none...")

        print("Searching for read/write volumes...")
        volumes = self.get_rw_volumes()
        if volumes:
            print(f"\t\U00002705 {len(volumes)} read/write volumes found.")
        else:
            print("\t\U0000274C No read\write volumes found.")
            exit()

        print("Checking for volumes not in a snapmirror relationship...")
        volumes_in_relationships = self.get_volumes_in_relationships()
        if volumes_in_relationships:
            print(f"\t\U00002705 {len(volumes_in_relationships)} of those volumes are not in a snapmirror relationship.")
        else:
            print("\t\U0000274C No eligible volumes found.")
            exit()

        eligible_volumes = set()
        for volume in volumes:
            if volume not in volumes_in_relationships:
                eligible_volumes.add(volume)

        eligible_volumes = sorted(list(eligible_volumes))
        self.eligible_volumes = eligible_volumes

        print(Fore.GREEN + "\n\U00002705 ---------- Validation check complete ----------- \U00002705\n")


if __name__ == '__main__':
    validation_service = ValidationService()





