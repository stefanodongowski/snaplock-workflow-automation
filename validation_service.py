'''
the validation service ensures the cluster can 
create a valid and usable snaplock policy
'''
import json
import sys
from re import L
import warnings
import requests
import cli_box
from colorama import init, Fore
from time import sleep
from simple_term_menu import TerminalMenu
init(autoreset=True)
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
        '''
        checks whether there is a compliant snaplock license installed
        on the cluster
        '''
        url = f"{self.url}/cluster/licensing/licenses?fields=name,state&return_records=true&return_timeout=15"

        response = requests.request("GET", url, headers=self.headers, verify=False, timeout=50)

        licenses = json.loads(response.text)["records"]
        for license_obj in licenses:
            if license_obj['name'] == 'snaplock' and license_obj['state'] == "compliant":
                return True
        return False

    def has_compliance_clock(self):
        '''
        checks whether there is a compliance clock initialized
        '''
        url = f"{self.url}/storage/snaplock/compliance-clocks?fields=*"

        response = requests.request("GET", url, headers=self.headers, verify=False, timeout=50)

        compliance_clocks = json.loads(response.text)["records"]
        if compliance_clocks:
            return True
        return False

    def get_version(self):
        '''
        retrieves the cluster ONTAP version
        '''
        url = f"{self.url}/cluster"

        response = requests.request("GET", url, headers=self.headers, verify=False, timeout=50)

        version = json.loads(response.text)['version']
        return version

    def get_cgs(self):
        '''
        retrieves consistency groups in cluster
        '''
        url = f"{self.url}/application/consistency-groups"
        response = requests.request("GET", url, headers=self.headers, verify=False, timeout=50)

        cgs = json.loads(response.text)["records"]
        return cgs


    def get_cg_volumes(self, uuid):
        '''
        maps all cgs to their member volumes
        '''
        url = f"{self.url}/application/consistency-groups/{uuid}?fields=volumes"
        response = requests.request("GET", url, headers=self.headers, verify=False, timeout=50)

        return [x["name"] for x in json.loads(response.text)["volumes"]]

    def get_rw_volumes(self):
        '''
        retrieves all volumes of type rw
        '''
        url = f"{self.url}/storage/volumes?type=rw&fields=name,type"

        response = requests.request("GET", url, headers=self.headers, verify=False, timeout=50)

        volume_names = []
        volumes = json.loads(response.text)["records"]
        for volume in volumes:
            volume_names.append(volume["name"])

        return sorted(volume_names)

    def get_volumes_in_relationships(self):
        '''
        retrieves all volumes in relationships
        '''
        url = f"{self.url}/snapmirror/relationships"

        response = requests.request("GET", url, headers=self.headers, verify=False, timeout=50)
        volumes = set()
        for record in json.loads(response.text)["records"]:
            source = record["source"]["path"].split('/')[-1]
            destination = record["destination"]["path"].split('/')[-1]
            volumes.add(source)
            volumes.add(destination)         
        return json.loads(response.text)["records"]
    
    def install_license(self):
        '''Installs the snaplock license'''
        menu = TerminalMenu(menu_entries=["Yes", "No"], title="Would you like to install a snaplock license?")
        selection_i = menu.show()
        if selection_i == 1:
            return False
        valid_key = False
        while not valid_key:
            print(cli_box.rounded("License Key: " + "_"*28))
            license_key = input("\033[2A\033[15C")
            if license_key == "":
                break
            elif len(license_key) > 28 or len(license_key) < 28:
                print(Fore.RED + "\033[1BKey must be 28 characters!\033[4A")
                continue
            else:
                url = f"{self.url}/cluster/licensing/licenses"
                response = requests.post(url=url, headers=self.headers, verify=False, json={"keys": [license_key]})
                if "error" in json.loads(response.text):
                    print(Fore.RED + "\033[1BInvalid key!                        \033[4A")
                else:
                    valid_key = True
        if not valid_key:
            return False
        print(Fore.GREEN + "\033[1BLicense successfully added.        ")
        return True

    def run_validation(self):
        '''
        runs a series of checks on the cluster to ensure it has a compliant
        version of ONTAP, valid snaplock license installed, initialized
        compliance clock, and elligible rw volumes not in relationships
        '''
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
            print(f"\t\U0000274C No valid license found. This may be due to a snaplock license not being installed or an existing one not being compliant.")
            license_installed = self.install_license()
            if not license_installed:
                print(Fore.RED + "\033[1BYou must obtain a valid license key to continue.")
                sleep(1)
                sys.exit()

        # Check whether compliance clock is initialized
        print("Checking if a compliance clock has been initialized...")
        clock_initialized = self.has_compliance_clock()
        if clock_initialized:
            print("\t\U00002705 Initialized compliance clock found.")
        else:
            print("\t\U0000274C No initialized compliance clock found. Initialize a compliance clock to proceed.")
            url = f"{self.url}/cluster/nodes"
            response = requests.request("GET", url, headers=self.headers, verify=False, timeout=50)
            options = [x["name"] for x in json.loads(response.text)["records"]]
            menu = TerminalMenu(options, multi_select=True, title="Press SPACE select the node(s) to initialize compliance clock:", menu_cursor_style=("fg_blue", "bold"), multi_select_cursor_style=("fg_blue", "bold"))
            selections = menu.show()
            for node in selections:
                node_to_initialize = {"node": {"name": node}}
                url = f"{self.url}/storage/snaplock/compliance-clocks"
                response = requests.request("POST", url=url, headers=self.headers, data=json.dumps(node_to_initialize), verify=False)
            print("Compliance clock initialized successfully!")
            
        # TODO # Check whether FabricPool policy is set to none
        # print("Checking if FabricPool policy is set to none...")

        print("Searching for read/write volumes...")
        volumes = self.get_rw_volumes()
        if volumes:
            print(f"\t\U00002705 {len(volumes)} read/write volumes found.")
        else:
            print("\t\U0000274C No read/write volumes found.")
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

        print("\n\U00002705 ---------- Validation check complete ----------- \U00002705\n")


if __name__ == '__main__':
    validation_service = ValidationService()
