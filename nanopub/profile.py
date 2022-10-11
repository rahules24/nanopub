# from functools import lru_cache
from pathlib import Path
from typing import Optional, Union

import yatiml
from Crypto.PublicKey import RSA
from base64 import decodebytes

from nanopub.definitions import DEFAULT_PROFILE_PATH, log

PROFILE_INSTRUCTIONS_MESSAGE = '''
    Follow these instructions to correctly setup your nanopub profile:
    https://nanopub.readthedocs.io/en/latest/getting-started/setup.html#setup-your-profile
'''


class ProfileError(RuntimeError):
    """
    Error to be raised if profile is not setup correctly.
    """


class Profile:
    """Represents a user profile.

    Attributes:
        orcid_id: The user's ORCID
        name: The user's name
        public_key: Path to the user's public key or string
        private_key: Path to the user's private key or string
        introduction_nanopub_uri: URI of the user's profile nanopub
    """

    def __init__(
            self,
            orcid_id: str,
            name: str,
            private_key: Union[Path,str],
            public_key: Optional[Union[Path,str]] = None,
            introduction_nanopub_uri: Optional[str] = None
    ) -> None:
        """Create a Profile."""
        self.orcid_id = orcid_id
        self.name = name
        self.introduction_nanopub_uri = introduction_nanopub_uri

        if isinstance(private_key, Path):
            try:
                with open(private_key, 'r') as f:
                    self.private_key = f.read().strip()
            except FileNotFoundError:
                raise ProfileError(
                    f'Private key file {private_key} for nanopub not found.\n'
                    f'Maybe your nanopub profile was not set up yet or not set up '
                    f'correctly. \n{PROFILE_INSTRUCTIONS_MESSAGE}'
                )
        else:
            self.private_key = private_key

        if not public_key:
            log.info('Public key not provided when loading the Nanopub profile, generating it from the provided private key')
            key = RSA.importKey(decodebytes(self.private_key.encode()))
            self.public_key = key.publickey().export_key().decode('utf-8')
        else:
            if isinstance(public_key, Path):
                try:
                    with open(public_key, 'r') as f:
                        self.public_key = f.read().strip()
                except FileNotFoundError:
                    raise ProfileError(
                        f'Private key file {public_key} for nanopub not found.\n'
                        f'Maybe your nanopub profile was not set up yet or not set up '
                        f'correctly. \n{PROFILE_INSTRUCTIONS_MESSAGE}'
                    )
            else:
                self.public_key = public_key


    # TODO: remove?
    def get_public_key(self) -> str:
        """Returns the user's public key."""
        return self.public_key

    def get_private_key(self) -> str:
        """Returns the user's private key."""
        return self.private_key


class ProfileLoader(Profile):
    """A class to load a user profile from a local YAML file."""
    def __init__(
            self,
            orcid_id: str,
            name: str,
            private_key: Path,
            public_key: Optional[Path],
            introduction_nanopub_uri: Optional[str] = None
    ) -> None:
        """Create a Profile."""
        super().__init__(
            orcid_id=orcid_id,
            name=name,
            private_key=private_key,
            public_key=public_key,
            introduction_nanopub_uri=introduction_nanopub_uri,
        )


_load_profile = yatiml.load_function(ProfileLoader)


_dump_profile = yatiml.dump_function(ProfileLoader)


# TODO: remove
def get_orcid_id() -> str:
    """Returns the user's ORCID."""
    return load_profile().orcid_id


# @lru_cache()
def load_profile(profile_path: Union[Path, str] = DEFAULT_PROFILE_PATH) -> Profile:
    """Retrieve nanopub user profile.

    By default the profile is stored in `HOME_DIR/.nanopub/profile.yaml`.

    Returns:
        A Profile containing the data from the configuration file.

    Raises:
        yatiml.RecognitionError: If there is an error in the file.
    """
    try:
        if profile_path:
            return _load_profile(Path(profile_path))
        else:
            return _load_profile(DEFAULT_PROFILE_PATH)
    except (yatiml.RecognitionError, FileNotFoundError) as e:
        msg = (f'{e}\nYour nanopub profile has not been set up yet, or is not set up correctly.\n'
               f'{PROFILE_INSTRUCTIONS_MESSAGE}')
        raise ProfileError(msg)



# TODO: fix for new Profile class
def store_profile(profile: Profile) -> Path:
    """Stores the nanopub user profile.

    By default the profile is stored in `HOME_DIR/.nanopub/profile.yaml`.

    Args:
        profile: The profile to store as the user's profile.

    Returns:
        The path where the profile was stored.

    Raises:
        yatiml.RecognitionError: If there is an error in the file.
    """
    _dump_profile(profile, DEFAULT_PROFILE_PATH)
    return DEFAULT_PROFILE_PATH
