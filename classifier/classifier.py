#!/usr/bin/env python

""" Classifier
    ----------------Contributors----------------
    https://github.com/bhrigu123/classifier/graphs/contributors
    ----------------Maintainer----------------
    Bhrigu Srivastava <captain.bhrigu@gmail.com>
    ----------------License----------------
    The MIT License [https://opensource.org/licenses/MIT]
    Copyright (c) 2015 Bhrigu Srivastava http://bhrigu.me

"""

import argparse
import os
import subprocess
from sys import platform


VERSION = 'Classifier 2.0'
DIRCONFFILE = '.classifier.conf'
PLATFORM = platform
OS = os.name
HELP = """usage: classifier [-i Directory]
        -h, --help        Show help."""
DEFAULT = """IGNORE: crdownload, desktop, opdownload, part, partial
Audio: aa, aac, aiff, amr, dvf, flac, gsm, m4a, m4b, m4p, midi, mp3, msv, ogg, ra, wav, wma
Ringtones: m4r, mmf, srt
Videos: 3g2, 3gp, amv, avi, flv, f4a, f4p, f4v, gifv, m4p, m4v, mkv, mp2, mp4, mpeg, mpg, ogv, rm, svi, ts, vob, webm, wmv
Pictures: bmp, bpg, gif, ico, jpeg, jpg, odg, png, psd, rgbe, svg, tiff, webp, vml
Archives: 7z, bz2, cpio, dmg, gz, iso, lz, rar, tar, tgz, xz, zip
Documents: ai, atom, doc, docx, kdb, kdbx, odf, odm, odp, ods, odt, pdf, ppsx, ppt, pptx, pub, qif, rtf, sxw, xls, xlsv, xlsx, xml, xt
Webpages: asp, aspx, cgi, htm, html, xhtml
Programming: a, c, cljs, coffee, class, d, e, el, erb, fth, go, java, js, lua, lisp, m, o, p, php, pl, pm, py, pyc, pyo, r, rb, so, tcl
Plain Text: asc, cer, cfg, conf, crt, css, csv, ini, inf, json, log, md, pem, pub, ppk, ssh, txt, xml, yaml
Books: chm, epub, fb2, mobi
Packages: deb, ebuild, jar, rpm
Programs: bat, cmd, com, exe, msi, out, sh, vbs"""


if PLATFORM == 'darwin':
    CONFIG = os.path.join(os.path.expanduser('~'), '.classifier-master.conf')
elif PLATFORM == 'win32' or OS == 'nt':
    CONFIG = os.path.join(os.getenv('userprofile'), 'classifier-master.conf')
elif PLATFORM == 'linux' or PLATFORM == 'linux2' or OS == 'posix':
    CONFIG = os.path.join(os.getenv('HOME'), '.classifier-master.conf')
else:
    CONFIG = os.path.join(os.getcwd(), '.classifier-master.conf')

class Classifier:
    """
    All format lists were taken from wikipedia, not all were added due to extensions
    not being exclusive to one format such as webm, or raw
    Audio           -       https://en.wikipedia.org/wiki/Audio_file_format
    Ringtones       -       https://en.wikipedia.org/wiki/Ringtone#Ring_tone_encoding_formats
    Images          -       https://en.wikipedia.org/wiki/Image_file_formats
    Video           -       https://en.wikipedia.org/wiki/Video_file_format
    Documents       -       https://en.wikipedia.org/wiki/List_of_Microsoft_Office_filename_extensions
                            https://en.wikipedia.org/wiki/Document_file_format
    Others          -       https://en.wikipedia.org/wiki/List_of_file_formats
    """

    def __init__(self):
        self.prog=VERSION
        self.description = "Organize files in your directory into different folders"
        self.parser = argparse.ArgumentParser(description=self.description)

        self.parser.add_argument("-v", "--version", action='store_true',
                                 help="Show version and exit")

        self.parser.add_argument("-e", "--edit", action='store_true',
                                 help="Edit the list of types and formats")

        self.parser.add_argument("-t", "--types", action='store_true',
                                 help="Show the current list of types and formats")

        self.parser.add_argument("-r", "--reset", action='store_true',
                                 help="Reset the default Config file")

        self.parser.add_argument("-s", "--show-default", action='store_true',
                                  help="Show the default Config file")
        
        """
        self.parser.add_argument("-re", "--recursive", action='store_true',
                                 help="Recursively search your source directory. " +
                                 "WARNING: Ensure you use the correct path as this " +
                                 "WILL move all files from your selected types.")
        """        

        self.parser.add_argument("-st", "--specific-types", type=str, nargs='+',
                                 help="Move all file extensions, given in the args list, " +
                                      "in the current directory into the Specific Folder")

        self.parser.add_argument("-sf", "--specific-folder", type=str,
                                 help="Folder to move Specific File Type")

        self.parser.add_argument("-o", "--output", type=str,
                                 help="Main directory to put organized folders")

        self.parser.add_argument("-i", "--input", type=str,
                                 help="The directory whose files to classify")

        self.parser.add_argument("-d", "--date", action='store_true',
                                 help="Organize files by creation date")

        self.parser.add_argument("-f", "--format", type=str,
                                 help="set the date format using YYYY, MM or DD")

        self.args = self.parser.parse_args()
        self.dateformat = 'YYYY-MM-DD'
        self.formats = {}
        self.dirconf = None
        self.checkconfig()
        self.run()

    def create_default_config(self):
        with open(CONFIG, "w") as conffile:
            conffile.write(DEFAULT)
        print("CONFIG file created at: "+CONFIG)

    def checkconfig(self):
        """ create a default config if not available """
        if not os.path.isdir(os.path.dirname(CONFIG)):
            os.makedirs(os.path.dirname(CONFIG))
        if not os.path.isfile(CONFIG):
            self.create_default_config()

        with open(CONFIG, 'r') as file:
            for items in file:
                spl = items.replace('\n', '').split(':')
                key = spl[0].replace(" ","")
                val = spl[1].replace(" ","")
                self.formats[key] = val
        return

    def moveto(self, filename, from_folder, to_folder):
        from_file = os.path.join(from_folder, filename)
        to_file = os.path.join(to_folder, filename)
        # to move only files, not folders
        if not to_file == from_file:
            print('moved: ' + str(to_file))
            if os.path.isfile(from_file):
                if not os.path.exists(to_folder):
                    os.makedirs(to_folder)
                os.rename(from_file, to_file)
        return

    def classify(self, formats, output, directory):
        for file in os.listdir(directory):
            tmpbreak = False
            # set up a config per folder
            if not file == DIRCONFFILE and os.path.isfile(os.path.join(directory, file)):
                filename, file_ext = os.path.splitext(file)
                file_ext = file_ext.lower().replace('.', '')
                if 'IGNORE' in self.formats:
                    for ignored in self.formats['IGNORE'].replace('\n', '').split(','):
                        if file_ext == ignored:
                            tmpbreak = True
                if not tmpbreak:
                    for folder, ext_list in list(formats.items()):
                        # never move files in the ignore list
                        if not folder == 'IGNORE':
                            folder = os.path.join(output, folder)
                            # make sure we are passing a list to the extension checker
                            if type(ext_list) == str:
                                ext_list = ext_list.split(',')
                            for tmp_ext in ext_list:
                                if file_ext == tmp_ext:
                                    try:
                                        self.moveto(file, directory, folder)
                                    except Exception as e:
                                        print('Cannot move file - {} - {}'.format(file, str(e)))
            """
            elif os.path.isdir(os.path.join(directory, file)) and self.args.recursive:
                self.classify(self.formats, output, os.path.join(directory, file))
            """
        return

    def classify_by_date(self, date_format, output, directory):
        print("Scanning Files")

        files = [x for x in os.listdir(directory) if not x.startswith('.')]
        creation_dates = map(lambda x: (x, arrow.get(os.path.getctime(os.path.join(directory, x)))), files)
        print(creation_dates)

        for file, creation_date in creation_dates:
            folder = creation_date.format(date_format)
            folder = os.path.join(output, folder)
            self.moveto(file, directory, folder)

        return

    def _format_text_arg(self, arg):
        """ Set a date format to name your folders"""
        if not isinstance(arg, str):
            arg = arg.decode('utf-8')
        return arg

    def _format_arg(self, arg):
        if isinstance(arg, str):
            arg = self._format_text_arg(arg)
        return arg

    def run(self):
        
        if self.args.version:
            # Show version information and quit
            print(VERSION)
            return False

        if self.args.types:
            # Show file format information then quit
            for key, value in self.formats.items():
                print(key + ': '+ value)
            return False

        if self.args.edit:
            if PLATFORM == 'darwin':
                subprocess.call(('open', '-t', CONFIG))
            elif PLATFORM == 'win32' or OS == 'nt':
                os.startfile(CONFIG)
            elif PLATFORM == 'linux' or PLATFORM == 'linux2' or OS == 'posix':
                subprocess.Popen(['xdg-open', CONFIG])
            return False

        if self.args.reset:
            self.create_default_config()
            return False

        if self.args.show_default:
            print(DEFAULT)
            return False

        if bool(self.args.specific_folder) ^ bool(self.args.specific_types):
            print('Specific Folder and Specific Types need to be specified together')
            quit()

        if self.args.specific_folder and self.args.specific_types:
            specific_folder = self._format_arg(self.args.specific_folder)
            self.formats = {specific_folder: self.args.specific_types}

        if self.args.output is None:
            output = self.args.input
        else:
            output = self._format_arg(self.args.output)

        # Check for a config file in the source file directory
        if self.args.input and os.path.isfile(os.path.join(self.args.input, DIRCONFFILE)):
                self.dirconf = os.path.join(self.args.input, DIRCONFFILE)

        if self.args.format and not self.args.date:
                print('Dateformat -f must be given along with date -d option')
                quit()

        if self.args.date:
            try:
                import arrow
            except ImportError:
                print("You must install arrow using 'pip install arrow' to use date formatting.")
                return False
            if self.args.dateformat:
                self.classify_by_date(self.args.dateformat, output, directory)
            else:
                self.classify_by_date(self.dateformat, output, directory)
        elif self.dirconf and os.path.isfile(self.dirconf):
            print('Using config in current directory')
            if self.args.output:
                print('Config in output directory is being ignored')
            for items in open(self.dirconf, "r"):
                # reset formats for individual folders
                self.formats = {}
                try:
                    (key, dst, val) = items.split(':')
                    self.formats[key] = val.replace('\n', '').split(',')
                    print("\nScanning:  " + input +
                          "\nFor:       " + key +
                          '\nFormats:   ' + val)
                    self.classify(self.formats, dst, directory)
                except ValueError:
                    print("Your local config file is malformed. Please check and try again.")
                    return False

        if self.args.input is None:
            print(HELP)
            return False
        
        directory = self._format_arg(self.args.input)
        if self.args.output is None:
            output = directory
            
        print("\nScanning Folder: " + directory)
        if self.args.specific_types:
            print("For: " + str(self.formats.items()))
        else:
            print("Using the default CONFIG File\n")
        self.classify(self.formats, output, directory)
        print("Done!")
        return True

if __name__ == "__main__":
    Classifier()
