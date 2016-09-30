import os
# import subprocess

import wx

from EnergyPlusPath import EnergyPlusPath
from EnergyPlusThread import EnergyPlusThread
# from FileTypes import FileTypes
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
        wx.Frame.__init__(self, None, title=__program_name__, size=(550, 183))
        self.SetMinSize((400, 175))

        self.settings_file_name = os.path.join(os.path.expanduser("~"), ".idfversionupdater.json")
        self.settings = load_settings(self.settings_file_name)

        # there should be some equivalent for box_spacing in wx land
        # initialize some class-level "constants"
        self.box_spacing = 4

        # initialize instance variables to be set later
        self.btn_select_idf = None
        self.btn_about = None
        self.lbl_path = None
        self.lbl_old_version = None
        self.chk_create_inter_versions = None
        self.btn_update_file = None
        self.btn_view_audit_file = None
        self.btn_exit = None
        self.status_bar = None

        # try to load the settings very early since it includes initialization
        set_language(self.settings[Keys.language])

        # connect signals for the GUI
        self.Bind(wx.EVT_CLOSE, self.on_closing_form)

        # build up the GUI itself
        self.build_gui()

        # update the list of E+ versions
        self.ep_run_folder = EnergyPlusPath.get_latest_eplus_version()
        self.status_bar.SetStatusText(EnergyPlusThread.get_ep_version(os.path.join(self.ep_run_folder, 'EnergyPlus')))

        # for good measure, check the validity of the idf/epw versions once at load time
        # self.check_file_paths(None)

    def on_closing_form(self, event):
        try:
            save_settings(self.settings, self.settings_file_name)
        except Exception as e:
            pass
        self.Destroy()

    def build_gui(self):
        """
        This function manages the window construction, including position, title, and presentation
        """
        self.status_bar = self.CreateStatusBar()  # A StatusBar in the bottom of the window

        # highest level layout control is the main panel
        panel = wx.Panel(self, wx.ID_ANY)

        # this is then broken into rows with one vertical sizer
        topSizer = wx.BoxSizer(wx.VERTICAL)

        # each row then has their own horizontal sizers on which controls are placed
        choose_about_sizer = wx.BoxSizer(wx.HORIZONTAL)
        path_version_sizer = wx.BoxSizer(wx.HORIZONTAL)
        checkbox_sizer = wx.BoxSizer(wx.HORIZONTAL)
        update_audit_close_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # let's create a bunch of controls
        self.btn_select_idf = wx.Button(panel, wx.ID_ANY, 'Choose File to Update...')
        self.btn_select_idf.Bind(wx.EVT_BUTTON, self.on_choose_idf)
        self.btn_about = wx.Button(panel, wx.ID_ANY, 'About...')
        self.btn_about.Bind(wx.EVT_BUTTON, self.on_about)
        self.lbl_path = wx.StaticText(panel, wx.ID_ANY, 'File Path')
        self.lbl_old_version = wx.StaticText(panel, wx.ID_ANY, 'Old Version')
        self.chk_create_inter_versions = wx.CheckBox(panel, wx.ID_ANY, 'Keep Intermediate Versions?')
        self.btn_update_file = wx.Button(panel, wx.ID_ANY, 'Update File')
        self.btn_update_file.Bind(wx.EVT_BUTTON, self.on_update_idf)
        self.btn_view_audit_file = wx.Button(panel, wx.ID_ANY, 'View Audit File...')
        self.btn_view_audit_file.Bind(wx.EVT_BUTTON, self.on_view_audit)
        self.btn_exit = wx.Button(panel, wx.ID_ANY, 'Close')
        self.btn_exit.Bind(wx.EVT_BUTTON, self.on_close)

        # now let's add the controls to each sizer
        choose_about_sizer.Add(self.btn_select_idf, 1, flag=wx.ALIGN_LEFT | wx.LEFT, border=self.box_spacing)
        choose_about_sizer.Add(wx.StaticText(panel, -1, ''), 100, wx.EXPAND, border=self.box_spacing)
        choose_about_sizer.Add(self.btn_about, 1, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=self.box_spacing)
        path_version_sizer.Add(self.lbl_path, 100, flag=wx.ALIGN_LEFT | wx.LEFT, border=self.box_spacing)
        path_version_sizer.Add(self.lbl_old_version, 1, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=self.box_spacing)
        checkbox_sizer.Add(self.chk_create_inter_versions, 1, wx.EXPAND, border=self.box_spacing)
        update_audit_close_sizer.Add(self.btn_update_file, 1, flag=wx.ALIGN_LEFT | wx.LEFT, border=self.box_spacing)
        update_audit_close_sizer.Add(wx.StaticText(panel, -1, ''), 7, wx.EXPAND, border=self.box_spacing)
        update_audit_close_sizer.Add(self.btn_view_audit_file, 1, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=self.box_spacing)
        update_audit_close_sizer.Add(self.btn_exit, 1, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=self.box_spacing)

        # then we'll add all the horizontal sizers into the main vertical sizer
        topSizer.Add(choose_about_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=self.box_spacing)
        topSizer.Add(wx.StaticLine(panel, ), proportion=0, flag=wx.EXPAND | wx.ALL, border=self.box_spacing)
        topSizer.Add(path_version_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=self.box_spacing)
        topSizer.Add(wx.StaticLine(panel, ), proportion=0, flag=wx.EXPAND | wx.ALL, border=self.box_spacing)
        topSizer.Add(checkbox_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=self.box_spacing)
        topSizer.Add(wx.StaticLine(panel, ), proportion=0, flag=wx.EXPAND | wx.ALL, border=self.box_spacing)
        topSizer.Add(update_audit_close_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=self.box_spacing)

        # and now tell the panel we are using this topSizer
        panel.SetSizer(topSizer)

        # also build out the menu bar
        menuBar = wx.MenuBar()
        menu1 = wx.Menu()
        # create the actual actionable items under the language menu
        menu1.Append(103, "English", "Change language to English")
        self.Bind(wx.EVT_MENU, self.switch_language, id=103)
        menu1.Append(104, "Spanish", "Change language to Spanish")
        self.Bind(wx.EVT_MENU, self.switch_language, id=104)
        menu1.Append(105, "French", "Change language to French")
        self.Bind(wx.EVT_MENU, self.switch_language, id=105)
        menu1.AppendSeparator()
        menu1.Append(106, "&Close\tCtrl+W", "Closes the window")
        self.Bind(wx.EVT_MENU, self.on_close, id=106)
        menuBar.Append(menu1, "&File")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # finally show the window in the center of the (primary? current?) screen
        self.Show(True)
        self.CenterOnScreen()

    def on_choose_idf(self, event):
        print("on_choose_idf")

    def on_about(self, event):
        print("on_about")

    def on_update_idf(self, event):
        print("on_update_idf")

    def on_view_audit(self, event):
        print("on_view_audit")

    def hello(self, event):
        print("Hello world")

    def on_close(self, event):
        print("Closing")
        self.Close(False)

#
#     def open_input_file(self, widget):
#         try:
#             subprocess.check_call(['open', self.input_file_path.get_text()], shell=False)
#         except Exception:
#             self.simple_error_dialog(
#                 _("Could not open input file, set default application by opening the file separately first.")
#             )
#
    def switch_language(self, event):
        id = event.GetId()
        language = Languages.English
        if id == 103:
            language = Languages.English
        elif id == 104:
            language = Languages.Spanish
        elif id == 105:
            language = Languages.French
        self.settings[Keys.language] = language
        print("Changing language to: " + language)
        # dialog = gtk.MessageDialog(
        #     parent=self,
        #     flags=0,
        #     type=gtk.MESSAGE_ERROR,
        #     buttons=gtk.BUTTONS_YES_NO,
        #     message_format=__program_name__)
        # dialog.set_title(_("Message"))
        # dialog.format_secondary_text(
        #     _("You must restart the app to make the language change take effect.  Would you like to restart now?"))
        # resp = dialog.run()
        # if resp == gtk.RESPONSE_YES:
        #     self.doing_restart = True
        # dialog.destroy()
        # if self.doing_restart:
        #     self.quit(None)
#
#     def select_input_file(self, widget, flag):
#         message, file_filters = FileTypes.get_materials(flag)
#         if flag == FileTypes.IDF:
#             key = Keys.last_idf_folder
#         else:
#             key = Keys.last_epw_folder
#         dialog = gtk.FileChooserDialog(
#             title=message,
#             action=gtk.FILE_CHOOSER_ACTION_OPEN,
#             buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)
#         )
#         dialog.set_select_multiple(False)
#         for file_filter in file_filters:
#             dialog.add_filter(file_filter)
#         if self.settings[key] is not None:
#             dialog.set_current_folder(self.settings[key])
#         response = dialog.run()
#         if response == gtk.RESPONSE_OK:
#             self.settings[key] = dialog.get_current_folder()
#             if flag == FileTypes.IDF:
#                 self.input_file_path.set_text(dialog.get_filename())
#             elif flag == FileTypes.EPW:
#                 self.weather_file_path.set_text(dialog.get_filename())
#             dialog.destroy()
#         else:
#             print(_("Cancelled!"))
#             dialog.destroy()
#
#     def run_simulation(self, widget):
#         self.running_simulation_thread = EnergyPlusThread(
#             os.path.join(self.ep_run_folder, 'energyplus'),
#             self.input_file_path.get_text(),
#             self.weather_file_path.get_text(),
#             self.message,
#             self.callback_handler_success,
#             self.callback_handler_failure,
#             self.callback_handler_cancelled
#         )
#         self.running_simulation_thread.start()
#         self.update_run_buttons(running=True)
#
#     def update_run_buttons(self, running=False):
#         self.button_sim.set_sensitive(not running)
#         self.button_cancel.set_sensitive(running)
#
#     def message(self, message):
#         gobject.idle_add(self.message_handler, message)
#
#     def message_handler(self, message):
#         self.status_bar.push(self.status_bar_context_id, message)
#
#     def callback_handler_cancelled(self):
#         gobject.idle_add(self.cancelled_simulation)
#
#     def cancelled_simulation(self):
#         self.update_run_buttons(running=False)
#
#     def callback_handler_failure(self, std_out, run_dir, cmd_line):
#         gobject.idle_add(self.failed_simulation, std_out, run_dir, cmd_line)
#
#     def failed_simulation(self, std_out, run_dir, cmd_line):
#         self.update_run_buttons(running=False)
#         message = gtk.MessageDialog(parent=self,
#                                     flags=0,
#                                     type=gtk.MESSAGE_ERROR,
#                                     buttons=gtk.BUTTONS_YES_NO,
#                                     message_format=_("EnergyPlus Failed!"))
#         message.set_title(_("EnergyPlus Failed"))
#         message.format_secondary_text(
#             _("Error file is the best place to start.  Would you like to open the Run Folder?"))
#         response = message.run()
#         if response == gtk.RESPONSE_YES:
#             subprocess.Popen(['open', run_dir], shell=False)
#         message.destroy()
#
#     def callback_handler_success(self, std_out, run_dir):
#         gobject.idle_add(self.completed_simulation, std_out, run_dir)
#
#     def completed_simulation(self, std_out, run_dir):
#         # update the GUI buttons
#         self.update_run_buttons(running=False)
#         # create the dialog
#         result_dialog = gtk.Dialog(_("Simulation Output"),
#                                    self,
#                                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
#                                    (_("Open Run Directory"), gtk.RESPONSE_YES, _("Close"), gtk.RESPONSE_ACCEPT)
#                                    )
#         # put a description label
#         label = gtk.Label(_("EnergyPlus Simulation Output:"))
#         label.show()
#         aligner = gtk.Alignment(xalign=1.0, yalign=0.5, xscale=1.0, yscale=1.0)
#         aligner.add(label)
#         aligner.show()
#         result_dialog.vbox.pack_start(aligner, False, True, 0)
#
#         # put the actual simulation results
#         label = gtk.Label(std_out)
#         scrolled_results = gtk.ScrolledWindow()
#         scrolled_results.set_border_width(10)
#         scrolled_results.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
#         scrolled_results.add_with_viewport(label)
#         scrolled_results.show()
#         result_dialog.vbox.pack_start(scrolled_results, True, True, 0)
#         label.show()
#         result_dialog.set_size_request(width=500, height=600)
#         resp = result_dialog.run()
#         if resp == gtk.RESPONSE_YES:
#             try:
#                 subprocess.Popen(['open', run_dir], shell=False)
#             except Exception:
#                 self.simple_error_dialog(_("Could not open run directory"))
#         result_dialog.destroy()
#
#     def cancel_simulation(self, widget):
#         self.button_cancel.set_sensitive(False)
#         self.running_simulation_thread.stop()
#
#     def check_file_paths(self, widget):
#         if self.weather_file_path is None or self.input_file_path is None or self.status_bar is None:
#             return  # we are probably doing early initialization of the GUI
#         idf = self.input_file_path.get_text()
#         epw = self.weather_file_path.get_text()
#         self.settings[Keys.last_idf] = idf
#         self.settings[Keys.last_epw] = epw
#         if os.path.exists(idf) and os.path.exists(epw):
#             self.message_handler(_("Ready for launch"))
#             self.button_sim.set_sensitive(True)
#             self.edit_idf_button.set_sensitive(True)
#         else:
#             self.message_handler(_("Input and/or Weather file paths are invalid"))
#             self.button_sim.set_sensitive(False)
#             self.edit_idf_button.set_sensitive(False)
#
#     def simple_error_dialog(self, message_text):
#         message = gtk.MessageDialog(parent=self,
#                                     flags=0,
#                                     type=gtk.MESSAGE_ERROR,
#                                     buttons=gtk.BUTTONS_OK,
#                                     message_format=_("Error performing prior action:"))
#         message.set_title(__program_name__)
#         message.format_secondary_text(message_text)
#         message.run()
#         message.destroy()
#
#     def about_dialog(self, widget):
#         message = gtk.MessageDialog(parent=self,
#                                     flags=0,
#                                     type=gtk.MESSAGE_INFO,
#                                     buttons=gtk.BUTTONS_OK,
#                                     message_format=__program_name__)
#         message.set_title(__program_name__)
#         message.format_secondary_text(_("ABOUT_DIALOG"))
#         message.run()
#         message.destroy()
