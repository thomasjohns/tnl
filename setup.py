from setuptools import setup


setup(
    name='tnl',
    version='0.1.0',
    packages=['tnl'],
    package_data={
        'tnl': ['py.typed']
    },
    entry_points={
        'console_scripts': [
            'tnl = tnl.__main__:exec_cli'
        ],
    },
)
