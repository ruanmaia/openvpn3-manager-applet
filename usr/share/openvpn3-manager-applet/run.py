import gi
import os
import subprocess
import pickle

from pathlib import Path

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk
from gi.repository import AppIndicator3
from gi.repository import Notify


class OpenVPN3ManagerApplet:

    DIALOG_RETURN_CLOSE=-4
    DIALOG_RETURN_CANCEL=0
    DIALOG_RETURN_SAVE=1

    def __init__(self):
        
        self._HOME = os.getenv('HOME')
        
        self._VPN_PATH = self._HOME + '/.vpn'
        self._EXEC_BIN = '/usr/bin/openvpn3'
        self._DATA_FILE = self._VPN_PATH + '/credentials.db'
        
        self._credentials = {}
        self._auth_dialog = None

        self._load_credentials()
        self._load_config_files()

        self._build_applet()


    def _load_credentials(self):
        if not Path(self._DATA_FILE).exists():
            print('CREATING DATABASE...')
            self._save_credentials()
        else:
            print('READING DATABASE...')
            with open(self._DATA_FILE, mode='rb') as f:
                self._credentials = pickle.load(f)


    def _save_credentials(self):
        with open(self._DATA_FILE, mode='wb') as f:
            pickle.dump(self._credentials, f)


    def _load_config_files(self):
        
        p = Path(self._VPN_PATH)
        config_files = set()

        for f in p.glob('*.ovpn'):
            config_files.add(f.stem)            
            if f.stem not in self._credentials.keys():
                print('IMPORTING (%s)' % f.stem)
                subprocess.run(
                    [self._EXEC_BIN, 'config-import', '--config', f.absolute(), '--name', f.stem, '--persistent']
                )
                self._credentials.setdefault(f.stem, None)

        configs_to_remove = set(self._credentials) - config_files
        for config_name in configs_to_remove:
            print('REMOVING (%s)' % config_name)
            subprocess.run(
                [self._EXEC_BIN, 'config-remove', '--force', '--config', config_name]
            )
            del self._credentials[config_name]

        self._save_credentials()


    def _build_applet(self):  
        """
        Starts the building of the applet and menu items
        """

        self._applet = AppIndicator3.Indicator.new(
            "system-lock-screen", 
            "dialog-password", 
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self._applet.set_status(
            AppIndicator3.IndicatorStatus.ACTIVE
        )

        # Create the applet menu 
        self._menu = Gtk.Menu()

        # Build the applet menu items
        for vpn_name in self._credentials.keys():

            check = Gtk.CheckMenuItem(label=vpn_name)
            check.connect('toggled', self._toggle_connection, vpn_name)
            check.show()
            
            self._menu.append(check)         

        # Adding manager actions
        self._build_manager_actions()
        self._menu.show()

        self._applet.set_menu(self._menu)


    def _build_manager_actions(self):
        
        # Adds a menu separator
        separator = Gtk.SeparatorMenuItem.new()
        separator.show()

        # Adds a "Reload Config Files" menu item
        menu_update = Gtk.MenuItem(label='Update Config Files')
        menu_update.connect('activate', self._update_config_files)
        menu_update.show()

        # Adds a "Quit" menu item
        menu_quit = Gtk.MenuItem(label='Quit')
        menu_quit.connect('activate', self._quit)
        menu_quit.show()

        # Adding to applet menu
        self._menu.append(separator)
        self._menu.append(menu_update)     
        self._menu.append(menu_quit) 


    def _toggle_connection(self, widget, data=None):
        
        if self._auth_dialog is not None:
            self._auth_dialog.destroy()

        if widget.get_active():
            self._try_connect(widget, data)
        else:
            self._disconnect(widget, data)


    def _try_connect(self, menu_item, session_name):
        
        print('(%s) CONNECTING...' % session_name)
        session_credentials = self._credentials[session_name]

        if session_credentials is None:

            # Create and open the credentials form
            username_label = Gtk.Label(label='Username')
            username_entry = Gtk.Entry()

            password_label = Gtk.Label(label='Password')
            password_entry = Gtk.Entry()
            password_entry.set_visibility(False)

            # Dialog setup
            self._auth_dialog = Gtk.Dialog()
            self._auth_dialog.set_icon_name('dialog-information')
            self._auth_dialog.set_resizable(False)
            self._auth_dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
            self._auth_dialog.set_title('Authentication')
            self._auth_dialog.set_default_size(400, 150)
            self._auth_dialog.set_modal(True)
            
            box = self._auth_dialog.get_content_area()
            
            # Adding username and password inputs
            box.add(username_label)
            box.add(username_entry)
            box.add(password_label)
            box.add(password_entry)

            # Adding action buttons
            self._auth_dialog.add_button('Save', 1)
            self._auth_dialog.add_button('Cancel', 0)
            
            self._auth_dialog.show_all()
            return_code = self._auth_dialog.run()
            
            # Auth form save button clicked
            if return_code == self.DIALOG_RETURN_SAVE:
                username = username_entry.get_text().strip()
                password = password_entry.get_text().strip()

                if len(username) > 3 and len(password) > 3:
                    self._credentials[session_name] = { 'username': username, 'password': password }
                    self._save_credentials()
                else:
                    menu_item.set_inconsistent(True)
                    menu_item.set_active(False)

            # Auth form close/cancel button clicked
            if return_code == self.DIALOG_RETURN_CLOSE or return_code == self.DIALOG_RETURN_CANCEL:
                menu_item.set_inconsistent(True)
                menu_item.set_active(False)

            self._auth_dialog.destroy()

        result = self._make_connection(session_name)
        if result:
            menu_item.set_inconsistent(False)
        else:
            menu_item.set_inconsistent(True)
            menu_item.set_active(False)


    def _make_connection(self, session_name):

        credentials = self._credentials[session_name]
        if credentials is not None:

            # Try to starts a VPN connection
            r = subprocess.run(
                [self._EXEC_BIN, 'session-start', '--config', session_name], 
                input="{}\n{}\n".format(credentials['username'], credentials['password']).encode()
            )

            if r.returncode == 0:
                # Connection success message
                Notify.init('OpenVPN3 Manager Applet')
                notification = Notify.Notification.new('Successfully Connected!', 'The VPN %s was successfully connected!' % session_name, 'dialog-information')
                notification.show()
                return True
            else:
                # Connection error messa
                Notify.init('OpenVPN3 Manager Applet')
                notification = Notify.Notification.new('Connection Error!', 'The VPN %s was unable to connect! Please check your configuration file' % session_name, 'dialog-error')
                notification.show()
                return False


    def _disconnect(self, widget, session_name):
        if not widget.get_inconsistent():
            print('(%s) DISCONNECTING...' % session_name)
            r = subprocess.run(
                [self._EXEC_BIN, 'session-manage', '--config', session_name, '--disconnect']
            )
            if r.returncode == 0:
                Notify.init('OpenVPN3 Manager Applet')
                notification = Notify.Notification.new('Closed connection!', 'The VPN %s was closed!' % session_name, 'dialog-information')
                notification.show()


    def _update_config_files(self, widget):
        print('RELOADING CONFIG FILES...')
        self._load_credentials()
        self._load_config_files()
        self._build_applet()


    def _quit(self, widget, data=None):
        Gtk.main_quit()
        for vpn_name in self._credentials.keys():
            subprocess.run(
                [self._EXEC_BIN, 'session-manage', '--config', vpn_name, '--disconnect']
            )


    def run(self):
        Gtk.main()
        return 0


if __name__ == "__main__":
    manager = OpenVPN3ManagerApplet()
    manager.run()