# Snaplock Workflow Automation

## Requirements
### Python Installation
Ensure you have Python 3.12+ installed by running the following command:
```python3 --version```
If you get an error indicating that you do not have Python installed, visit https://www.python.org/downloads/ and download the latest version. Follow the instructions on the installation wizard to ensure the latest version of Python is installed.

If the version is less than 3.12, update your local Python installation by visiting the above link.

Once Python is installed and updated to the latest version, navigate to the project folder and run ```python3 main.py```.
This will load the tool and run the necessary checks on your ONTAP cluster to ensure a snapshot policy can be created. Then, a menu of snapshot policy fields will be presented for you to fill out. Your current policy properties will be displayed in a in-terminal menu at the top of the terminal.

## APIs
The APIs used in this tool are all public-facing endpoints in ONTAP.
### Policy Creation
The following endpoints are called during the policy creation process.
#### /svm/svms
Retrieves the most up-to-date list of SVMs on the cluster.
#### /cluster/schedules
Retrieves the most up-to-date list of created schedules.
### Validation
The following endpoints are called during the cluster validation process.
#### /cluster/licensing/licenses
Retrieves all cluster licenses to check whether a valid snaplock license is installed.
#### /storage/snaplock/compliance-clocks
Retrieves a list of compliance clocks to check whether there exists a initialized compliance clock on the cluster
#### /cluster
Used to validate ONTAP version being 9.14+
#### /application/consistency-groups
Used to map consistency groups to their constituent volumes
#### /storage/volumes
Used to retrieve all type 'rw' volumes
#### /snapmirror/relationships
Used to check which of the rw volumes are already in a snapmirror relationship

## Policy Creation
When creating a policy, the user is prompted to define five properties of the new policy:
1. Policy name
2. SVM
3. Schedule
4. Keep Count
5. Retention Period

## Validation Check
When checking to see if a snaplock policy can be created for the given cluster, the following checks are run:
1. ONTAP version is 9.14+
2. Valid snaplock license is installed
3. Compliance clock is initialized
4. There exists rw volumes not currently in a snapmirror relationship
5. TODO: Check that the FabricPool policy is set to None



