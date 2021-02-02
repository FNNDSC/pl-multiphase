#!/usr/bin/env python
#
# multiphase ds ChRIS plugin app
#
# (c) 2021 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

from chrisapp.base import ChrisApp
import      pudb
import      subprocess
import      pfmisc
from        pfmisc._colors      import  Colors

Gstr_title = """


                 _ _   _       _
                | | | (_)     | |
 _ __ ___  _   _| | |_ _ _ __ | |__   __ _ ___  ___
| '_ ` _ \| | | | | __| | '_ \| '_ \ / _` / __|/ _ \.
| | | | | | |_| | | |_| | |_) | | | | (_| \__ \  __/
|_| |_| |_|\__,_|_|\__|_| .__/|_| |_|\__,_|___/\___|
                        | |
                        |_|

"""

Gstr_synopsis = """

    NAME

       multiphase.py

    SYNOPSIS

        python multiphase.py                                            \\
            [--exec <appToRun>]                                         \\
            [--specificArgs <pipeSeparatedSpecificArgs>]                \\
            [--commonArgs <commonArgs>]                                 \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--man]                                                     \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [--noJobLogging]                                            \\
            [-v <level>] [--verbosity <level>]                          \\
            [--version]                                                 \\
            <inputDir>                                                  \\
            <outputDir>

    BRIEF EXAMPLE

        * Bare bones execution

            docker run --rm -u $(id -u)                                 \\
                -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing          \\
                fnndsc/pl-multiphase multiphase                         \\
                /incoming /outgoing

    DESCRIPTION

        `multiphase` is a very simple script that runs a specific
        <appToRun> on the underlying system shell multiple times over
        the same <inputDir>. Each run, or phase, differs in the
        set of <pipeSeparatedSpecificArgs> that is passed to the app.

        In each phase, the <commonArgs> is passed.

        The main purpose of this plugin is to allow for one simple
        mechanism of running slightly different flags over the
        same <inputDir> space in several phases, and capturing
        the multiple outputs in the <outputDir>. In the context of
        a `ChRIS` feed tree, this has the effect of having one feed
        thread have effectively multiple runs of some <appToRun>.

    ARGS

        [--exec <appToRun>]
        A specific `app` to run in _multi-phase_ mode. This app must by
        necessity exist within the  `multiphase` container. See the
        `requirements.txt` for list of installed apps

        [--specificArgs <pipeSeparatedSpecificArgs>]
        This is a string list of per-phase specific arguments. Each
        phase is separeted by the pip `|` character.

        [--commonArgs <commonArgs>]
        This is a raw string of args, common to each phase call of the
        <appToRun>.

        [-h] [--help]
        If specified, show help message and exit.

        [--json]
        If specified, show json representation of app and exit.

        [--man]
        If specified, print (this) man page and exit.

        [--meta]
        If specified, print plugin meta data and exit.

        [--savejson <DIR>]
        If specified, save json representation file to DIR and exit.

        [-v <level>] [--verbosity <level>]
        Verbosity level for app. Not used currently.

        [--version]
        If specified, print version number and exit.
"""

class Multiphase(ChrisApp):
    """
    This ChRIS plugin simply runs/execs other apps
    (these must be in the container) multiple times,
    each time with a slightly different set of CLI.
    """
    PACKAGE                 = __package__
    CATEGORY                = 'utility'
    TYPE                    = 'ds'
    ICON                    = '' # url of an icon image
    MAX_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MAX_CPU_LIMIT           = '' # Override with millicore value as string, e.g. '2000m'
    MIN_CPU_LIMIT           = '' # Override with millicore value as string, e.g. '2000m'
    MAX_MEMORY_LIMIT        = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT        = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_GPU_LIMIT           = 0  # Override with the minimum number of GPUs, as an integer, for your plugin
    MAX_GPU_LIMIT           = 0  # Override with the maximum number of GPUs, as an integer, for your plugin

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """
        self.add_argument("-c", "--commonArgs",
                            help        = "DS arguments to pass except inputdir and outputdir",
                            type        = str,
                            dest        = 'commonArgs',
                            optional    = True,
                            default     = "")

        self.add_argument("-s", "--specificArgs",
                            help        = "DS arguments to pass",
                            type        = str,
                            dest        = 'specificArgs',
                            optional    = True,
                            default     = "")

        self.add_argument("-e", "--exec",
                            help        = "DS app to run",
                            type        = str,
                            dest        = 'exec',
                            optional    = True,
                            default     = "pfdo_mgz2image")

        self.add_argument("--noJobLogging",
                            help        = "Turn off per-job logging to file system",
                            type        = bool,
                            dest        = 'noJobLogging',
                            action      = 'store_true',
                            optional    = True,
                            default     = False)

    def job_run(self, str_cmd):
        """
        Running some CLI process via python is cumbersome. The typical/easy
        path of

                            os.system(str_cmd)

        is deprecated and prone to hidden complexity. The preferred
        method is via subprocess, which has a cumbersome processing
        syntax. Still, this method runs the `str_cmd` and returns the
        stderr and stdout strings as well as a returncode.
        Providing readtime output of both stdout and stderr seems
        problematic. The approach here is to provide realtime
        output on stdout and only provide stderr on process completion.
        """
        d_ret       : dict = {
            'stdout':       "",
            'stderr':       "",
            'returncode':   0
        }
        str_stdoutLine  : str   = ""
        str_stdout      : str   = ""

        p = subprocess.Popen(
                    str_cmd.split(),
                    stdout      = subprocess.PIPE,
                    stderr      = subprocess.PIPE,
        )

        # Realtime output on stdout
        str_stdoutLine  = ""
        str_stdout      = ""
        while True:
            stdout      = p.stdout.readline()
            if p.poll() is not None:
                break
            if stdout:
                str_stdoutLine = stdout.decode()
                if int(self.args['verbosity']):
                    print(str_stdoutLine, end = '')
                str_stdout      += str_stdoutLine
        d_ret['stdout']     = str_stdout
        d_ret['stderr']     = p.stderr.read().decode()
        d_ret['returncode'] = p.returncode
        if int(self.args['verbosity']) and len(d_ret['stderr']):
            print('\nstderr: \n%s' % d_ret['stderr'])
        return d_ret

    def job_stdwrite(self, d_job, str_outputDir, str_prefix = ""):
        """
        Capture the d_job entries to respective files.
        """
        if not self.args['noJobLogging']:
            for key in d_job.keys():
                with open(
                    '%s/%s%s' % (str_outputDir, str_prefix, key), "w"
                ) as f:
                    f.write(str(d_job[key]))
                    f.close()
        return {
            'status': True
        }

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        l_specificArg :     list    = []
        str_cmd:            str     = ""
        count:              int     = 0

        self.args           = vars(options)
        self.__name__       = "multiphase"
        self.dp             = pfmisc.debug(
                                 verbosity   = int(self.args['verbosity']),
                                 within      = self.__name__
                             )

        self.dp.qprint( Colors.CYAN + Gstr_title,
                        level   = 1,
                        syslog  = False)

        self.dp.qprint( Colors.YELLOW + 'Version: %s' % self.get_version(),
                        level   = 1,
                        syslog  = False)

        for k,v in self.args.items():
            self.dp.qprint("%25s: %-40s" % (k, v),
                            comms   = 'status',
                            syslog  = False)
        self.dp.qprint(" ", level   = 1, syslog = False)

        l_specificArg   = options.specificArgs.split('|')
        str_cmd         = ""

        for str_specificArg in l_specificArg:
            if options.exec == 'pfdo_mgz2image':
                str_cmd = '%s -I %s -O %s %s %s' % \
                          (
                            options.exec,
                            options.inputdir,
                            options.outputdir,
                            options.commonArgs,
                            str_specificArg
                        )
            self.dp.qprint("Running %s..." % str_cmd)
            # Run the job and provide realtime stdout
            # and post-run stderr
            self.job_stdwrite(
                self.job_run(str_cmd), options.outputdir,
                '%s-%d-' % (options.exec, count)
            )
            count += 1

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)
