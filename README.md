# Snaplock Workflow Automation

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



