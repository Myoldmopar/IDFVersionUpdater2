import os
import subprocess

import wx

from EnergyPlusPath import EnergyPlusPath
from EnergyPlusThread import EnergyPlusThread
from International import translate as _, Languages, set_language
from Settings import Keys, load_settings, save_settings

__program_name__ = "IDFVersionUpdater (v2.0)"

_doing_restart = False


def doing_restart():
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
        self.ep_run_folder = EnergyPlusPath.get_latest_eplus_version()
        self.SetTitle(
            __program_name__ + " -- " + EnergyPlusThread.get_ep_version(os.path.join(self.ep_run_folder, 'EnergyPlus')))
        self.status_bar.SetStatusText(_("Program Initialized"))
        self.transition_run_dir = EnergyPlusPath.get_transition_run_dir(self.ep_run_folder)
        self.transitions_available = EnergyPlusPath.get_transitions_available(self.transition_run_dir)

        # check the validity of the idf versions once at load time to initialize the action availability
        self.check_file_paths(None)

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
        self.lbl_path.Bind(wx.EVT_TEXT, self.check_file_paths)
        if self.settings[Keys.last_idf] is not None:
            self.lbl_path.SetValue(self.settings[Keys.last_idf])
        self.lbl_old_version = wx.StaticText(panel, wx.ID_ANY, _('Old Version'))
        self.chk_create_inter_versions = wx.CheckBox(panel, wx.ID_ANY, _('Keep Original Version?'))
        self.btn_update_file = wx.Button(panel, wx.ID_ANY, _('Update File'))
        self.btn_update_file.Bind(wx.EVT_BUTTON, self.on_update_idf)
        self.btn_open_run_dir = wx.Button(panel, wx.ID_ANY, _('Open Run Directory'))
        self.btn_open_run_dir.Bind(wx.EVT_BUTTON, self.on_open_run_dir)
        self.btn_exit = wx.Button(panel, wx.ID_ANY, _('Close'))
        self.btn_exit.Bind(wx.EVT_BUTTON, self.on_close)

        # now let's add the controls to each sizer
        choose_about_sizer.Add(self.btn_select_idf, 1, flag=wx.ALIGN_LEFT | wx.LEFT, border=self.box_spacing)
        choose_about_sizer.Add(wx.StaticText(panel, -1, ''), 100, wx.EXPAND, border=self.box_spacing)
        choose_about_sizer.Add(self.btn_about, 1, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=self.box_spacing)
        path_version_sizer.Add(self.lbl_path, 4, flag=wx.ALIGN_LEFT | wx.LEFT, border=self.box_spacing)
        path_version_sizer.Add(wx.StaticText(panel, -1, ''), 1, wx.EXPAND, border=self.box_spacing)
        path_version_sizer.Add(self.lbl_old_version, 1, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=self.box_spacing)
        checkbox_sizer.Add(self.chk_create_inter_versions, 1, flag=wx.ALIGN_LEFT | wx.LEFT, border=self.box_spacing)
        update_audit_close_sizer.Add(self.btn_update_file, 1, flag=wx.ALIGN_LEFT | wx.LEFT, border=self.box_spacing)
        update_audit_close_sizer.Add(wx.StaticText(panel, -1, ''), 7, wx.EXPAND, border=self.box_spacing)
        update_audit_close_sizer.Add(self.btn_open_run_dir, 1, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=self.box_spacing)
        update_audit_close_sizer.Add(self.btn_exit, 1, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=self.box_spacing)

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
        self.Bind(wx.EVT_MENU, self.switch_language, id=Languages.English)
        menu1.Append(Languages.Spanish, "Spanish", "Change language to Spanish")
        self.Bind(wx.EVT_MENU, self.switch_language, id=Languages.Spanish)
        menu1.Append(Languages.French, "French", "Change language to French")
        self.Bind(wx.EVT_MENU, self.switch_language, id=Languages.French)
        menu1.AppendSeparator()
        menu1.Append(106, "&Close\tCtrl+W", "Closes the window")
        self.Bind(wx.EVT_MENU, self.on_close, id=106)
        menu_bar.Append(menu1, "&File")
        self.SetMenuBar(menu_bar)  # Adding the MenuBar to the Frame content.

        # finally show the window in the center of the (primary? current?) screen
        self.Show(True)
        self.CenterOnScreen()

    def on_open_run_dir(self, event):
        try:
            subprocess.Popen(['open', self.transition_run_dir], shell=False)
        except Exception:
            self.simple_error_dialog(
                _("Could not open run directory")
            )

    def on_closing_form(self, event):
        try:
            save_settings(self.settings, self.settings_file_name)
        except Exception:
            pass
        self.Destroy()

    def on_choose_idf(self, event):
        cur_folder = ""
        if self.settings[Keys.last_idf_folder] is not None:
            cur_folder = self.settings[Keys.last_idf_folder]
        cur_idf = ""
        if self.settings[Keys.last_idf] is not None:
            cur_idf = self.settings[Keys.last_idf]
        open_file_dialog = wx.FileDialog(self, "Open File for Transition", cur_folder, cur_idf,
                                         "EnergyPlus Input Files (*.idf;*.imf)|*.idf;*.imf",
                                         wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        result = open_file_dialog.ShowModal()
        if result == wx.ID_OK:
            cur_idf = open_file_dialog.GetPath()
            self.settings[Keys.last_idf] = cur_idf
            self.settings[Keys.last_idf_folder] = os.path.dirname(cur_idf)
            self.lbl_path.SetValue(cur_idf)
        open_file_dialog.Destroy()

    def on_about(self, event):
        message = wx.MessageDialog(parent=self,
                                   message=_("ABOUT_DIALOG"),
                                   caption=__program_name__,
                                   style=wx.OK | wx.CENTRE | wx.ICON_INFORMATION)
        message.ShowModal()
        message.Destroy()

    def on_update_idf(self, event):
        if self.idf_version not in [tr.source_version for tr in self.transitions_available]:
            self.on_msg("Cannot find a matching transition tool for this idf version")
        # we need to build up the list of transition steps to perform
        transitions_to_run = []
        for tr in self.transitions_available:
            if tr.source_version < self.idf_version:
                continue  # skip this older version
            transitions_to_run.append(tr)
        self.running_transition_thread = EnergyPlusThread(
            transitions_to_run,
            self.transition_run_dir,
            self.settings[Keys.last_idf],
            self.chk_create_inter_versions.GetValue(),
            self.callback_on_msg,
            self.callback_on_done
        )
        self.running_transition_thread.start()
        self.set_buttons_for_running(enabled=False)

    def set_buttons_for_running(self, enabled):
        buttons = [self.btn_update_file, self.btn_select_idf, self.btn_exit]
        if enabled:
            [x.Enable() for x in buttons]
        else:
            [x.Disable() for x in buttons]

    def callback_on_msg(self, message):
        wx.CallAfter(self.on_msg, message)

    def on_msg(self, message):
        self.status_bar.SetStatusText(message)

    def callback_on_done(self, message):
        wx.CallAfter(self.on_done, message)

    def on_done(self, message):
        self.status_bar.SetStatusText(message)
        self.set_buttons_for_running(enabled=True)

    def on_close(self, event):
        self.Close(False)

    def switch_language(self, event):
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

    def check_file_paths(self, event):
        if self.lbl_path is None or self.btn_update_file is None:
            return
        idf = self.lbl_path.GetValue()
        self.settings[Keys.last_idf] = idf
        if os.path.exists(idf):
            self.on_msg("IDF File exists, ready to go")
            self.idf_version = EnergyPlusPath.get_idf_version(idf)
            self.lbl_old_version.SetLabel("%s: %s" % (_('Old Version'), self.idf_version))
            self.btn_update_file.Enable()
        else:
            self.on_msg("IDF File doesn't exist at path given; cannot transition")
            self.btn_update_file.Disable()

# TODO: Add a progress bar to allow watching the individual transition runs go
# TODO: Add a cancel button, just steal it from the EPLaunchLite code
