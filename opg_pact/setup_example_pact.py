import requests
import pytest
import json
from opg_pact.check_pact_deployable import PactDeploymentCheck

provider_base_url = "http://localhost:5000"
provider_custom_header = "Authorization: asdf1234567890"
pact_broker_url = "http://localhost:9292"
broker_user_name = "admin"
broker_secret_name = "local"  # pactbroker_admin
consumer_pacticipant = "OPGExampleApp"
provider_pacticipant = "OPGExampleAPI"
api_version = "v1"
git_commit_consumer = "x123456"
git_commit_provider = "z123456"
broker_password = "password"
headers = {'Content-Type': 'application/json'}
file = "contract.json"

pact_check = PactDeploymentCheck(
  provider_base_url,
  provider_custom_header,
  pact_broker_url,
  broker_user_name,
  broker_secret_name,
  consumer_pacticipant,
  provider_pacticipant,
  api_version,
  git_commit_consumer,
  git_commit_provider
)

def create_pact(
    git_commit_consumer,
    provider_pacticipant,
    consumer_pacticipant,
    file,
    broker_user_name = "admin",
    broker_password = "password",
    headers = {'Content-Type': 'application/json'},
    ):
  full_url = f"{pact_broker_url}/pacts/provider/{provider_pacticipant}/consumer/{consumer_pacticipant}/version/{git_commit_consumer}"
  pact_response = requests.put(full_url, data=open(file, 'rb'), auth=(broker_user_name, broker_password),headers=headers)
  if pact_response.status_code < 399:
    return True
  else:
    return False

def delete_pact(
    consumer_pacticipant,
    provider_pacticipant,
    broker_user_name = "admin",
    broker_password = "password",
    headers = {'Content-Type': 'application/json'},
    ):
    full_url = f"{pact_broker_url}/pacticipants/{consumer_pacticipant}"
    pact_response = requests.delete(full_url, auth=(broker_user_name, broker_password), headers=headers)
    if pact_response.status_code < 399:
        consumer_deleted = True
    else:
        consumer_deleted = False
    full_url = f"{pact_broker_url}/pacticipants/{provider_pacticipant}"
    pact_response = requests.delete(full_url, auth=(broker_user_name, broker_password), headers=headers)
    if pact_response.status_code < 399 and consumer_deleted:
        return True
    else:
        return False


def tag_consumer_pact(
    git_commit_consumer,
    consumer_pacticipant,
    broker_user_name = "admin",
    broker_password = "password",
    headers = {'Content-Type': 'application/json'},
    ):
  full_url = f"{pact_broker_url}/pacticipants/{consumer_pacticipant}/versions/{git_commit_consumer}/tags/v1"
  pact_response = requests.put(full_url, auth=(broker_user_name, broker_password), headers=headers)
  if pact_response.status_code < 399:
    return True
  else:
    return False

def tag_prod_consumer_pact(
    git_commit_consumer,
    consumer_pacticipant,
    broker_user_name = "admin",
    broker_password = "password",
    headers = {'Content-Type': 'application/json'},
    ):
  full_url = f"{pact_broker_url}/pacticipants/{consumer_pacticipant}/versions/{git_commit_consumer}/tags/v1_production"
  pact_response = requests.put(full_url, auth=(broker_user_name, broker_password), headers=headers)
  if pact_response.status_code < 399:
    return True
  else:
    return False

def tag_prod_provider_pact(
    git_commit_provider,
    provider_pacticipant,
    broker_user_name = "admin",
    broker_password = "password",
    headers = {'Content-Type': 'application/json'},
    ):
  full_url = f"{pact_broker_url}/pacticipants/{provider_pacticipant}/versions/{git_commit_provider}/tags/v1_production"
  pact_response = requests.put(full_url, auth=(broker_user_name, broker_password), headers=headers)
  if pact_response.status_code < 399:
    return True
  else:
    return False

# ==== CONSUMER SIDE NO PROVIDER CREATED

# # CREATE THE PACT
# full_url = f"{pact_broker_url}/pacts/provider/{provider_pacticipant}/consumer/{consumer_pacticipant}/version/{git_commit_consumer}"
# pact_response = requests.put(full_url, data=open('contract.json', 'rb'), auth=(broker_user_name, broker_password), headers=headers)
# print(pact_response)
# message = pact_check.consumer_can_i_deploy()
#
# assert message == "Consumer has no Tags"

# # TAG IT WITH V1
# full_url = f"{pact_broker_url}/pacticipants/{consumer_pacticipant}/versions/{git_commit_consumer}/tags/v1"
# pact_response = requests.put(full_url, auth=(broker_user_name, broker_password), headers=headers)
# print(pact_response)
#
# message, fail_build = pact_check.consumer_can_i_deploy()
# print(message)
# assert message == f"Consumer Side 'Can I Deploy' Failed! No pacts or verifications have been published for version {git_commit_consumer}"
# assert fail_build == True

# # TAG IT WITH V1_PRODUCTION
# full_url = f"{pact_broker_url}/pacticipants/{consumer_pacticipant}/versions/x12345/tags/v1_production"
# pact_response = requests.put(full_url, auth=(broker_user_name, broker_password), headers=headers)
# print(pact_response)
# message, fail_build = pact_check.consumer_can_i_deploy()
# print(message)
# assert message == f"Consumer Side 'Can I Deploy' Failed! No pacts or verifications have been published for version {git_commit_consumer}"
# assert fail_build == True

# DELETE IT
# full_url = f"{pact_broker_url}/pacticipants/{consumer_pacticipant}"
# pact_response = requests.delete(full_url, auth=(broker_user_name, broker_password), headers=headers)
# print(pact_response)
# message, fail_build = pact_check.consumer_can_i_deploy()
# print(message)

# ==== PROVIDER SIDE

# # CREATE THE PACT
# full_url = f"{pact_broker_url}/pacts/provider/{provider_pacticipant}/consumer/{consumer_pacticipant}/version/{git_commit_consumer}"
# pact_response = requests.put(full_url, data=open('contract.json', 'rb'), auth=(broker_user_name, broker_password), headers=headers)
# print(pact_response)
# message, fail_build = pact_check.provider_can_i_deploy()
# print(message)
# assert message == "Failure! No verification processed"

# # TAG IT WITH V1
# full_url = f"{pact_broker_url}/pacticipants/{consumer_pacticipant}/versions/{git_commit_consumer}/tags/v1"
# pact_response = requests.put(full_url, auth=(broker_user_name, broker_password), headers=headers)
# print(pact_response)
# message, fail_build = pact_check.provider_can_i_deploy()
# print(message)
# assert message == "Provider Side 'Can I Deploy' Successful but against non production tag"

# # TAG IT WITH V1_PRODUCTION
# full_url = f"{pact_broker_url}/pacticipants/{consumer_pacticipant}/versions/x123456/tags/v1_production"
# pact_response = requests.put(full_url, auth=(broker_user_name, broker_password), headers=headers)
# print(pact_response)
# message, fail_build = pact_check.provider_can_i_deploy()
# print(message)
# print(fail_build)
# assert message == f"Provider Side 'Can I Deploy' Successful"


# # DELETE IT
# full_url = f"{pact_broker_url}/pacticipants/{consumer_pacticipant}"
# pact_response = requests.delete(full_url, auth=(broker_user_name, broker_password), headers=headers)
# print(pact_response)


# ==== CONSUMER SIDE WITH EXISTING PROVIDER CHECK

# CREATE THE PACT AND TAG IT WITH v1
# full_url = f"{pact_broker_url}/pacts/provider/{provider_pacticipant}/consumer/{consumer_pacticipant}/version/{git_commit_consumer}"
# pact_response = requests.put(full_url, data=open('contract.json', 'rb'), auth=(broker_user_name, broker_password),
#                              headers=headers)
# print(pact_response)
# full_url = f"{pact_broker_url}/pacticipants/{consumer_pacticipant}/versions/{git_commit_consumer}/tags/v1"
# pact_response = requests.put(full_url, auth=(broker_user_name, broker_password), headers=headers)
# message, fail_build = pact_check.provider_can_i_deploy()
# message, fail_build = pact_check.consumer_can_i_deploy()
#
# print(message)

# # CONSUMER SIDE WITH EXISTING PROVIDER BUT NO PROVIDER PROD TAG (fail as no v1_production tag on provider)
# delete_pact(consumer_pacticipant, provider_pacticipant)
# create_pact(git_commit_consumer, provider_pacticipant, consumer_pacticipant, file)
# tag_consumer_pact(git_commit_consumer, consumer_pacticipant)
# pact_check.provider_can_i_deploy()
# message, fail_build = pact_check.consumer_can_i_deploy()
# assert message == "Consumer Side 'Can I Deploy' Failed! No matching provider pact with v1_production tag!"
# assert fail_build

# # CONSUMER SIDE TAG V1 WITH PROVIDER TAG V1_PRODUCTION
delete_pact(consumer_pacticipant, provider_pacticipant)
create_pact(git_commit_consumer, provider_pacticipant, consumer_pacticipant, file)
tag_consumer_pact(git_commit_consumer, consumer_pacticipant)
pact_check.provider_can_i_deploy()
tag_prod_provider_pact(git_commit_provider, provider_pacticipant)
message, fail_build = pact_check.consumer_can_i_deploy()
assert message == "Provider Side 'Can I Deploy' Successful"
assert not fail_build

