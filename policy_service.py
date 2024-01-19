'''
Policy service allows for the creation and modification of snaplock policies
'''
from ast import For
import json
import sched
import warnings
import requests
import cli_box
from simple_term_menu import TerminalMenu
from colorama import init, Fore, Style
init(autoreset=True)
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
        self.selected_svm = "None"
        self.policy_name = "None"
        self.schedule = "None"
        self.keep_count = "None"
        self.retention_period = "None"


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

    def clear_lines(self, num_lines):
        #TODO: Dynamic display
        for _ in range(num_lines):
            print ("\033[A                                                                                         \033[A")

    def show_policy_info(self):
        svm = "SVM: " + Fore.RED + self.selected_svm + Fore.BLACK + "\n"
        policy = "Policy name: " + Fore.RED + self.policy_name + Fore.BLACK + "\n"
        schedule = "Schedule: " + Fore.RED + self.schedule + Fore.BLACK + "\n"
        keep_count = "Keep count: " + Fore.RED + str(self.keep_count) + Fore.BLACK + "\n"
        retention_period = "Retention: " + Fore.RED + self.retention_period + Fore.BLACK + "\n"
        print(cli_box.rounded(
            svm + policy + schedule + keep_count + retention_period, align="left"
        ))

    def show_policy_menu(self):
        '''initiates policy creation menu'''
        svm_chosen = False
        name_chosen = False
        schedule_chosen = False
        count_chosen = False
        retention_chosen = False
        confirmed = False
        exited = False
        policy_creation_in_progress = ((not svm_chosen or 
                                        not name_chosen or 
                                        not schedule_chosen or 
                                        not count_chosen or 
                                        not retention_chosen or 
                                        not confirmed) and
                                        not exited)
        params_filled = (svm_chosen and 
                        name_chosen and 
                        schedule_chosen and 
                        count_chosen and 
                        retention_chosen)
        policy = {
            "copies": [
                {
                    "schedule": {
                        "name": None
                    },
                    "count": None,
                    "retention_period": None
                }
            ],
            "svm": {
                "name": None
            },
            "name": "tutorial_",
            "enabled": False
        }
        while policy_creation_in_progress:
            self.show_policy_info()

            options = ["SVM", "Policy name", "Schedule", "Count", "Retention Period", None, "Exit"]
            if params_filled:
                options.insert(6, "Create this policy")

            menu = TerminalMenu(options,
                                title="Provide the following policy parameters",
                                menu_cursor_style=("fg_blue", "bold"))
            
            selection_i = menu.show()
            selection = options[selection_i]
            match selection:
                case "SVM":
                    options = [x[0] for x in self.svms]
                    menu = TerminalMenu(options,
                                        title="Select an SVM",
                                        search_key='\\',
                                        menu_cursor_style=("fg_blue", "bold"))
                    selection_i = menu.show()            
                    policy["svm"]["name"] = options[selection_i]
                    self.selected_svm = Fore.GREEN + policy["svm"]["name"] + Fore.BLACK
                    svm_chosen = True
                case "Policy name":
                    policy["name"] = input("Policy name: ")
                    self.policy_name = Fore.GREEN + policy["name"] + Fore.BLACK
                    self.clear_lines(1)
                    name_chosen = True
                case "Schedule":
                    schedules = self.get_schedules()
                    options = [x["name"] for x in schedules]
                    menu = TerminalMenu(options,
                                        title="Select schedule",
                                        search_key='\\',
                                        menu_cursor_style=("fg_blue", "bold"))
                    selection_i = menu.show()
                    policy["copies"][0]["schedule"]["name"] = schedules[selection_i]["name"]
                    self.schedule = Fore.GREEN + policy["copies"][0]["schedule"]["name"] + Fore.BLACK
                    schedule_chosen = True
                case "Count":
                    policy["copies"][0]["count"] = str(input("Keep count: "))
                    self.keep_count = Fore.GREEN + policy["copies"][0]["count"] + Fore.BLACK
                    self.clear_lines(1)
                    count_chosen = True
                case "Retention Period":
                    policy["copies"][0]["retention_period"] = input("Select a retention period. \n\tW = weeks \n\tD = days \n\tH = hours \n\tM = minutes \n\tS = seconds\n(e.g. 20H = 20 hours):\n")
                    self.clear_lines(8)
                    self.retention_period = Fore.GREEN + "PT" + policy["copies"][0]["retention_period"]
                    retention_chosen = True
                case "Exit":
                    exited = True
                    self.clear_lines(8)
                    return {
                            "status" : "early exit",
                            "policy" : None
                           }
                case "Create this policy":
                    options = ["Yes", "No"]
                    menu = TerminalMenu(options,
                                        title="Are you sure you want to create this policy?",
                                        menu_cursor_style=("fg_blue", "bold"))
                    selection_i = menu.show()
                    if selection_i == 0:
                        self.selected_svm = Fore.RED + "None" + Fore.BLACK
                        self.policy_name = Fore.RED + "None" + Fore.BLACK
                        self.schedule = Fore.RED + "None" + Fore.BLACK
                        self.keep_count = Fore.RED + "None" + Fore.BLACK
                        self.retention_period = Fore.RED + 'None' + Fore.BLACK 
                        self.clear_lines(8)
                        confirmed = True
                        break

            policy_creation_in_progress = ((not svm_chosen or 
                                        not name_chosen or 
                                        not schedule_chosen or 
                                        not count_chosen or 
                                        not retention_chosen or 
                                        not confirmed) and
                                        not exited)
            params_filled = (svm_chosen and 
                            name_chosen and 
                            schedule_chosen and 
                            count_chosen and 
                            retention_chosen)
            
            print("\033[8A")
            
        return {
                "status" : "success",
                "policy" : policy 
               }
        # json.dumps(policy)
        # url = self.url + "/storage/snapshot-policies"
        # response = requests.request("POST", url, headers=self.headers, data=json.dumps(policy), verify=False)

        # if str(response.status_code) == "201":
        #     print(f"Successfully created policy {policy['name']}.")
        # else:
        #     print("Policy already exists. Choose a different name.")
