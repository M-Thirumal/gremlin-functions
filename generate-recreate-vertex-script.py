from gremlin_python.driver import client
from gremlin_python.driver import serializer
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

import logging

#Clone vertex from the given old_vertex_id and move edges to newly cloned vertex
def generate_recreate_vertex(old_id, new_id):
    clone_vertex_with_new_id = 'g.V(\'{}\').as(\'old_vertex\').addV().property(label, select(\'old_vertex\').label()).property(T.id, \'{}\').as(\'new_vertex\').select(\'old_vertex\').properties().as(\'old_vertex_properties\').select(\'new_vertex\').property(select(\'old_vertex_properties\').key(), select(\'old_vertex_properties\').value()).iterate();'.format(old_id, new_id)
    edges = g.V(old_id).bothE().elementMap().toList()
    edge_script = ""
    for edge in edges:
        edge_id = edge['id']
        outE = '.from(g.V(\'{}\'))'.format(new_id if edge['OUT']['id'] == old_id else edge['OUT']['id'])
        inE = '.to(g.V(\'{}\'))'.format(new_id if edge['IN']['id'] == old_id else edge['IN']['id'])
        edge_script += 'g.E(\'{}\').drop().iterate();'.format(edge_id)
        edge_script += 'g.addE(\'{}\'){}{}.property(T.id, \'{}\')'.format(edge['label'], inE, outE, edge_id)
        for k, v in edge.items():
            if k not in ['label', 'id', 'IN', 'OUT']:
                edge_script += '.property(\'{}\', \'{}\')'.format(k, v)
        edge_script += ".iterate();"
    #
    vertex_drop = 'g.V(\'{}\').drop()'.format(old_id)
    script = clone_vertex_with_new_id + edge_script + vertex_drop
    return script

    
def submit_script(script):
    print("---------SCRIPT---------------")
    print(script)
    result_set = cli().submit(script, {'evaluationTimeout': 50000})
    future_results = result_set.all()
    results = future_results.result()
    return results

def cli():
    return client.Client(connection_string(), 'g');

def create_remote_connection():
    return DriverRemoteConnection(
        connection_string(),
        'g',
        pool_size=1,
        message_serializer=serializer.GraphSONSerializersV2d0()
    )

def connection_string():
    database_url = 'wss://{}:{}/gremlin'.format("localhost", "8080")
    return database_url

def create_graph_traversal_source(conn):
    return traversal().withRemote(conn)

conn = create_remote_connection()
g = create_graph_traversal_source(conn)

generate_recreate_vertex("1", "21")