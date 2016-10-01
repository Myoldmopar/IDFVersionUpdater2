from setuptools import setup

# set up common things
APP = ['IDFVersionUpdater.py']

# then setup specific things
py2app_options = {'argv_emulation': True,
                  'includes': ['wx', 'subprocess'],
                  'iconfile': 'resources/ep-logo-3d-transparent.icns'}
setup(
    name='idfversionupdater',
    description='A wxPython-based tool for transition EnergyPlus input files',
    url='https://github.com/myoldmopar/idfversionupdater2',
    author='Edwin Lee via NREL via United States Department of Energy',
    app=APP,
    options={'py2app': py2app_options},
    version="2.0.0",
)

# TODO: Fix cross platform support

