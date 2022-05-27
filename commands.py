from __future__ import (absolute_import, division, print_function)

import os
from ranger.api.commands import Command


# Changed BulkRename by WSL Editor ( *.exe) or Raw VIM
from commands_full import bulkrename as bk
class bulkrename(bk):
    def execute(self):
        import sys
        import tempfile

        # set tempfile a wsl format path (windows app -> eg: Sublime.exe & Notepad.exe)
        from pathlib import Path  # Maybe python3.4+
        import re

        conf_str = Path(self.fm.rifle.config_file).read_text()
        r1 = re.compile(r"\nmime\s+\^text,\s+label\s+editor\s+(.*?\.exe)")

        # if no windows editor find, nothing happend
        if r1.search(conf_str):
            # May be  /mnt/d should be set in config file for user change
            tempfile.tempdir = "/mnt/d"

        # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        from ranger.container.file import File
        from ranger.ext.shell_escape import shell_escape as esc
        py3 = sys.version_info[0] >= 3

        # Create and edit the file list
        filenames = [f.relative_path for f in self.fm.thistab.get_selection()]

        with tempfile.NamedTemporaryFile(delete=False) as listfile:
            listpath = listfile.name
            if py3:
                listfile.write("\n".join(filenames).encode(
                    encoding="utf-8", errors="surrogateescape"))
            else:
                listfile.write("\n".join(filenames))
        self.fm.execute_file([File(listpath)], app='editor')

        with (open(listpath, 'r', encoding="utf-8", errors="surrogateescape") if
              py3 else open(listpath, 'r')) as listfile:

            # limit that not allow <space> on both sides of filename (in Wslg(Windows) .exe)
            if r1.search(conf_str):  
                new_filenames = listfile.read().strip().split("\n")
                new_filenames = [*map(str.strip, new_filenames)]
            else:
                new_filenames = listfile.read().split("\n")

        os.unlink(listpath)
        if all(a == b for a, b in zip(filenames, new_filenames)):
            self.fm.notify("No renaming to be done!")
            return

        # Generate script
        with tempfile.NamedTemporaryFile() as cmdfile:
            script_lines = []

            # if not wsl app 
            if not r1.search(conf_str):  
                script_lines.append("# This file will be executed when you close"
                                    " the editor.")
                script_lines.append("# Please double-check everything, clear the"
                                    " file to abort.")

            new_dirs = []
            for old, new in zip(filenames, new_filenames):
                if old != new:
                    basepath, _ = os.path.split(new)
                    if (basepath and basepath not in new_dirs
                            and not os.path.isdir(basepath)):
                        script_lines.append("mkdir -vp -- {dir}".format(
                            dir=esc(basepath)))
                        new_dirs.append(basepath)

                    # for wsl app 
                    if r1.search(conf_str):
                        script_lines.append("mv -i -- {old} {new}".format(
                            old=esc(old), new=esc(new)))
                    else:
                        script_lines.append("mv -vi -- {old} {new}".format(
                            old=esc(old), new=esc(new)))

            # Make sure not to forget the ending newline
            script_content = "\n".join(script_lines) + "\n"
            if py3:
                cmdfile.write(script_content.encode(encoding="utf-8",
                                                    errors="surrogateescape"))
            else:
                cmdfile.write(script_content)
            cmdfile.flush()

            # for wsl app (I )
            if r1.search(conf_str):  
                self.fm.run(['/bin/sh', cmdfile.name])

            else:
                # Open the script and let the user review it, then check if the
                # script was modified by the user
                self.fm.execute_file([File(cmdfile.name)], app='editor')
                cmdfile.seek(0)
                script_was_edited = (script_content != cmdfile.read())

                # # Do the renaming
                self.fm.run(['/bin/sh', cmdfile.name], flags='w')

        # Retag the files, but only if the script wasn't changed during review,
        # because only then we know which are the source and destination files.
        # if not wsl app
        if not r1.search(conf_str):  
            if not script_was_edited:
                tags_changed = False
                for old, new in zip(filenames, new_filenames):
                    if old != new:
                        oldpath = self.fm.thisdir.path + '/' + old
                        newpath = self.fm.thisdir.path + '/' + new
                        if oldpath in self.fm.tags:
                            old_tag = self.fm.tags.tags[oldpath]
                            self.fm.tags.remove(oldpath)
                            self.fm.tags.tags[newpath] = old_tag
                            tags_changed = True
                if tags_changed:
                    self.fm.tags.dump()
                else:
                    fm.notify("files have not been retagged")


# From Ranger Wiki
class mkcd(Command):
    """
    :mkcd <dirname>

    Creates a directory with the name <dirname> and enters it.
    """
    def execute(self):
        from os.path import join, expanduser, lexists
        from os import makedirs
        import re

        dirname = join(self.fm.thisdir.path, expanduser(self.rest(1)))
        if not lexists(dirname):
            makedirs(dirname)

            match = re.search('^/|^~[^/]*/', dirname)
            if match:
                self.fm.cd(match.group(0))
                dirname = dirname[match.end(0):]

            for m in re.finditer('[^/]+', dirname):
                s = m.group(0)
                if s == '..' or (s.startswith('.') and not self.fm.settings['show_hidden']):
                    self.fm.cd(s)
                else:
                    ## We force ranger to load content before calling `scout`.
                    self.fm.thisdir.load_content(schedule=False)
                    self.fm.execute_console('scout -ae ^{}$'.format(s))
        else:
            self.fm.notify("file/directory exists!", bad=True)



# Changed that force use "fdfind" instead of get_executables()
class fzf_select(Command):
    """
    :fzf_select
    Find a file using fzf.
    With a prefix argument to select only directories.

    See: https://github.com/junegunn/fzf
    """

    def execute(self):
        import subprocess

        # Debuged for Ranger
        ############ is a dict in for rc.conf ############
        # print(self.fm.settings._settings)  

        ########### is a list for rifle.conf #############
        # print(dir(self.fm.settings.fm.rifle)) 
        # from pathlib import Path
        # f = Path("/mnt/d/debug/debug.txt")

        # from pprint import PrettyPrinter
        # content = self.fm.settings.fm.rifle.rules

        # pp = PrettyPrinter(indent=4, stream=f.open("w"))
        # pp.pprint(content)
        ##################################################
        
        # get_executables is so slowly
            # from ranger.ext.get_executables import get_executables
            # get_executables():
        # so must use fd (I think that if user can install fzf and he must can install fd by himself)

        # print(help(self.fm.mark_in_direction))

        fd = "fdfind"

        hidden = ('--hidden' if self.fm.settings.show_hidden else '')
        exclude = "--no-ignore-vcs --exclude '.git' --exclude '*.py[co]' --exclude '__pycache__'"
        only_directories = ('--type directory' if self.quantifier else '')
        fzf_default_command = '{} --follow {} {} {}'.format(
            fd, hidden, exclude, only_directories
        )

        env = os.environ.copy()
        env['FZF_DEFAULT_COMMAND'] = fzf_default_command

        # you can remap and config your fzf (and your can still use ctrl+n / ctrl+p ...) + preview
        env['FZF_DEFAULT_OPTS'] = '\
        --reverse \
        --bind alt-n:down,alt-p:up,alt-o:backward-delete-char,alt-h:beginning-of-line,alt-l:end-of-line,alt-j:backward-char,alt-k:forward-char,alt-b:backward-word,alt-f:forward-word \
        --height 95% \
        --layout reverse \
        --border \
        --preview "bat --style=numbers --color=always --line-range :500 {}"'

        fzf = self.fm.execute_command('fzf ', env=env, universal_newlines=True, stdout=subprocess.PIPE)
        stdout, _ = fzf.communicate()

        if fzf.returncode == 0:
            selected = os.path.abspath(stdout.strip())
            if os.path.isdir(selected):
                self.fm.cd(selected)
            else:
                self.fm.select_file(selected)


# Reform Multi Select&Mark by fzf
class fzf_mark(Command):
    """
    `:fzf_mark` refer from `:fzf_select`  (But Just in `Current directory and Not Recursion`)
        so just `find` is enough instead of `fdfind`)

    `:fzf_mark` can One/Multi/All Selected & Marked files of current dir that filterd by `fzf extended-search mode` 
        fzf extended-search mode: https://github.com/junegunn/fzf#search-syntax
        eg:    py    'py    .py    ^he    py$    !py    !^py
    In addition:
        there is a delay in using `get_executables` (So I didn't use it)
        so there is no compatible alias.
        but find is builtin command, so you just consider your `fzf` name
    Usage
        :fzf_mark
        
        shortcut in fzf_mark:
            <CTRL-a>      : select all 
            <CTRL-e>      : deselect all 
            <TAB>         : multiple select
            <SHIFT+TAB>   : reverse multiple select
            ...           : and some remap <Alt-key> for movement
    """

    def execute(self):
        from pathlib import Path 
        import os
        import subprocess

        fzf_name = "fzf" 

        hidden = ('-false' if self.fm.settings.show_hidden else r"-path '*/\.*' -prune")
        exclude = r"\( -name '\.git' -o -iname '\.*py[co]' -o -fstype 'dev' -o -fstype 'proc' \) -prune"
        only_directories = ('-type d' if self.quantifier else '')
        fzf_default_command = 'find -L . -mindepth 1 -type d -prune {} -o {} -o {} -print | cut -b3-'.format(
            hidden, exclude, only_directories
        )

        env = os.environ.copy()
        env['FZF_DEFAULT_COMMAND'] = fzf_default_command

        # you can remap and config your fzf (and your can still use ctrl+n / ctrl+p ...) + preview
        env['FZF_DEFAULT_OPTS'] = '\
        --multi \
        --reverse \
        --bind ctrl-a:select-all,ctrl-e:deselect-all,alt-n:down,alt-p:up,alt-o:backward-delete-char,alt-h:beginning-of-line,alt-l:end-of-line,alt-j:backward-char,alt-k:forward-char,alt-b:backward-word,alt-f:forward-word \
        --height 95% \
        --layout reverse \
        --border \
        --preview "bat --style=numbers --color=always --line-range :500 {}"'

        fzf = self.fm.execute_command(fzf_name, env=env, universal_newlines=True, stdout=subprocess.PIPE)
        stdout, _ = fzf.communicate()

        if fzf.returncode == 0:
            filename_list = stdout.strip().split()
            for filename in filename_list:
                self.fm.select_file( str(Path(filename).resolve()) )
                self.fm.mark_files(all=False,toggle=True)


# Extract by WinRAR(WSL-Windows)
from ranger.core.loader import CommandLoader

class extract_here(Command):

    def execute(self):
        """ extract selected files to current directory."""
        def update_obj_path(marked_files):
            for marked_file_obj in marked_files:
                marked_file_obj.path = f'{marked_file_obj.path[5]}:/{marked_file_obj.path[7:]}'
        win_rar = '/mnt/c/Program Files/WinRAR/unRar.exe' #   x -mt8 100.rar  / x -mt8 -ad 100.rar 

        cwd = self.fm.thisdir
        marked_files = tuple(cwd.get_selection())

        def refresh(_):
            cwd = self.fm.get_directory(original_path)
            cwd.load_content()

        update_obj_path(marked_files)
        one_file = marked_files[0]
        cwd = self.fm.thisdir

        original_path = cwd.path
        win_rar_args = ['x', '-mt8']
        win_rar_args += self.line.split()[1:]
        
        self.fm.copy_buffer.clear()

        self.fm.cut_buffer = False
        if len(marked_files) == 1:
            descr = "extracting: " + os.path.basename(one_file.path)
            win_rar_args += ['-ad']
        else:
            win_rar_args += ['-ad']
            descr = "extracting files from: " + os.path.basename(
                one_file.dirname)

        for one_mark_file in marked_files:
            obj = CommandLoader(args=[win_rar] + win_rar_args
                    + [one_mark_file.path], descr=descr,read=True)
            obj.signal_bind('after', refresh)
            self.fm.loader.add(obj)


# Compress by WinRAR(WSL-Windows)
from ranger.core.loader import CommandLoader

class compress(Command):
    def execute(self):
        """ Compress marked files to current directory """

        # temp from wsl-path to windows-path for winrar.exe
        def update_obj_path(marked_files):
            for marked_file_obj in marked_files:
                marked_file_obj.path = f'{marked_file_obj.path[5]}:/{marked_file_obj.path[7:]}'

        def refresh(_):
            cwd = self.fm.get_directory(original_path)
            cwd.load_content()

        cwd = self.fm.thisdir
        marked_files = cwd.get_selection()

        # thread 8
        win_rar_args = ['x', '-mt8']
        win_rar_args += self.line.split()[1:]
        
        update_obj_path(marked_files)
        if not marked_files:
            return

        win_rar = '/mnt/c/Program Files/WinRAR/Rar.exe' #    a -r new_dir.rar 123-12.md 123-12515.py
        original_path = cwd.path

        dst_file_name = self.line.split()[1]
        win_rar_args = ["a", "-r"]
        descr = "compressing files in: " + os.path.basename(dst_file_name)
        obj = CommandLoader(args=[win_rar] + win_rar_args + [dst_file_name] + \
                [os.path.relpath(f.path, cwd.path) for f in marked_files], descr=descr, read=True)

        obj.signal_bind('after', refresh)
        self.fm.loader.add(obj)

    def tab(self, tabnum):
        """ Complete with current folder name """
        import time
        time.sleep(100)
        extension = ['.zip', '.tar.gz', '.rar', '.7z']
        return ['compress ' + os.path.basename(self.fm.thisdir.path) + ext for ext in extension]