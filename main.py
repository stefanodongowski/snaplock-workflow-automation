'''
Module to run snaplock policy creator
'''
import warnings
from validation_service import ValidationService
from policy_service import PolicyService
warnings.filterwarnings("ignore")


def main() -> None:
    '''Entry point to application'''
    validation_service = ValidationService()
    validation_service.run_validation()
    policy_service = PolicyService()
    policy_service.update_svms()

    # Allow user to customize their policy
    policy_service.show_policy_menu()


if __name__ == '__main__':
    main()
