# Copyright 2015 Allen Institute for Brain Science
# This file is part of Allen SDK.
#
# Allen SDK is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Allen SDK is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Allen SDK.  If not, see <http://www.gnu.org/licenses/>.

from allensdk.api.queries.rma_template import RmaTemplate

class OntologiesApi(RmaTemplate):
    '''
    See: `Atlas Drawings and Ontologies
    <http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies>`_
    '''
    
    rma_templates = \
        {"ontology_queries": [
            {'name': 'structures_by_graph_ids',
             'description': 'see name',
             'model': 'Structure',
             'criteria': '[graph_id$in{{ graph_ids }}]',
             'order': ['structures.graph_order'],
             'num_rows': 'all',
             'count': False,
             'criteria_params': ['graph_ids']
            },
            {'name': 'structures_by_graph_names',
             'description': 'see name',
             'model': 'Structure',
             'criteria': 'graph[structure_graphs.name$in{{ graph_names }}]',
             'order': ['structures.graph_order'],
             'num_rows': 'all',
             'count': False,
             'criteria_params': ['graph_names']
            },
            {'name': 'structures_by_set_ids',
             'description': 'see name',
             'model': 'Structure',
             'criteria': '[structure_set_id$in{{ set_ids }}]',
             'order': ['structures.graph_order'],
             'num_rows': 'all',
             'count': False,
             'criteria_params': ['set_ids']
            },
            {'name': 'structures_by_set_names',
             'description': 'see name',
             'model': 'Structure',
             'criteria': 'structure_sets[name$in\'{{ set_names }}\']',
             'order': ['structures.graph_order'],
             'num_rows': 'all',
             'count': False,
             'criteria_params': ['set_names']
            },
            {'name': 'structure_graphs_list',
             'description': 'see name',
             'model': 'StructureGraph',
             'num_rows': 'all',
             'count': False
            },
            {'name': 'structure_sets_list',
             'description': 'see name',
             'model': 'StructureSet',
             'num_rows': 'all',
             'count': False
            },
            {'name': 'atlases_list',
             'description': 'see name',
             'model': 'Atlas',
             'num_rows': 'all',
             'count': False
            },
            {'name': 'atlases_table',
             'description': 'see name',
             'model': 'Atlas',
             'criteria': '{% if atlas_ids is defined %}[id$in{{ atlas_ids }}],{%endif%}structure_graph(ontology),graphic_group_labels',
             'include': 'structure_graph(ontology),graphic_group_labels',
             'only': ['atlases.id',
                      'atlases.name',
                      'atlases.image_type',
                      'ontologies.id',
                      'ontologies.name',
                      'structure_graphs.id',
                      'structure_graphs.name',
                      'graphic_group_labels.id',
                      'graphic_group_labels.name'],
             'num_rows': 'all',
             'count': False,
             'criteria_params': ['atlas_ids']
            }
        ]}
    
    
    def __init__(self, base_uri=None):
        super(OntologiesApi, self).__init__(base_uri,
                                            query_manifest=OntologiesApi.rma_templates)
    
    
    def get_structures(self,
                       structure_graph_ids=None,
                       structure_graph_names=None,
                       structure_set_ids=None,
                       structure_set_names=None,
                       order = ['structures.graph_order'],
                       num_rows='all',
                       count=False):
        '''Retrieve data about anatomical structures.
        
        Parameters
        ----------
        structure_graph_ids : int or list of ints, optional
            database keys to get all structures in particular graphs
        structure_graph_names : string or list of strings, optional
            list of graph names to narrow the query
        structure_set_ids : int or list of ints, optional
            database keys to get all structures in a particular set
        structure_set_names : string or list of strings, optional
            list of set names to narrow the query.
        order : list of strings
            list of RMA order clauses for sorting
        num_rows : int
            how many records to retrieve
            
        Returns
        -------
        dict
            the parsed json response containing data from the API
            
        Notes
        -----
        Only one of the methods of limiting the query should be used at a time.
        '''
        if structure_graph_ids != None:
            data = self.template_query('ontology_queries',
                                       'structures_by_graph_ids',
                                       graph_ids=structure_graph_ids,
                                       order=order,
                                       num_rows=num_rows,
                                       count=count)
        elif structure_graph_names != None:
            data = self.template_query('ontology_queries',
                                       'structures_by_graph_names',
                                       graph_names=structure_graph_names,
                                       order=order,
                                       num_rows=num_rows,
                                       count=count)
        elif structure_set_ids != None:
            data = self.template_query('ontology_queries',
                                       'structures_by_set_ids',
                                       set_ids=structure_set_ids,
                                       order=order,
                                       num_rows=num_rows,
                                       count=count)
        elif structure_set_names != None:
            data = self.template_query('ontology_queries',
                                       'structures_by_set_names',
                                       set_names=structure_set_names,
                                       order=order,
                                       num_rows=num_rows,
                                       count=count)
        
        return data
    
    
    def unpack_structure_set_ancestors(self, structure_dataframe):
        '''Convert a slash-separated structure_id_path field to a list.
        
        Parameters
        ----------
        structure_dataframe : DataFrame
            structure data from the API
        
        Returns
        -------
        None
            A new column is added to the dataframe containing the ancestor list.
        '''
        ancestors = structure_dataframe['structure_id_path'].apply(
            lambda e: [int(a) for a in e.split('/')[1:-1]])
        structure_ancestors = [
            [n for n in ancestors_n] for ancestors_n in ancestors
        ]
        structure_dataframe['structure_set_ancestor'] = structure_ancestors


    def get_atlases_table(self, atlas_ids=None, brief=True):
        '''List Atlases available through the API
        with associated ontologies and structure graphs.
        
        Parameters
        ----------
        atlas_ids : integer or list of integers, optional
            only select specific atlases
        brief : boolean, optional
            True (default) requests only name and id fields.
        
        Returns
        -------
        dict : atlas metadata
        
        Notes
        -----
        This query is based on the
        `table of available Atlases <http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies>`_.
        See also: `Class: Atlas <http://api.brain-map.org/doc/Atlas.html>`_
        '''
        if brief == True:
            data = self.template_query('ontology_queries',
                                       'atlases_table',
                                       atlas_ids=atlas_ids)
        else:
            data = self.template_query('ontology_queries',
                                       'atlases_table',
                                       atlas_ids=atlas_ids,
                                       only=None)
        
        return data
    
    
    def get_atlases(self):
        return self.template_query('ontology_queries',
                                   'atlases_list')
    
    
    def get_structure_graphs(self):
        return self.template_query('ontology_queries',
                                   'structure_graphs_list')
        
    def get_structure_sets(self):
        return self.template_query('ontology_queries',
                                   'structure_sets_list')
