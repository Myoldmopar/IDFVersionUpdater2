from setuptools import setup

# check incoming command line arg for build type
import sys
if not len(sys.argv) == 2:
    print("Bad argument to setup.py")
    sys.exit(1)
type_mac = -1
type_nix = -2
# type_win = -3
platform = 0
if sys.argv[1] == 'py2app':
    platform = type_mac
elif sys.argv[1] == 'py2deb':
    platform = type_nix
# elif sys.argv[1] == 'py2exe':
#     platform = type_win
else:
    print("Bad argument to setup.py")
    sys.exit(1)

# set up common things
APP = ['IDFVersionUpdater.py']

# then setup specific things
if platform == type_mac:
    OPTIONS = {'argv_emulation': True,
               'includes': ['wx', 'subprocess'],
               'iconfile': 'resources/ep-logo-3d-transparent.icns'}
    setup(
        name='IDFVersionUpdater',
        description='A wxPython-based tool for transition EnergyPlus input files',
        url='https://github.com/myoldmopar/idfversionupdater2',
        author='Edwin Lee via NREL via United States Department of Energy',
        app=APP,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
        version="2.0.0",
    )
elif platform == type_nix:
    setup(
        name='IDFVersionUpdater',
        description='A wxPython-based tool for transition EnergyPlus input files',
        url='https://github.com/myoldmopar/idfversionupdater2',
        author='Edwin Lee via NREL via United States Department of Energy',
        app=APP,
        setup_requires=['py2deb'],
        version="2.0.0",
    )
# elif platform == type_win:
#     setup(
#         app=APP,
#         setup_requires=['py2exe'],
#         version="2.0.0",
#     )

# TODO: Fix cross platform support

