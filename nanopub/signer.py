from base64 import decodebytes, encodebytes

import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from rdflib import BNode, ConjunctiveGraph, Literal, Namespace, URIRef

from nanopub.definitions import DUMMY_NAMESPACE, DUMMY_URI, FINAL_NANOPUB_URI, NANOPUB_SERVER_LIST, log
from nanopub.namespaces import NPX
from nanopub.profile import Profile
from nanopub.trustyuri.rdf import RdfHasher, RdfUtils
from nanopub.trustyuri.rdf.RdfPreprocessor import transform


def add_signature(g: ConjunctiveGraph, profile: Profile) -> ConjunctiveGraph:
    """Implementation in python of the process to sign with the private key"""
    # TODO: Add signature triples
    g.add((
        DUMMY_NAMESPACE["sig"],
        NPX["hasPublicKey"],
        Literal(profile.public_key),
        DUMMY_NAMESPACE["pubInfo"],
    ))
    g.add((
        DUMMY_NAMESPACE["sig"],
        NPX["hasAlgorithm"],
        Literal("RSA"),
        DUMMY_NAMESPACE["pubInfo"],
    ))
    g.add((
        DUMMY_NAMESPACE["sig"],
        NPX["hasSignatureTarget"],
        DUMMY_URI,
        DUMMY_NAMESPACE["pubInfo"],
    ))
    # Normalize RDF
    # print("NORMED RDF STARTS")
    quads = RdfUtils.get_quads(g)

    # TODO: the disgusting rdflib warnings "does not look like a valid URI, trying to serialize this will break." shows up here
    normed_rdf = RdfHasher.normalize_quads(
        quads,
        baseuri=str(DUMMY_NAMESPACE),
        hashstr=" "
    )
    # Be careful: normed_rdf needs to end with a newline
    # print("NORMED RDF STARTS")
    # print(normed_rdf)
    # print("NORMED RDF END")

    # Signature signature = Signature.getInstance("SHA256withRSA");
    # https://stackoverflow.com/questions/55036059/a-java-server-use-sha256withrsa-to-sign-message-but-python-can-not-verify
    private_key = RSA.importKey(decodebytes(profile.private_key.encode()))
    signer = PKCS1_v1_5.new(private_key)
    signature_b = signer.sign(SHA256.new(normed_rdf.encode()))
    signature = encodebytes(signature_b).decode().replace("\n", "")
    log.debug(f"Nanopub signature: {signature}")

    g.add((
        DUMMY_NAMESPACE["sig"],
        NPX["hasSignature"],
        Literal(signature),
        DUMMY_NAMESPACE["pubInfo"],
    ))

    quads = RdfUtils.get_quads(g)
    trusty_artefact = RdfHasher.make_hash(
        quads,
        baseuri=str(DUMMY_NAMESPACE),
        hashstr=" "
    )
    log.debug(f"Trusty artefact: {trusty_artefact}")

    g = replace_trusty_in_graph(trusty_artefact, str(DUMMY_NAMESPACE), g)
    # print("TRUSTY REPLACE IN PYTHON START")
    # print(g.serialize(format="trig"))
    # print("TRUSTY REPLACE IN PYTHON END")
    return g


def replace_trusty_in_graph(trusty_artefact: str, dummy_ns: str, graph: ConjunctiveGraph):
    np_uri = FINAL_NANOPUB_URI + trusty_artefact
    # replace_trusty_in_graph()
    graph.bind("this", Namespace(np_uri))
    graph.bind("sub", Namespace(np_uri + "#"))

    bnodemap: dict = {}
    for s, p, o, c in graph.quads():
        if c:
            g = c.identifier
        else:
            raise Exception("Found a nquads without graph when replacing dummy URIs with trusty URIs. Something went wrong.")
        new_g = URIRef(transform(g, trusty_artefact, dummy_ns, bnodemap))
        new_s = URIRef(transform(s, trusty_artefact, dummy_ns, bnodemap))
        new_p = URIRef(transform(p, trusty_artefact, dummy_ns, bnodemap))
        new_o = o
        if isinstance(o, URIRef) or isinstance(o, BNode):
            new_o = URIRef(transform(o, trusty_artefact, dummy_ns, bnodemap))

        graph.remove((s, p, o, g))
        graph.add((new_s, new_p, new_o, new_g))
        # print(str(new_g))
    return graph



def publish_graph(g: ConjunctiveGraph, use_server: str = NANOPUB_SERVER_LIST[0]) -> bool:
    """Publish a nanopub.

    Publish the signed nanopub to the nanopub server we do a simple POST request.
    """
    # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    headers = {'Content-Type': 'application/trig'}
    data = g.serialize(format="trig")
    r = requests.post(use_server, headers=headers, data=data)
    r.raise_for_status()
    # if r.status_code == 201:
    return True



def verify(g: ConjunctiveGraph, source_uri: str) -> bool:
    # TODO: improve to better test the different components (signature, etc)

    # signature_uri = URIRef(f"{np.source_uri}#sig")
    # for s, p, o in g.triples((signature_uri, NPX.hasSignature, None)):
    #     signature = str(o)
    # g.remove((signature_uri, NPX.hasSignature, None))

    quads = RdfUtils.get_quads(g)
    trusty_artefact = RdfHasher.make_hash(
        quads,
        baseuri=str(DUMMY_NAMESPACE),
        hashstr=" "
    )
    expected_uri = f"http://purl.org/np/{trusty_artefact}"
    if expected_uri != source_uri:
        print(f"The Trusty artefact of the nanopub {source_uri} is not valid. It should be {trusty_artefact}")
        return False
    else:
        return True


# Implement sign/publish in python:
# 1. Use trusty-uri lib to get the trusty URI
# 2. Replace the temp nanopub URIs in the graph by the generated trusty URI
# 3. Add signature in pubInfo (how to generate it?)
# In java SignatureUtils > createSignedNanopub
# 4. Publish to one of the np servers: https://monitor.petapico.org/
# post.setEntity(new StringEntity(nanopubString, "UTF-8"));
# post.setHeader("Content-Type", RDFFormat.TRIG.getDefaultMIMEType());
