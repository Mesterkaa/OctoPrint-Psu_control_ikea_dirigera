# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import dirigera

class Psu_control_ikea_dirigeraPlugin(octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin
):

    def __init__(self):
        self.config = dict()
        self.hub = None

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            IP = '',
            Token = '',
            Outlet_Name = ''
        )

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.reload_settings()

    def get_settings_version(self):
        return 1

    def reload_settings(self):
        for key, value in self.get_settings_defaults().items():
            if type(value) == str:
                value = self._settings.get([key])
            elif type(value) == int:
                value = self._settings.get_int([key])
            elif type(value) == float:
                value = self._settings.get_float([key])
            elif type(value) == bool:
                value = self._settings.get_boolean([key])

            self.config[key] = value
            self._logger.debug("{}: {}".format(key, value))

        self._logger.info(f"Config: {self.config}")
        self._init_hub()

    def on_settings_migrate(self, target, current=None):
        pass

    def on_startup(self, host, port):
        psucontrol_helpers = self._plugin_manager.get_helpers("psucontrol")
        if not psucontrol_helpers or 'register_plugin' not in psucontrol_helpers.keys():
            self._logger.warning("The version of PSUControl that is installed does not support plugin registration.")
            return

        self._logger.debug("Registering plugin with PSUControl")
        psucontrol_helpers['register_plugin'](self)
        self._init_hub()

    def _init_hub(self):
        self._logger.info("Initializing Hub")
        if self.config['Token'] is not None and self.config['IP'] is not None:
            self._logger.info("Hub initialized")
            self.hub = dirigera.Hub(
                token=self.config['Token'],
                ip_address=self.config['IP']
            )
        else:
            self._logger.info("Hub not initialized. Config not set")

    def turn_psu_on(self):
        if self.hub is not None and self.config['Outlet_Name'] is not None:
            smart_plug = self.hub.get_outlet_by_name(self.config['Outlet_Name'])
            smart_plug.set_on(outlet_on=True)
        pass

    def turn_psu_off(self):
        if self.hub is not None and self.config['Outlet_Name'] is not None:
            smart_plug = self.hub.get_outlet_by_name(self.config['Outlet_Name'])
            smart_plug.set_on(outlet_on=False)
        pass

    def get_psu_state(self):
        if self.hub is not None and self.config['Outlet_Name'] is not None:
            smart_plug = self.hub.get_outlet_by_name(self.config['Outlet_Name'])
            return smart_plug.attributes.is_on()
        return False

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "PSU_Control_IKEA_Dirigera": {
                "displayName": "Psu_control_ikea_dirigera Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "Mesterkaa",
                "repo": "OctoPrint-Psu_control_ikea_dirigera",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/Mesterkaa/OctoPrint-Psu_control_ikea_dirigera/archive/{target_version}.zip",
            }
        }


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
## __plugin_name__ = "PSU Control - IKEA Dirigera"


# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.4.0 - 1.7.x run under both Python 3 and the end-of-life Python 2.
# OctoPrint 1.8.0 onwards only supports Python 3.
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Psu_control_ikea_dirigeraPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
