//Re-Create vertex with new id. Clone vertex and move edges and delete the vertex.
def reCreateV(g, old_id, new_id) {
    g.V(old_id).as('old_vertex').addV().property(label, select('old_vertex').label()).property(T.id, new_id).as('new_vertex').\
    select('old_vertex').properties().as('old_vertex_properties').select('new_vertex').property(select('old_vertex_properties').key(), select('old_vertex_properties').value())
}