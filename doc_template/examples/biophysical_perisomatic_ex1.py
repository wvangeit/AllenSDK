from allensdk.api.queries.biophysical_perisomatic_api import \
    BiophysicalPerisomaticApi

bp = BiophysicalPerisomaticApi('http://api.brain-map.org')
bp.cache_stimulus = True # change to False to not download the large stimulus NWB file
neuronal_model_id = 472451419    # get this from the web site as above
bp.cache_data(neuronal_model_id, working_directory='neuronal_model')
