import os
import tempfile

import pytest
import requests

from nanopub.client import NANOPUB_TEST_GRLC_URL
from nanopub.definitions import TEST_RESOURCES_FILEPATH


def pytest_addoption(parser):
    parser.addoption('--no_rsa_key', action='store_true', default=False,
                     help="enable no_rsa_key decorated tests")


def pytest_configure(config):
    if not config.option.no_rsa_key:
        setattr(config.option, 'markexpr', 'not no_rsa_key')


skip_if_nanopub_server_unavailable = (
    pytest.mark.skipif(requests.get(NANOPUB_TEST_GRLC_URL).status_code != 200,
                       reason='Nanopub server is unavailable'))



# Create a temporary profile.yml file for testing
test_profile_path = os.path.join(tempfile.mkdtemp(), "profile.yml")
profile_yaml = f"""orcid_id: https://orcid.org/0000-0000-0000-0000
name: Python Tests
public_key: {os.path.join(TEST_RESOURCES_FILEPATH, "id_rsa.pub")}
private_key: {os.path.join(TEST_RESOURCES_FILEPATH, "id_rsa")}
introduction_nanopub_uri:
"""
with open(test_profile_path, "w") as f:
    f.write(profile_yaml)
