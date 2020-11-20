from setuptools import find_packages, setup

setup(
    name='oratools',
    version='0.1',
    packages=find_packages(),
    zip_safe=False,
    entry_points=dict(
        console_scripts=[
            'ora-trace = oratools.trace:run',
            'ora-buildorder = oratools.buildorder:run',
            'ora-chat = oratools.chat:run',
        ],
    ),
)
