# (c) 2019 Kevin Gallagher <kevingallagher@gmail.com>
# (c) 2017 Yannig Perre <yannig.perre(at)gmail.com>
# (c) 2019 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: alt_ini
    author: Kevin Gallagher <kevingallagher@gmail.com>
    version_added: "2.0"
    short_description: read data from a ini file without section headers
    description:
      - "The ini lookup reads the contents of a file in INI format C(key1=value1).
        This plugin retrieve the value on the right side after the equal sign C('=') of a given section C([section])."
    options:
      _terms:
        description: khe key(s) to look up
        required: True
      file:
        description: name of the file to load
        default: ansible.ini
      section:
        default: global
        description: section to look within for the key
      encoding:
        default: utf-8
        description: text encoding to use
      default:
        description: return value if the key is not in the ini file
        default: ''
"""

EXAMPLES = """
- debug: msg="User in integration is {{ lookup('alt_ini', 'user section=integration file=users.ini') }}"

- debug:
    msg: "{{ item }}"
  with_alt_ini:
    - value[1-2]
    - section: section1
    - file: "lookup.ini"
    - re: true
"""

RETURN = """
_raw:
  description:
    - value(s) of the key(s) in the ini file
"""
import os
import re
from configobj import ConfigObj, ConfigObjError
from collections import MutableSequence
from io import StringIO

from ansible.errors import AnsibleError, AnsibleAssertionError
from ansible.module_utils._text import to_bytes, to_text
from ansible.plugins.lookup import LookupBase


def _parse_params(term):
    '''Safely split parameter term to preserve spaces'''

    keys = ['key', 'section', 'file', 'default', 'encoding']
    params = {}
    for k in keys:
        params[k] = ''

    thiskey = 'key'
    for idp, phrase in enumerate(term.split()):
        for k in keys:
            if ('%s=' % k) in phrase:
                thiskey = k
        if idp == 0 or not params[thiskey]:
            params[thiskey] = phrase
        else:
            params[thiskey] += ' ' + phrase

    rparams = [params[x] for x in keys if params[x]]
    return rparams


class LookupModule(LookupBase):

    def get_value(self, key, section, dflt):
        value = None
        try:
            value = self.cp[section][key]
        except ConfigObjError:
            return dflt
        return value

    def run(self, terms, variables=None, **kwargs):

        ret = []
        for term in terms:
            params = _parse_params(term)
            key = params[0]

            paramvals = {
                'file': 'ansible.ini',
                'default': None,
                'section': "global",
                'encoding': 'utf-8'
            }

            # parameters specified?
            try:
                for param in params[1:]:
                    name, value = param.split('=')
                    if name not in paramvals:
                        raise AnsibleAssertionError('%s not in paramvals' % name)
                    paramvals[name] = value
            except (ValueError, AssertionError) as e:
                raise AnsibleError(e)

            try:
                self.cp = ConfigObj(paramvals['file'], encoding=paramvals['encoding'], file_error=True)
            except (ConfigObjError, IOError) as e:
                raise AnsibleError('Could not read "%s": %s' % (paramvals['file'], e))

            # Retrieve file path
            path = self.find_file_in_search_path(variables, 'files', paramvals['file'])

            # Create StringIO later used to parse ini
            config = StringIO()

            # Open file using encoding
            contents, show_data = self._loader._get_file_contents(path)
            contents = to_text(contents, errors='surrogate_or_strict')
            config.write(contents)
            config.seek(0, os.SEEK_SET)
            sec = self.cp[paramvals['section']]
            var = sec[key]
            if var is not None:
                if isinstance(var, MutableSequence):
                    for v in var:
                        ret.append(v)
                else:
                    ret.append(var)
        return ret
