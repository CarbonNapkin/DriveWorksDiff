"""
Simple Tkinter GUI for the DriveWorks comparison tool.

Lets the user pick two projects (folders or .driveprojx files), choose an
output path, and run a comparison without using the command line.
"""

from __future__ import annotations

import queue
import sys
import threading
import traceback
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import Tk, StringVar, BooleanVar, END, DISABLED, NORMAL, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from ._version import __version__, __author__, __url__, __license__
from .parsers import load_project
from .report import generate_html_report
from .update_check import check_for_update, RELEASES_PAGE

try:
    from .__main__ import resolve_input, cleanup_temp_dirs
except ImportError:
    resolve_input = None  # type: ignore
    cleanup_temp_dirs = None  # type: ignore


PROJX_FILETYPES = [('DriveWorks project', '*.driveprojx'), ('All files', '*.*')]
APP_TITLE = f'DriveWorks Project Compare {__version__}'


class _QueueWriter:
    """File-like object that pushes writes onto a queue."""

    def __init__(self, q: queue.Queue):
        self._q = q

    def write(self, s: str) -> int:
        if s:
            self._q.put(s)
        return len(s)

    def flush(self) -> None:
        pass


class CompareApp:
    def __init__(self, root: Tk):
        self.root = root
        root.title(APP_TITLE)
        root.geometry('720x520')
        self._build_menu()

        self.old_path = StringVar()
        self.new_path = StringVar()
        self.output_path = StringVar(value='dw_comparison.html')
        self.open_in_browser = BooleanVar(value=True)

        self._log_queue: queue.Queue[str] = queue.Queue()
        self._worker: threading.Thread | None = None

        self._build_ui()
        self._drain_log()
        threading.Thread(target=self._check_updates, daemon=True).start()

    def _build_menu(self) -> None:
        """Standard menubar with Help. Integrates with the macOS global menu
        automatically. The File menu carries only Quit so the keyboard
        shortcut shows up where users expect it."""
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label='Quit', accelerator='Cmd+Q' if sys.platform == 'darwin' else 'Ctrl+Q',
                              command=self.root.destroy)
        menubar.add_cascade(label='File', menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=False, name='help')
        help_menu.add_command(label='Open Documentation', command=self._open_docs)
        help_menu.add_separator()
        help_menu.add_command(label='About DriveWorks Project Compare', command=self._show_about)
        menubar.add_cascade(label='Help', menu=help_menu)

        self.root.config(menu=menubar)

    def _open_docs(self) -> None:
        webbrowser.open(__url__)

    def _show_about(self) -> None:
        """Custom About window. messagebox.showinfo works but a Toplevel
        gives us a clickable repo link and slightly nicer typography."""
        top = tk.Toplevel(self.root)
        top.title('About')
        top.resizable(False, False)
        bg = '#f4f4f4'
        top.configure(bg=bg)

        pad = {'padx': 16, 'pady': 4}
        tk.Label(top, text='DriveWorks Project Compare', bg=bg,
                 font=('TkDefaultFont', 14, 'bold')).pack(**pad, anchor='w')
        tk.Label(top, text=f'Version {__version__}', bg=bg).pack(padx=16, pady=(0, 8), anchor='w')
        tk.Label(top, text=f'© {__author__}', bg=bg).pack(padx=16, anchor='w')
        tk.Label(top, text=f'Licensed under {__license__}', bg=bg, fg='#555').pack(padx=16, anchor='w')

        link = tk.Label(top, text=__url__, bg=bg, fg='#3f51b5', cursor='hand2')
        link.pack(padx=16, pady=(8, 4), anchor='w')
        link.bind('<Button-1>', lambda _e: webbrowser.open(__url__))

        tk.Button(top, text='Close', command=top.destroy).pack(pady=(8, 12))

        # Center the dialog over the main window.
        top.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - top.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - top.winfo_height()) // 3
        top.geometry(f'+{max(0, x)}+{max(0, y)}')
        top.transient(self.root)
        top.grab_set()

    def _build_ui(self) -> None:
        # Plain tk widgets (not ttk) because ttk + Tk 8.5 on modern macOS often
        # renders as an empty / black frame. tk widgets are uglier but draw.
        pad = {'padx': 8, 'pady': 6}
        bg = '#f4f4f4'
        self.root.configure(bg=bg)

        frm = tk.Frame(self.root, bg=bg, padx=12, pady=12)
        frm.pack(fill='both', expand=True)

        def label(text, **kw):
            return tk.Label(frm, text=text, bg=bg, anchor='w', **kw)

        def entry(var):
            return tk.Entry(frm, textvariable=var, highlightthickness=1, relief='solid', bd=1)

        def button(text, cmd):
            return tk.Button(frm, text=text, command=cmd, highlightthickness=0)

        label('Old project:').grid(row=0, column=0, sticky='w', **pad)
        entry(self.old_path).grid(row=0, column=1, sticky='ew', **pad)
        button('File…', lambda: self._pick_file(self.old_path)).grid(row=0, column=2, **pad)
        button('Folder…', lambda: self._pick_folder(self.old_path)).grid(row=0, column=3, **pad)

        label('New project:').grid(row=1, column=0, sticky='w', **pad)
        entry(self.new_path).grid(row=1, column=1, sticky='ew', **pad)
        button('File…', lambda: self._pick_file(self.new_path)).grid(row=1, column=2, **pad)
        button('Folder…', lambda: self._pick_folder(self.new_path)).grid(row=1, column=3, **pad)

        label('Output HTML:').grid(row=2, column=0, sticky='w', **pad)
        entry(self.output_path).grid(row=2, column=1, sticky='ew', **pad)
        button('Save as…', self._pick_output).grid(row=2, column=2, columnspan=2, sticky='ew', **pad)

        tk.Checkbutton(
            frm, text='Open report in browser when done',
            variable=self.open_in_browser, bg=bg, anchor='w',
            highlightthickness=0,
        ).grid(row=3, column=1, sticky='w', **pad)

        self.compare_btn = tk.Button(
            frm, text='Compare', command=self._on_compare,
            highlightthickness=0, font=('TkDefaultFont', 13, 'bold'),
        )
        self.compare_btn.grid(row=3, column=2, columnspan=2, sticky='ew', **pad)

        label('Log:').grid(row=4, column=0, sticky='nw', **pad)
        self.log_box = ScrolledText(frm, height=14, wrap='word', state=DISABLED, bd=1, relief='solid')
        self.log_box.grid(row=4, column=1, columnspan=3, sticky='nsew', **pad)

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(4, weight=1)

        # Filled by a background update check (notify-only; see _check_updates).
        self.update_label = tk.Label(frm, text='', bg=bg, fg='#3f51b5', anchor='w', cursor='hand2')
        self.update_label.grid(row=5, column=1, columnspan=3, sticky='w', padx=8, pady=(0, 6))

    def _pick_file(self, target: StringVar) -> None:
        path = filedialog.askopenfilename(
            title='Select project file',
            filetypes=PROJX_FILETYPES,
        )
        if path:
            target.set(path)

    def _pick_folder(self, target: StringVar) -> None:
        path = filedialog.askdirectory(title='Select project folder')
        if path:
            target.set(path)

    def _pick_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title='Save report as',
            defaultextension='.html',
            initialfile=self.output_path.get() or 'dw_comparison.html',
            filetypes=[('HTML', '*.html'), ('All files', '*.*')],
        )
        if path:
            self.output_path.set(path)

    def _log(self, msg: str) -> None:
        self.log_box.configure(state=NORMAL)
        self.log_box.insert(END, msg)
        self.log_box.see(END)
        self.log_box.configure(state=DISABLED)

    def _drain_log(self) -> None:
        try:
            while True:
                self._log(self._log_queue.get_nowait())
        except queue.Empty:
            pass
        self.root.after(80, self._drain_log)

    def _on_compare(self) -> None:
        if self._worker and self._worker.is_alive():
            return

        old_raw = self.old_path.get().strip()
        new_raw = self.new_path.get().strip()
        out_raw = self.output_path.get().strip() or 'dw_comparison.html'

        if not old_raw or not new_raw:
            messagebox.showwarning('Missing input', 'Pick both an old and a new project.')
            return

        old = Path(old_raw)
        new = Path(new_raw)
        if not old.exists():
            messagebox.showerror('Not found', f'Old project not found:\n{old}')
            return
        if not new.exists():
            messagebox.showerror('Not found', f'New project not found:\n{new}')
            return

        output = Path(out_raw)
        open_browser = self.open_in_browser.get()

        # Clear log and disable button
        self.log_box.configure(state=NORMAL)
        self.log_box.delete('1.0', END)
        self.log_box.configure(state=DISABLED)
        self.compare_btn.configure(state=DISABLED, text='Comparing…')

        self._worker = threading.Thread(
            target=self._run_compare,
            args=(old, new, output, open_browser),
            daemon=True,
        )
        self._worker.start()

    def _run_compare(self, old: Path, new: Path, output: Path, open_browser: bool) -> None:
        writer = _QueueWriter(self._log_queue)
        prev_stdout = sys.stdout
        sys.stdout = writer
        try:
            old_name = old.stem if old.suffix.lower() == '.driveprojx' else old.name
            new_name = new.stem if new.suffix.lower() == '.driveprojx' else new.name

            old_folder = resolve_input(old) if resolve_input else old
            new_folder = resolve_input(new) if resolve_input else new

            if not old_folder.is_dir():
                raise ValueError(f'{old} is not a directory or .driveprojx file')
            if not new_folder.is_dir():
                raise ValueError(f'{new} is not a directory or .driveprojx file')

            print(f'Loading old project: {old_name}')
            old_proj = load_project(old_folder)

            print(f'Loading new project: {new_name}')
            new_proj = load_project(new_folder)

            print('Generating comparison report...')
            html = generate_html_report(old_proj, new_proj, old_name, new_name)

            output.write_text(html, encoding='utf-8')
            print(f'Report saved to: {output.resolve()}')

            if open_browser:
                webbrowser.open(f'file://{output.resolve()}')
        except Exception as e:
            print('\nERROR: ' + str(e))
            print(traceback.format_exc())
        finally:
            sys.stdout = prev_stdout
            if cleanup_temp_dirs:
                cleanup_temp_dirs()  # remove .driveprojx extractions from this run
            self.root.after(0, self._on_done)

    def _on_done(self) -> None:
        self.compare_btn.configure(state=NORMAL, text='Compare')

    def _check_updates(self) -> None:
        """Free, fail-silent update check; runs off the UI thread on launch."""
        newer = check_for_update()
        if newer:
            try:
                self.root.after(0, lambda: self._show_update(newer))
            except Exception:
                pass  # window already closed

    def _show_update(self, newer: str) -> None:
        self.update_label.configure(text=f'⬆ Update available: v{newer} — click to download')
        self.update_label.bind('<Button-1>', lambda _e: webbrowser.open(RELEASES_PAGE))


def main() -> None:
    root = Tk()
    CompareApp(root)
    # On macOS a Tk window launched from a Terminal child process opens behind
    # everything else. Force it to the front, then drop the topmost flag so the
    # user can still move other windows on top of it normally.
    root.lift()
    root.attributes('-topmost', True)
    root.after(300, lambda: root.attributes('-topmost', False))
    try:
        root.focus_force()
    except Exception:
        pass
    root.mainloop()


if __name__ == '__main__':
    main()
