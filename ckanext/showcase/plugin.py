import logging

import ckan.plugins as plugins
import ckan.lib.plugins as lib_plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import OrderedDict, _

from routes.mapper import SubMapper

import ckanext.showcase.logic.auth

log = logging.getLogger(__name__)

DATASET_TYPE_NAME = 'showcase'


class ShowcasePlugin(plugins.SingletonPlugin, lib_plugins.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IAuthFunctions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        # toolkit.add_public_directory(config_, 'public')
        # toolkit.add_resource('fanstatic', 'showcase')

    # IDatasetForm

    def package_types(self):
        return [DATASET_TYPE_NAME]

    def is_fallback(self):
        return False

    def search_template(self):
        return 'showcase/search.html'

    def read_template(self):
        return 'showcase/read.html'

    # IFacets

    def dataset_facets(self, facets_dict, package_type):
        if package_type != DATASET_TYPE_NAME:
            return facets_dict
        return OrderedDict({'tags': _('Tags')})

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'ckanext_showcase_create': ckanext.showcase.logic.auth.create
        }

    # IRoutes

    def before_map(self, map):
        # These named routes are used for custom dataset forms which will use the
        # names below based on the dataset.type ('dataset' is the default type)
        with SubMapper(map, controller='ckanext.showcase.controller:ShowcaseController') as m:
            m.connect('showcase_index', '/showcase', action='search',
                      highlight_actions='index search')
            m.connect('add showcase', '/showcase/new', action='new')
            m.connect('showcase_read', '/showcase/{id}', action='read',
                      ckan_icon='sitemap')

        map.redirect('/showcases', '/showcase')
        map.redirect('/showcases/{url:.*}', '/showcase/{url}')
        return map
