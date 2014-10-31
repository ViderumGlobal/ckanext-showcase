import ckan.model as model
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.logic as logic
from ckan.common import c, request, _
from ckan.controllers.package import PackageController
from ckan.controllers.home import CACHE_PARAMETERS
import ckan.lib.render

render = base.render
abort = base.abort
check_access = logic.check_access
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params

NotAuthorized = logic.NotAuthorized

from ckanext.showcase.plugin import DATASET_TYPE_NAME

import logging
log = logging.getLogger(__name__)


class ShowcaseController(PackageController):

    def new(self, data=None, errors=None, error_summary=None):
        package_type = DATASET_TYPE_NAME

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'save': 'save' in request.params}

        # Package needs to have a organization group in the call to
        # check_access and also to save it
        try:
            check_access('ckanext_showcase_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a package'))

        if context['save'] and not data:
            return self._save_new(context, package_type=package_type)

        data = data or clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(
            request.params, ignore_keys=CACHE_PARAMETERS))))
        c.resources_json = h.json.dumps(data.get('resources', []))
        # convert tags if not supplied in data
        if data and not data.get('tag_string'):
            data['tag_string'] = ', '.join(
                h.dict_list_reduce(data.get('tags', {}), 'name'))

        errors = errors or {}
        error_summary = error_summary or {}
        # in the phased add dataset we need to know that
        # we have already completed stage 1
        stage = ['active']
        if data.get('state', '').startswith('draft'):
            stage = ['active', 'complete']

        form_snippet = self._package_form(package_type=package_type)
        form_vars = {'data': data, 'errors': errors,
                     'error_summary': error_summary,
                     'action': 'new', 'stage': stage,
                     'dataset_type': package_type}
        c.errors_json = h.json.dumps(errors)

        self._setup_template_variables(context, {},
                                       package_type=package_type)

        new_template = self._new_template(package_type)
        c.form = ckan.lib.render.deprecated_lazy_render(
            new_template,
            form_snippet,
            lambda: render(form_snippet, extra_vars=form_vars),
            'use of c.form is deprecated. please see '
            'ckan/templates/package/base_form_page.html for an example '
            'of the new way to include the form snippet'
            )
        return render(new_template,
                      extra_vars={'form_vars': form_vars,
                                  'form_snippet': form_snippet,
                                  'dataset_type': package_type})
