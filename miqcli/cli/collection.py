import os
import yaml
import ast
import sys

from miqcli.constants import MIQCLI_CFG_FILE_LOC, MIQCLI_CFG_NAME

class Collection(object):
    """
    Collection Class

    Main option is to save the settings
    """

    _settings = None

    def __init__(self, settings):
        """
        :param settings: MIQ settings
        :type settings: dict
        """
        self._settings = settings

    @property
    def settings(self):
        """
        :return: dict of settings
        """
        return self._settings

    def set_settings(self):
        """
        Verify the settings are already set, if not go through all options
        of collecting settings
        :return:
        """
        # Get configuration setup for the Collections
        # if global options will take the highest precedence
        settings = self._settings
        if settings["url"] or settings["username"] or settings["password"] or \
                settings["token"]:
            # the global settings have been set no need to do anything
            pass

        # setting the MIQ_CFG_FILE env var will have the 2nd highest precedence
        elif 'MIQ_CFG' in os.environ and os.environ['MIQ_CFG']:
            self._settings = ast.literal_eval(os.environ['MIQ_CFG'])

        # check the local path for the config file
        elif os.path.isfile(os.path.join(os.getcwd(), MIQCLI_CFG_NAME)):
            local_cfg = os.path.join(os.getcwd(), MIQCLI_CFG_NAME)
            stream = file(local_cfg, 'r')
            self._settings = yaml.load(stream)

        # the MIQ default config file has the lowest precedence
        else:
            try:
                stream = file(os.path.join(
                    MIQCLI_CFG_FILE_LOC, MIQCLI_CFG_NAME), 'r')
                self._settings = yaml.load(stream)
            except:
                print ("Please set the required settings in the file:"
                                " {}".format(os.path.join(MIQCLI_CFG_FILE_LOC,
                                                         MIQCLI_CFG_NAME)))
                sys.exit(1)
