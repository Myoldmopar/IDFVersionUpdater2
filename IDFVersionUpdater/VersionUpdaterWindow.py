import os
import subprocess

import wx

from .EnergyPlusPath import EnergyPlusPath
from .TransitionRunThread import TransitionRunThread
from .International import translate as _, Languages, set_language
from .Settings import Keys, load_settings, save_settings

__program_name__ = "IDFVersionUpdater (v2.0)"

_doing_restart = False


def doing_restart():
    """
    This function exposes the private, global, variable to determine if the program is going through an automated restart
    :return: True if the program should be restarted after reloaded settings, or False to just let the program be done
    """
    return _doing_restart


class VersionUpdaterWindow(wx.Frame):
    """ The main window, or wx.Frame, for the IDFVersionUpdater program.
    This initializer function creates instance variables, sets up threading, and builds the GUI"""

    def __init__(self):

        # initialize base class
        wx.Frame.__init__(self, None, title=__program_name__, size=(600, 183))
        self.SetMinSize((400, 175))

        # load the settings here very early; the tilde is cross platform thanks to Python
        self.settings_file_name = os.path.join(os.path.expanduser("~"), ".idfversionupdater.json")
        self.settings = load_settings(self.settings_file_name)

        # initialize some class-level "constants"
        self.box_spacing = 4

        # reset the restart flag
        global _doing_restart
        _doing_restart = False

        # initialize instance variables to be set later
        self.btn_select_idf = None
        self.btn_about = None
        self.lbl_path = None
        self.lbl_old_version = None
        self.chk_create_inter_versions = None
        self.btn_update_file = None
        self.btn_open_run_dir = None
        self.btn_cancel = None
        self.btn_exit = None
        self.status_bar = None
        self.idf_version = None
        self.running_transition_thread = None

        # try to load the settings very early since it includes initialization
        set_language(self.settings[Keys.language])

        # connect signals for the GUI
        self.Bind(wx.EVT_CLOSE, self.on_closing_form)

        # build up the GUI itself
        self.build_gui()

        # update the list of E+ versions
        self.ep_run_folder = EnergyPlusPath()
        title = TransitionRunThread.get_ep_version(
            os.path.join(self.ep_run_folder.installation_path, 'energyplus'))
        self.SetTitle(__program_name__ + " -- " + title.decode('utf-8'))
        self.status_bar.SetStatusText(_("Program Initialized"))

        # check the validity of the idf versions once at load time to initialize the action availability
        self.on_update_for_new_file(None)

    # GUI Worker Functions

    def build_gui(self):
        """
        This function manages the window construction, including position, title, and presentation
        """
        self.status_bar = self.CreateStatusBar()  # A StatusBar in the bottom of the window

        # highest level layout control is the main panel
        panel = wx.Panel(self, wx.ID_ANY)

        # this is then broken into rows with one vertical sizer
        top_sizer = wx.BoxSizer(wx.VERTICAL)

        # each row then has their own horizontal sizers on which controls are placed
        choose_about_sizer = wx.BoxSizer(wx.HORIZONTAL)
        path_version_sizer = wx.BoxSizer(wx.HORIZONTAL)
        checkbox_sizer = wx.BoxSizer(wx.HORIZONTAL)
        update_audit_close_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # let's create a bunch of controls
        self.btn_select_idf = wx.Button(panel, wx.ID_ANY, _('Choose File to Update...'))
        self.btn_select_idf.Bind(wx.EVT_BUTTON, self.on_choose_idf)
        self.btn_about = wx.Button(panel, wx.ID_ANY, _('About...'))
        self.btn_about.Bind(wx.EVT_BUTTON, self.on_about)
        self.lbl_path = wx.TextCtrl(panel, wx.ID_ANY, _('File Path'), style=wx.BORDER_NONE)
        self.lbl_path.Bind(wx.EVT_TEXT, self.on_update_for_new_file)
        if self.settings[Keys.last_idf] is not None:
            self.lbl_path.SetValue(self.settings[Keys.last_idf])
        self.lbl_old_version = wx.StaticText(panel, wx.ID_ANY, _('Old Version'))
        self.chk_create_inter_versions = wx.CheckBox(panel, wx.ID_ANY, _('Keep Intermediate Versions of Files?'))
        self.chk_create_inter_versions.SetValue(True)
        self.btn_update_file = wx.Button(panel, wx.ID_ANY, _('Update File'))
        self.btn_update_file.Bind(wx.EVT_BUTTON, self.on_update_idf)
        self.btn_cancel = wx.Button(panel, wx.ID_ANY, _('Cancel Run'))
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.btn_cancel.Disable()
        self.btn_open_run_dir = wx.Button(panel, wx.ID_ANY, _('Open Run Directory'))
        self.btn_open_run_dir.Bind(wx.EVT_BUTTON, self.on_open_run_dir)
        self.btn_exit = wx.Button(panel, wx.ID_ANY, _('Close'))
        self.btn_exit.Bind(wx.EVT_BUTTON, self.on_close)

        # now let's add the controls to each sizer
        choose_about_sizer.Add(self.btn_select_idf, 1, flag=wx.ALIGN_LEFT | wx.LEFT, border=self.box_spacing)
        choose_about_sizer.Add(wx.StaticText(panel, -1, ''), 100, wx.EXPAND, border=self.box_spacing)
        choose_about_sizer.Add(self.btn_about, 1, flag=wx.RIGHT, border=self.box_spacing)
        path_version_sizer.Add(self.lbl_path, 4, flag=wx.ALIGN_LEFT | wx.LEFT, border=self.box_spacing)
        path_version_sizer.Add(wx.StaticText(panel, -1, ''), 1, wx.EXPAND, border=self.box_spacing)
        path_version_sizer.Add(self.lbl_old_version, 1, flag=wx.RIGHT, border=self.box_spacing)
        checkbox_sizer.Add(self.chk_create_inter_versions, 1, flag=wx.ALIGN_LEFT | wx.LEFT, border=self.box_spacing)
        update_audit_close_sizer.Add(self.btn_update_file, 1, flag=wx.ALIGN_LEFT | wx.LEFT, border=self.box_spacing)
        update_audit_close_sizer.Add(self.btn_cancel, 1, flag=wx.ALIGN_LEFT | wx.LEFT, border=self.box_spacing)
        update_audit_close_sizer.Add(wx.StaticText(panel, -1, ''), 7, wx.EXPAND, border=self.box_spacing)
        update_audit_close_sizer.Add(self.btn_open_run_dir, 1, flag=wx.RIGHT, border=self.box_spacing)
        update_audit_close_sizer.Add(self.btn_exit, 1, flag=wx.RIGHT, border=self.box_spacing)

        # then we'll add all the horizontal sizers into the main vertical sizer
        top_sizer.Add(choose_about_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=self.box_spacing)
        top_sizer.Add(wx.StaticLine(panel, ), proportion=0, flag=wx.EXPAND | wx.ALL, border=self.box_spacing)
        top_sizer.Add(path_version_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=self.box_spacing)
        top_sizer.Add(wx.StaticLine(panel, ), proportion=0, flag=wx.EXPAND | wx.ALL, border=self.box_spacing)
        top_sizer.Add(checkbox_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=self.box_spacing)
        top_sizer.Add(wx.StaticLine(panel, ), proportion=0, flag=wx.EXPAND | wx.ALL, border=self.box_spacing)
        top_sizer.Add(update_audit_close_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=self.box_spacing)

        # and now tell the panel we are using this topSizer
        panel.SetSizer(top_sizer)

        # also build out the menu bar
        menu_bar = wx.MenuBar()
        menu1 = wx.Menu()
        # create the actual actionable items under the language menu
        menu1.Append(Languages.English, "English", "Change language to English")
        self.Bind(wx.EVT_MENU, self.on_switch_language, id=Languages.English)
        menu1.Append(Languages.Spanish, "Spanish", "Change language to Spanish")
        self.Bind(wx.EVT_MENU, self.on_switch_language, id=Languages.Spanish)
        menu1.Append(Languages.French, "French", "Change language to French")
        self.Bind(wx.EVT_MENU, self.on_switch_language, id=Languages.French)
        menu1.AppendSeparator()
        menu1.Append(106, "&Close\tCtrl+W", "Closes the window")
        self.Bind(wx.EVT_MENU, self.on_close, id=106)
        menu_bar.Append(menu1, "&File")
        self.SetMenuBar(menu_bar)  # Adding the MenuBar to the Frame content.

        # finally show the window in the center of the (primary? current?) screen
        self.Show(True)
        self.CenterOnScreen()

    def set_buttons_for_running(self, enabled):
        """
        This function sets the state of different buttons on the main window while a background task is running
        The list of controls to be enabled/disabled is hardcoded in an array in this function
        :param enabled: True if the controls are to be enabled, for example when the process is complete, False to disable.
        :return:
        """
        buttons = [self.btn_update_file, self.btn_select_idf, self.btn_exit]
        if enabled:
            [x.Enable() for x in buttons]
        else:
            [x.Disable() for x in buttons]
        buttons_to_invert = [self.btn_cancel]
        if enabled:
            [x.Disable() for x in buttons_to_invert]
        else:
            [x.Enable() for x in buttons_to_invert]

    # Event Handlers

    def on_switch_language(self, event):
        """
        This function handles the request to change languages, where the language identifier is passed in with the event
        :param event: The event information generated by the caller, for this function, the event ID should be set to
        an item in the :py:class:`Languages <International.Languages>` enumeration class
        """
        global _doing_restart
        this_id = event.GetId()
        language = this_id
        self.settings[Keys.language] = language
        message = wx.MessageDialog(
            parent=self,
            message=_(
                "You must restart the app to make the language change take effect.  Would you like to restart now?"),
            caption=__program_name__,
            style=wx.YES_NO | wx.CENTRE | wx.ICON_QUESTION)
        resp = message.ShowModal()
        if resp == wx.ID_YES:
            _doing_restart = True
        message.Destroy()
        if doing_restart():
            self.Close(False)

    def on_update_for_new_file(self, event):
        """
        This function handles the request to update for a new file, including updating program settings,
        gui button state, and updating the file version label if the file exists
        :param event: The event information generated by the caller, which is typically a text ctrl text change event
        """
        if self.lbl_path is None or self.btn_update_file is None:
            return
        idf = self.lbl_path.GetValue()
        self.settings[Keys.last_idf] = idf
        if os.path.exists(idf):
            self.on_msg(_("IDF File exists, ready to go"))
            self.idf_version = self.get_idf_version(idf)
            self.lbl_old_version.SetLabel("%s: %s" % (_('Old Version'), self.idf_version))
            self.btn_update_file.Enable()
        else:
            self.on_msg(_("IDF File doesn't exist at path given; cannot transition"))
            self.btn_update_file.Disable()

    def on_open_run_dir(self, event):
        """
        This function handles the request to open the current run directory in the default application (Finder...)
        :param event: The event information generated by the caller, which in this case is a wx Button
        """
        try:
            cur_platform = EnergyPlusPath.get_platform()
            open_cmd = ""
            if cur_platform == "linux":
                open_cmd = "xdg-open"
            elif cur_platform == "mac":
                open_cmd = "open"
            elif cur_platform == "windows":
                open_cmd = "explorer"
            subprocess.Popen([open_cmd, self.ep_run_folder.transition_directory], shell=False)
        except Exception:
            message = wx.MessageDialog(
                parent=self,
                message=_("Could not open run directory"),
                caption=__program_name__,
                style=wx.OK | wx.CENTRE | wx.ICON_WARNING)
            message.ShowModal()
            message.Destroy()

    def on_closing_form(self, event):
        """
        This function handles the request to close the form, first trying to save program settings
        :param event: The event information generated by the caller, which in this case is a wx Button
        """
        try:
            save_settings(self.settings, self.settings_file_name)
        except Exception:
            pass
        self.Destroy()

    def on_choose_idf(self, event):
        """
        This function handles the request to choose a new idf, opening a dialog, and updating settings if applicable
        :param event: The event information generated by the caller, which in this case is a wx Button
        """
        cur_folder = ""
        cur_idf = ""
        if self.settings[Keys.last_idf] is not None:
            last_idf_full_path = self.settings[Keys.last_idf]
            cur_folder = os.path.dirname(last_idf_full_path)
            cur_idf = os.path.basename(last_idf_full_path)
        elif self.settings[Keys.last_idf_folder] is not None:
            cur_folder = self.settings[Keys.last_idf_folder]
        open_file_dialog = wx.FileDialog(self, _("Open File for Transition"), cur_folder, cur_idf,
                                         "EnergyPlus Input Files (*.idf;*.imf)|*.idf;*.imf",
                                         wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        result = open_file_dialog.ShowModal()
        if result == wx.ID_OK:
            cur_idf_full_path = open_file_dialog.GetPath()
            print(cur_idf)
            self.settings[Keys.last_idf] = cur_idf_full_path
            self.settings[Keys.last_idf_folder] = os.path.dirname(cur_idf_full_path)
            self.lbl_path.SetValue(cur_idf_full_path)
        open_file_dialog.Destroy()

    def on_about(self, event):
        """
        This function handles the request to show the "About..." modal dialog window
        :param event: The event information generated by the caller, which in this case is a wx Button
        """
        message = wx.MessageDialog(parent=self,
                                   message=_("ABOUT_DIALOG"),
                                   caption=__program_name__,
                                   style=wx.OK | wx.CENTRE | wx.ICON_INFORMATION)
        message.ShowModal()
        message.Destroy()

    def on_update_idf(self, event):
        """
        This function handles the request to run Transition itself, building up the list of transitions,
        creating a new thread instance, prepping the gui, and running it
        :param event: The event information generated by the caller, which in this case is a wx Button
        """
        if self.idf_version not in [tr.source_version for tr in self.ep_run_folder.transitions_available]:
            self.on_msg(_("Cannot find a matching transition tool for this idf version"))
        # we need to build up the list of transition steps to perform
        transitions_to_run = []
        for tr in self.ep_run_folder.transitions_available:
            if tr.source_version < self.idf_version:
                continue  # skip this older version
            transitions_to_run.append(tr)
        self.running_transition_thread = TransitionRunThread(
            transitions_to_run,
            self.ep_run_folder.transition_directory,
            self.settings[Keys.last_idf],
            self.chk_create_inter_versions.GetValue(),
            self.callback_on_msg,
            self.callback_on_done
        )
        self.running_transition_thread.start()
        self.set_buttons_for_running(enabled=False)

    def on_cancel(self, event):
        self.btn_cancel.Disable()
        self.running_transition_thread.stop()

    def on_close(self, event):
        """
        This function handles the request to close the form, simply calling Close
        Note this does not destroy the form, allowing the owning code to still access the form settings
        :param event: The event information generated by the caller, which in this case is a wx Button
        """
        self.Close(False)

    # Callback functions and delegates to be called on MainLoop thread

    def callback_on_msg(self, message):
        wx.CallAfter(self.on_msg, message)

    def on_msg(self, message):
        self.status_bar.SetStatusText(message)

    def callback_on_done(self, message):
        wx.CallAfter(self.on_done, message)

    def on_done(self, message):
        self.status_bar.SetStatusText(message)
        self.set_buttons_for_running(enabled=True)

    # Utilities

    @staticmethod
    def get_idf_version(path_to_idf):
        """
        This function returns the current version of a given input file.
        The function uses a simplified parsing approach so it only works for valid syntax files, and provides no specialized error handling

        :param path_to_idf: Absolute path to a EnergyPlus input file
        :rtype: A floating point version number for the input file, for example 8.5 for an 8.5.0 input file
        """
        # phase 1: read in lines of file
        with open(path_to_idf, "r") as fo:
            lines = fo.readlines()
        # phases 2: remove comments and blank lines
        lines_a = []
        for line in lines:
            line_text = line.strip()
            this_line = ""
            if len(line_text) > 0:
                exclamation = line_text.find("!")
                if exclamation == -1:
                    this_line = line_text
                elif exclamation == 0:
                    this_line = ""
                elif exclamation > 0:
                    this_line = line_text[:exclamation]
                if not this_line == "":
                    lines_a.append(this_line)
        # phase 3: join entire array and re-split by semicolon
        idf_data_joined = ''.join(lines_a)
        idf_object_strings = idf_data_joined.split(";")
        # phase 4: break each object into an array of object name and field values
        for this_object in idf_object_strings:
            tokens = this_object.split(',')
            if tokens[0].upper() == "VERSION":
                version_string = tokens[1]
                version_string_tokens = version_string.split('.')  # might be 2 or 3...
                version_number = float("%s.%s" % (version_string_tokens[0], version_string_tokens[1]))
                return version_number
