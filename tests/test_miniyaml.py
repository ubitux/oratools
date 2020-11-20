from oratools import miniyaml

def test():
    d = miniyaml.load(b'''
A:
\tfoo: bar
\tB:
\t\tC:
\t\t\tD:
\t\t\tbla: xxx
\tE:
\t\tZ: yes
''')
    assert d == {
        'A': {
            'foo': 'bar',
            'B': {
                'C': {
                    'D': '',
                    'bla': 'xxx',
                }
            },
            'E': {
                'Z': 'yes',
            }
        }
    }
