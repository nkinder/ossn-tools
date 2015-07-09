def _parse_section(text, section, unwrap=True):
    """Extract the content of a section

    Args:
      text: the text version of the security note
      section: the section name to extract
      unwrap: defines if we should remove line-wrapping
    Returns:
      a list of paragraphs within the section
    """
    # Find the start of the section.
    section_header = ('### %s ###' % section.lower())
    start = text.lower().find(section_header) + len(section_header)

    # Find the end of the section
    end = text.find('\n### ', start)
    if end == -1:
        end = len(text)

    # Split section into paragraphs and strip line-wrapping if requested
    paragraphs = []
    for p in text[start:end].split('\n\n'):
        # NGK(TODO) a regex would be better
        if unwrap and not p.startswith('  --- begin'):
            paragraphs.append(p.strip('\r\n').replace('\n', ' '))
        else:
            paragraphs.append(p.strip('\r\n'))

    return paragraphs


def _parse_affected(text):
    """Extract the affected releases, services, and other software

    Args:
      text: the text version of the security note
    Returns:
      a list of the affected releases
    """
    valid_releases = ['austin', 'bexar', 'cactus', 'diablo', 'essex',
                      'folsom', 'grizzly', 'havana', 'icehouse', 'juno',
                      'kilo', 'liberty']

    valid_services = ['barbican', 'ceilometer', 'cinder', 'designate',
                      'glance', 'heat', 'horizon', 'ironic', 'keystone',
                      'manila', 'neutron', 'nova', 'sahara', 'swift',
                      'trove', 'zaqar']

    # Extract the affected section
    section = _parse_section(text, "Affected Services / Software")

    # Split the values up into separate lists of releases, services,
    # and other software.
    releases = []
    services = []
    other = []
    for val in [v.strip() for v in section[0].split(',')]:
        if val.lower() in valid_releases:
            releases.append(val)
        elif val.lower() in valid_services:
            services.append(val)
        else:
            other.append(val)

    # NGK(TODO) What about other free form text?  Can we assume the first line
    # is csv?  Maybe detect CSV and make an affected text from the non-CSV
    # content?

    return {'releases': releases,
            'services': services,
            'other': other}


def _parse_references(text):
    """Extract the references

    Args:
      text: the text version of the security note
    Returns:
      a list of tuples for each reference (title, reference)
    """
    # Extract the references section
    section = _parse_section(text, "Contacts / References", unwrap=False)

    references = []
    combine_line = False
    for line in [l.strip() for l in section[0].split('\n')]:
        # Check for references that have been split across two lines
        if combine_line:
            combine_line = False
            references.append((first_line, line.strip()))
        elif line.endswith(':'):
            first_line = line.rstrip(':').strip()
            combine_line = True
        else:
            references.append(tuple([v.strip() for v in line.split(':', 1)]))

    return references


class SecurityNote:
    """A representation of a Security Note"""

    def __init__(self):
        self.title = ''
        self.summary = []
        self.affected = {}
        self.discussion = []
        self.recommendations = []
        self.references = []

    def load_from_text(self, text):
        # Parse title
        end_loc = text.find('---')
        self.title = text[:end_loc].strip()

        # Parse affected releases, services, and other software
        self.affected = _parse_affected(text)

        # Parse summary
        self.summary = _parse_section(text, 'Summary')

        # Parse discussion
        self.discussion = _parse_section(text, 'Discussion')

        # Parse recommendations
        self.recommendations = _parse_section(text, 'Recommended Actions')

        # Parse references
        self.references = _parse_references(text)

    def load_from_yaml(self, yaml):
        # NGK(TODO) Needs to be implemented, though it is unclear if there
        # is value in having OSSNs formatted in YAML in the first place.
        return

    def to_yaml(self):
        yaml = 'title: %s\n' % self.title
        yaml += 'summary:\n'
        for p in self.summary:
            # NGK - need line wrapping
            yaml += '  - %s\n' % p
        yaml += 'affected releases:\n'
        for release in self.affected['releases']:
            yaml += '  - %s\n' % release
        yaml += 'affected services:\n'
        for service in self.affected['services']:
            yaml += '  - %s\n' % service
        yaml += 'affected other:\n'
        for other in self.affected['other']:
            yaml += '  - %s\n' % other
        yaml += 'discussion:\n'
        for p in self.discussion:
            # NGK(TODO) Needs line wrapping.  Config examples are a mess.
            yaml += '  - %s\n' % p
        yaml += 'recommendations:\n'
        for p in self.recommendations:
            # NGK(TODO) Needs line wrapping.
            yaml += '  - %s\n' % p
        yaml += 'references:\n'
        for ref in self.references:
            yaml += '  - %s: %s\n' % (ref[0], ref[1])

        return yaml.rstrip()

    def to_text(self):
        # NGK(TODO) Needs to be implemented.  Return text for OSSN, wrap at e-mail
        # width.
        return 'NOT IMPLEMENTED'

    def __repr__(self):
        return (('---title---\n%s\n' % self.title) +
                ('---summary---\n%s\n' % self.summary) +
                ('---affected_releases---\n%s\n' % self.affected['releases']) +
                ('---affected_services---\n%s\n' % self.affected['services']) +
                ('---affected_other---\n%s\n' % self.affected['other']) +
                ('---discussion---\n%s\n' % self.discussion) +
                ('---recommendations---\n%s\n' % self.recommendations) +
                ('---references---\n%s' % self.references))
