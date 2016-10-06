
Welcome to IDFVersionUpdater's documentation!
=============================================

The purpose of this program is to enable EnergyPlus users to transition up their existing input files to the latest version of EnergyPlus.
This program itself is EnergyPlus-version-agnostic, and currently will transition input files up to the latest version found installed in this machine in the default location.

--------------------------
Packaging and Installation
--------------------------

The program is built by `Travis CI <https://travis-ci.org>`_ and packaged using `py2app <https://pythonhosted.org/py2app/>`_ to create a Mac-compatible program package.
This package can then be *installed* onto the machine by placing it into the ``/Applications`` directory so that it can be launched via Spotlight or other means.

-------------------
Program Main Window
-------------------

Launching the program reveals the following main window:

.. image:: images/mainwindow.png
   :align: center

This main window reveals a lot of information.

* The window title bar shows the program version, as well as the highest detected version of EnergyPlus installed on the system

* The top row of the window includes buttons to allow selection of an input file, and show the ``About...`` dialog with additional information about the program

* The next row has a user-editable file path text entry, and a label showing the entered file version:

  * The text entry is populated when using the file selection dialog, although the user can enter a file path manually as well

  * Whenever a file is selected, the contents of the file is parsed to detect the existing file version and that version is shown on the label

  * The available actions on the window vary based on whether a valid file path is entered in the text box

* The next row allows the user to select whether to keep a copy of the original file in the run directory or allow it to be overwritten during transition

* The next row includes the main action buttons:

  * ``Update`` will run the transition utilities to get the file up to the latest version, running multiple transitions as needed

  * ``Open Run Directory`` opens the run directory to allow inspection of the transition files at any time

  * ``Close`` obviously closes the program

* The status bar shows updates during the program operation, including running each transition and when the whole transition is complete or if there was a failure

----------------
Typical Workflow
----------------

Consider a new version of EnergyPlus is released, version 17.0.  A user has built example files previously that are based on EnergyPlus 16.0.
Instead of manually updating each input file, they will:

* Open this IDFVersionUpdater utility, which is installed with the latest (17.0 in this example) version of EnergyPlus

* Use the ``Choose File`` button to locate an idf from the previous version (16.0 in this example) and select it, verifying that the version label on the form properly reflects the expected version

* Click the ``Update`` button to initiate the transition up to the latest version.  For this example, it would transition from 16 to 17 in one step.  If the original input file was an older version, multiple transition steps would be performed to get to the latest version

* The user would then click the ``Open Run Directory`` button to open a window to the new input file, and copy it to be placed back into the user's desired location to be run with the latest version (17.0 in this example)

-------------------------
Source Code Documentation
-------------------------

Documentation of the source code, pretty much only important for the developers, is available for the following modules.

.. toctree::
   :maxdepth: 2

   EnergyPlusPath
   International
   TransitionBinary
   TransitionRunThread
   VersionUpdaterWindow


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

