from schema import Schema, Optional, And, Or, Regex, SchemaError
from validator.schema.image_schema import IMAGE_CONTENT_SCHEMA
from validator.schema.rpm_schema import RPM_CONTENT_SCHEMA

GIT_SSH_URL_REGEX = r'((git@[\w\.]+))([\w\.@\:/\-~]+)(\.git)(/)?'

ASSEMBLY_DEPENDENCIES = {
    'rpms': [
        And({
            Regex(r'el\d+'): str,  # Each RHEL version can have its own
            'why': str,  # Human description of why this is being added for historical purposes
            'non_gc_tag': str,  # Artist should provide tag they know will prevent this NVR from garbage collection.
        })
    ]
}

ASSEMBLY_NAME_REGEX = Regex(r'^art\d+$')


def releases_schema(file):
    return Schema({
        'releases': {
            Optional(Or('stream', 'test', ASSEMBLY_NAME_REGEX)): {
                'assembly': {
                    Optional('basis'): {
                        Optional('brew_event'): int,
                        Optional('assembly'): ASSEMBLY_NAME_REGEX,
                    },
                    Optional('rhcos'): {
                        'machine-os-content': {
                            'images': {
                                # pullspecs for arch specific images
                                Optional('x86_64'): str,
                                Optional('s390x'): str,
                                Optional('ppc64le'): str,
                                Optional('arm64'): str,
                            },
                        },
                        Optional('dependencies'): ASSEMBLY_DEPENDENCIES,
                    },
                    Optional('group'): {
                        Optional('arches'): [
                            Or('x86_64', 'ppc64le', 's390x', 'aarch64')
                        ],
                        Optional('repos'): {
                            Regex('[a-z0-9.-]+'): {
                                'conf': {
                                    'baseurl': {
                                        Or('x86_64', 'ppc64le', 's390x', 'aarch64'): str
                                    }
                                }
                            }
                        },
                        Optional('advisories'): {
                            Optional('image'): int,
                            Optional('rpm'): int,
                            Optional('extras'): int,
                            Optional('metadata'): int,
                        },
                        Optional('dependencies'): ASSEMBLY_DEPENDENCIES,
                    },
                    Optional('members'): {
                        Optional('rpms'): [
                            And({
                                'distgit_key': str,
                                'why': str,  # Human description of why this is being added for historical purposes
                                Optional('metadata'): {
                                    Optional('content'): RPM_CONTENT_SCHEMA,
                                    Optional('is'): {
                                        Regex(r'el\d+'): str
                                    }
                                },
                            })
                        ],
                        Optional('images'): [
                            And({
                                'distgit_key': str,
                                'why': str,  # Human description of why this is being added for historical purposes
                                Optional('metadata'): {
                                    Optional('content'): IMAGE_CONTENT_SCHEMA,
                                    Optional('dependencies'): ASSEMBLY_DEPENDENCIES,
                                    Optional('is'): {
                                        'nvr': str
                                    },
                                },
                            })
                        ]
                    },
                    Optional('issues'): {
                        Optional('include'): [
                            And({
                                'id': Or(int, Regex(r'[A-Z]+-\d+'))  # bugzilla or Jira
                            })
                        ],
                        Optional('exclude'): [
                            And({
                                'id': Or(int, Regex(r'[A-Z]+-\d+'))  # bugzilla or Jira
                            })
                        ],
                    },
                },
            }
        }
    })


def validate(file, data):
    try:
        releases_schema(file).validate(data)
    except SchemaError as err:
        return '{}'.format(err)
