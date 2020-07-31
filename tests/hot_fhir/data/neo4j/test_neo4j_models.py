from hot_fhir.data.neo4j import Neo4jModels
import configparser
import pytest


@pytest.fixture(scope='session')
def config():
    cfg = configparser.ConfigParser()
    cfg.read('test_config.ini')
    return cfg['neo4j']


@pytest.fixture(scope='session')
def neo4j(config):
    neo4j = Neo4jModels(config['uri'], config['user'], config['password'])
    yield neo4j
    neo4j.close()


def test_terminology_service(neo4j: Neo4jModels):
    data = {
        'identifier': '_bioportal',
        'name': '_BioPortal',
        'url': 'http://bioportal.bioontology.org/',
        'type': 'ontology',
        'rest_endpoint': 'https://data.bioontology.org',
        'sparql_endpoint': 'http://sparql.bioontology.org',
        'description': 'A short description',
        'storage': 'triple store',
        'publisher': 'National Center for Biomedical Ontology (NCBO)'
    }
    with neo4j.driver.session() as session:
        session.write_transaction(neo4j.create_terminology_service, data)
        ts = session.read_transaction(neo4j.match_by_name, '_BioPortal', 'TerminologyService')
        assert len(ts) == 1
        session.write_transaction(neo4j.delete_by_identifier, '_bioportal', 'TerminologyService')
        ts = session.read_transaction(neo4j.match_by_name, 'BioPortal', 'TerminologyService')
        assert len(ts) == 0


def test_create_terminology_service(neo4j: Neo4jModels):
    data = {
        'identifier': '_test_id',
        'name': '_test'
    }
    with neo4j.driver.session() as session:
        session.write_transaction(neo4j.create_terminology_service, data)
        ts = session.read_transaction(neo4j.match_by_name, '_test', 'TerminologyService')
        assert len(ts) == 1
        assert len(ts[0]['n'].keys()) == 2

        session.write_transaction(neo4j.delete_by_identifier, '_test_id', 'TerminologyService')
        ts = session.read_transaction(neo4j.match_by_name, '_test', 'TerminologyService')
        assert len(ts) == 0


def test_create_naming_service(neo4j: Neo4jModels):
    data = {
        'identifier': '_ncit',
        'name': '_NCI Thesaurus',
        'publisher': 'National Cancer Institute (NCI)',
        'kind': 'codesystem',
    }
    with neo4j.driver.session() as session:
        session.write_transaction(neo4j.create_naming_system, data)
        ts = session.read_transaction(neo4j.match_by_name, '_NCI Thesaurus', 'NamingSystem')
        assert len(ts) == 1

        session.write_transaction(neo4j.delete_by_identifier, '_ncit', 'NamingSystem')
        ts = session.read_transaction(neo4j.match_by_name, '_NCI Thesaurus', 'NamingSystem')
        assert len(ts) == 0


def test_match_by_id(neo4j: Neo4jModels):
    data = {
        'identifier': '_ncit',
        'name': '_NCI Thesaurus',
        'publisher': 'National Cancer Institute (NCI)',
        'kind': 'codesystem',
    }
    with neo4j.driver.session() as session:
        session.write_transaction(neo4j.create_naming_system, data)
        n = session.read_transaction(neo4j.match_by_identifier, '_ncit', 'NamingSystem')
        assert n is not None
        assert 'publisher' in n.keys()
        assert 'preferred_prefix' not in n.keys()
        assert n.get('identifier') == '_ncit'
        print(n)

        session.write_transaction(neo4j.delete_by_identifier, '_ncit', 'NamingSystem')
        n = session.read_transaction(neo4j.match_by_identifier, '_ncit', 'NamingSystem')
        assert n is None