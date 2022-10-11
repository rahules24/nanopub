import os
import tempfile

from rdflib import BNode, Graph, Literal

from nanopub import NanopubClient, NanopubConfig, namespaces
from nanopub.definitions import TEST_RESOURCES_FILEPATH
from tests.conftest import test_profile_path
# from tests.conftest import skip_if_nanopub_server_unavailable


client = NanopubClient(
    use_test_server=True,
    profile_path=test_profile_path,
    # sign_explicit_private_key=True,
    nanopub_config=NanopubConfig(
        add_prov_generated_time=False,
        add_pubinfo_generated_time=False,
        attribute_assertion_to_profile=True,
        attribute_publication_to_profile=True,
        assertion_attributed_to=None,
        publication_attributed_to=None,
        derived_from=None
    )
)

# TEST_ASSERTION = (namespaces.AUTHOR.DrBob, namespaces.HYCL.claims, rdflib.Literal('This is a test'))
# PUBKEY = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCC686zsZaQWthNDSZO6unvhtSkXSLT8iSY/UUwD/' \
#          '7T9tabrEvFt/9UPsCsg/A4HG6xeuPtL5mVziVnzbxqi9myQOY62LBja85pYLWaZPUYakP' \
#          'HyVm9A0bRC2PUYZde+METkZ6eoqLXP26Qo5b6avPcmNnKkr5OQb7KXaeX2K2zQQIDAQAB'
# NANOPUB_SAMPLE_SIGNED = str(TEST_RESOURCES_FILEPATH / 'nanopub_sample_signed.trig')


class TestSigner:


    def test_nanopub_sign(self):
        expected_np_uri = "http://purl.org/np/RAmdN3ynXoyMki1Ab9j9O4KWnX2hj7ETw3PdKtOMkpvhY"

        assertion = Graph()
        assertion.add((
            BNode('test'), namespaces.HYCL.claims, Literal('This is a test of nanopub-python')
        ))

        # test_concept = rdflib.term.BNode('test')
        # test_published_uri = 'http://www.example.com/my-nanopub'
        # expected_concept_uri = 'http://www.example.com/my-nanopub#test'
        # client.java_wrapper.publish = mock.MagicMock(return_value=test_published_uri)

        np = client.create_nanopub(
            assertion=assertion,
            # introduces_concept=test_concept,
        )
        np = client.sign(np)
        print(np.rdf.serialize(format="trig"))
        print(np.source_uri)
        assert np.source_uri == expected_np_uri




    # def test_assertion_rdf_not_mutated(self):
    #     """
    #     Check that the assertion rdf graph provided by the user
    #     is not mutated by publishing in instances where it contains
    #     a BNode.
    #     """
    #     rdf = rdflib.Graph()
    #     rdf.add((rdflib.BNode('dontchangeme'), rdflib.RDF.type, rdflib.FOAF.Person))
    #     publication = Publication.from_assertion(assertion_rdf=rdf)

    #     client = NanopubClient()
    #     client.java_wrapper.publish = mock.MagicMock()
    #     client.publish(publication)

    #     assert (rdflib.BNode('dontchangeme'), rdflib.RDF.type, rdflib.FOAF.Person) in rdf

    # def test_retract_with_force(self):
    #     client = NanopubClient()
    #     client.java_wrapper.publish = mock.MagicMock()
    #     client.retract('http://www.example.com/my-nanopub', force=True)

    # TODO: Not sure how to use mocks in this case (we want to get rid of the static get_public_key)
    # @mock.patch('nanopub.client.profile.get_public_key')
    # def test_retract_without_force(self, mock_get_public_key):
    #     test_uri = 'http://www.example.com/my-nanopub'
    #     test_public_key = 'test key'
    #     client = NanopubClient()
    #     client.java_wrapper.publish = mock.MagicMock()

    #     # Return a mocked to-be-retracted publication object that is signed with public key
    #     mock_publication = mock.MagicMock()
    #     mock_publication.pubinfo = rdflib.Graph()
    #     mock_publication.signed_with_public_key = test_public_key
    #     client.fetch = mock.MagicMock(return_value=mock_publication)

    #     client = NanopubClient()
    #     # Retract should be successful when public keys match
    #     mock_get_public_key.return_value = test_public_key
    #     client.retract(test_uri)

    #     # And fail if they don't match
    #     mock_get_public_key.return_value = 'Different public key'
    #     with pytest.raises(AssertionError):
    #         client.retract(test_uri)
