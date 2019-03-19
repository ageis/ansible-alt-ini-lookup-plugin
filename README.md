alt_ini
=======

A customized version/fork of the [INI file lookup plugin](https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/lookup/ini.py) in Ansible core.

It uses [ConfigObj](https://configobj.readthedocs.io/en/latest/index.html) rather
than [ConfigParser](https://docs.python.org/3/library/configparser.html), so you can retrieve values from INI files that lack section
headers which are otherwise expected, avoiding the following error:

    configparser.MissingSectionHeaderError: File contains no section headers.

Options
-------

Similar to the plugin in core. The format expected by alt_ini is `key_name section=optional_section_name file=path_to_ini_file` with the encoding and a default value as further unrequired options. 

Setup
------

Set `lookup_plugins` in ansible.cfg to a path containing alt_ini.py. 

Example Usage
-------------

Suppose that the INI file we're reading from looks like this:

```
# renew_before_expiry = 30 days
version = 0.32.0
archive_dir = /etc/letsencrypt/archive/example.com
cert = /etc/letsencrypt/live/example.com/cert.pem
privkey = /etc/letsencrypt/live/example.com/privkey.pem
chain = /etc/letsencrypt/live/example.com/chain.pem
fullchain = /etc/letsencrypt/live/example.comfullchain.pem

# Options used in the renewal process
[renewalparams]
account = cd1e311184737cf7e86581f08c9346c7
rsa_key_size = 4096
authenticator = standalone
server = https://acme-v02.api.letsencrypt.org/directory
post_hook = systemctl start nginx
pre_hook = systemctl stop nginx
```

As you can see above, there's no [global] or initial section header; the file begins with key/value(s). Attempting to read from this using the ordinary INI lookup would fail.

Here's an example of how to use ours in a task:

    - name: Find all post-hooks in certbot renewal config for example.com.
      set_fact:
        post_hooks: "{{ lookup('alt_ini', 'post_hook section=renewalparams file=/etc/letsencrypt/renewal/example.com.conf') }}"

License
-------

BSD

Author Information
------------------

Kevin Gallagher ([@ageis](https://twitter.com/ageis)) 

[cointel.pro](https://cointel.pro)
