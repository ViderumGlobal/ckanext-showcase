import ckan.lib.helpers as h
from ckan.plugins import toolkit as tk

DATASET_TYPE_NAME = 'showcase'


def facet_remove_field(key, value=None, replace=None):
    '''
    A custom remove field function to be used by the Showcase search page to
    render the remove link for the tag pills.
    '''
    return h.remove_url_param(
        key, value=value, replace=replace,
        controller='ckanext.showcase.controller:ShowcaseController',
        action='search')


def get_site_statistics():
    '''
    Custom stats helper, so we can get the correct number of packages, and a
    count of showcases.
    '''

    stats = {}
    stats['showcase_count'] = tk.get_action('package_search')(
        {}, {"rows": 1, 'fq': 'dataset_type:showcase'})['count']
    stats['dataset_count'] = tk.get_action('package_search')(
        {}, {"rows": 1, 'fq': '!dataset_type:showcase'})['count']
    stats['group_count'] = len(tk.get_action('group_list')({}, {}))
    stats['organization_count'] = len(
        tk.get_action('organization_list')({}, {}))

    return stats


def get_recent_showcases(limit=3):
    showcases = tk.get_action('ckanext_showcase_list')({}, {})
    showcases_list = []
    for showcase in showcases:
        showcases_list.append(_add_to_pkg_dict({}, {}, showcase))
    showcases_list.sort(key=lambda item: item['metadata_created'], reverse=True)
    return showcases_list[:limit]


def _add_to_pkg_dict(self, context, pkg_dict):
    '''
    Add key/values to pkg_dict and return it.
    '''

    if pkg_dict['type'] != 'showcase':
        return pkg_dict
    # Add a display url for the Showcase image to the pkg dict so template
    # has access to it.
    extras = pkg_dict.get('extras')
    image_url = extras[0].get('value')
    pkg_dict[u'image_display_url'] = image_url
    if image_url and not image_url.startswith('http'):
        pkg_dict[u'image_url'] = image_url
        pkg_dict[u'image_display_url'] = \
            h.url_for_static('uploads/{0}/{1}'
                             .format(DATASET_TYPE_NAME,
                                     pkg_dict.get('image_url')),
                             qualified=True)
    return pkg_dict
