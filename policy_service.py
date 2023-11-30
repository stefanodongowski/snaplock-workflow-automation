'''
policy services allows for the creation and modification of snaplock policies
'''
import json
import warnings
import requests
from simple_term_menu import TerminalMenu
warnings.filterwarnings('ignore')

class PolicyService():
    '''
    PolicyService acts as a instantiation of the policy service to be 
    injected into dependencies or the main method as needed
    '''

    def __init__(self):
        self.url = "https://rtp-sa-select01.naeastdemo.net/api"
        self.headers = {
            'accept': 'application/json',
            'return_timeout': '15',
            'return_records': 'true',
            'Authorization': 'Basic TkFFQVNUREVNT1xkc3RlZmFubzpDYWNpb2VQZXBlMQ=='
        }
        self.svms = []

    def update_svms(self):
        '''updates policy service with most recent list of svms in the cluster'''
        url = f"{self.url}/svm/svms"

        response = requests.request("GET", url, headers=self.headers, verify=False, timeout=50)

        svms = []
        for svm in json.loads(response.text)["records"]:
            svms.append((svm["name"], svm["uuid"]))

        self.svms = svms

    def get_schedules(self):
        '''retrieves cluster schedules'''
        url = f"{self.url}/cluster/schedules?order_by=name"

        response = requests.request("GET", url, headers=self.headers, verify=False, timeout=50)
        schedules = json.loads(response.text)["records"]
        return schedules


    def show_policy_menu(self):
        '''initiates policy creation menu'''
        svm_chosen = False
        name_chosen = False
        schedule_chosen = False
        count_chosen = False
        policy = {
            "svm": None,
            "name": None,
            "schedule": None,
            "count": None
        }
        while not svm_chosen or not name_chosen or not schedule_chosen or not count_chosen:
            options = ["SVM", "Policy name", "Schedule", "Count"]
            menu = TerminalMenu(options,
                                title="Create a policy",
                                menu_cursor_style=("fg_blue", "bold"))
            selection_i = menu.show()
            if selection_i == 0:
                options = [x[0] for x in self.svms]
                menu = TerminalMenu(options,
                                    title="Select an SVM",
                                    search_key='\\',
                                    menu_cursor_style=("fg_blue", "bold"))
                selection_i = menu.show()
                policy["svm"] = options[selection_i]
                svm_chosen = True
            elif selection_i == 1:
                policy["name"] = input("Policy name: ")
                name_chosen = True
            elif selection_i == 2:
                schedules = self.get_schedules()
                options = [x["name"] for x in schedules]
                menu = TerminalMenu(options,
                                    title="Select schedule",
                                    search_key='\\',
                                    menu_cursor_style=("fg_blue", "bold"))
                selection_i = menu.show()
                policy["schedule"] = schedules[selection_i]
                schedule_chosen = True
            elif selection_i == 3:
                policy["count"] = input("Keep count: ")
                count_chosen = True

        print(policy)
