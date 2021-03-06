from __future__ import unicode_literals

import subprocess

from ..compat import shlex_quote
from ..utils import PostProcessingError
from .common import PostProcessor


class ExecAfterDownloadPP(PostProcessor):
    def __init__(self, downloader, exec_cmd):
        super(ExecAfterDownloadPP, self).__init__(downloader)
        self.exec_cmd = exec_cmd

    def run(self, information):
        cmd = self.exec_cmd
        if '{}' not in cmd:
            cmd += ' {}'

        cmd = cmd.replace('{}', shlex_quote(information['filepath']))

        self._downloader.to_screen('[exec] Executing command: %s' % cmd)
        retCode = subprocess.call(cmd, shell=True)
        if retCode != 0:
            raise PostProcessingError(
                'Command returned error code %d' % retCode)

        return [], information
