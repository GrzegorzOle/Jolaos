"""Okno programu: trzy zakładki, przełączniki, opisy dla nieinformatyka."""

from __future__ import annotations

import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Callable

from . import __version__, i18n, notify, update, winapi
from .guard import last_report
from .heads import GUARD_ID, AuditResult, Head, HeadError, Status, build_heads
from .i18n import t
from .journal import Journal, append_log, data_dir

LICENSE_URL = "https://github.com/GrzegorzOle/Jolaos?tab=MIT-1-ov-file#"

BODY_FONT = ("Segoe UI", 10)
SMALL_FONT = ("Segoe UI", 9)
TITLE_FONT = ("Segoe UI", 11, "bold")
HEADER_FONT = ("Segoe UI", 16, "bold")
MONO_FONT = ("Consolas", 9)
GLYPH_FONT = ("Segoe UI Symbol", 11)

SWITCH_ON = "#16a34a"
SWITCH_OFF = "#dc2626"

THEMES = {
    "light": {
        "page": "#f3f4f6",
        "card": "#ffffff",
        "border": "#e5e7eb",
        "text": "#111827",
        "muted": "#6b7280",
        "accent": "#2563eb",
        "accent_fg": "#ffffff",
        "tab": "#e5e7eb",
        "tab_active": "#ffffff",
        "button": "#e5e7eb",
        "button_hover": "#d1d5db",
        "log_bg": "#111827",
        "log_fg": "#e5e7eb",
        "field": "#ffffff",
        "switch_disabled": "#d1d5db",
        "status": {
            Status.UNKNOWN: "#9ca3af",
            Status.PRESENT: "#dc2626",
            Status.ABSENT: "#16a34a",
            Status.PARTIAL: "#d97706",
            Status.ERROR: "#7c3aed",
        },
    },
    "dark": {
        "page": "#0f172a",
        "card": "#1e293b",
        "border": "#334155",
        "text": "#f1f5f9",
        "muted": "#94a3b8",
        "accent": "#3b82f6",
        "accent_fg": "#ffffff",
        "tab": "#1e293b",
        "tab_active": "#334155",
        "button": "#334155",
        "button_hover": "#475569",
        "log_bg": "#020617",
        "log_fg": "#cbd5e1",
        "field": "#1e293b",
        "switch_disabled": "#475569",
        "status": {
            Status.UNKNOWN: "#94a3b8",
            Status.PRESENT: "#f87171",
            Status.ABSENT: "#4ade80",
            Status.PARTIAL: "#fbbf24",
            Status.ERROR: "#c084fc",
        },
    },
}

C = THEMES["light"]


def set_theme(name: str) -> None:
    global C
    C = THEMES.get(name, THEMES["light"])


def resource_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base / name


# ---------------------------------------------------------------------------
# Drobne widżety


class Switch(tk.Canvas):
    """Przełącznik w stylu suwaka: zielony włączony, czerwony wyłączony."""

    W, H, PAD = 46, 24, 3

    def __init__(self, master, variable: tk.BooleanVar, **kwargs) -> None:
        super().__init__(master, width=self.W, height=self.H, highlightthickness=0,
                         bg=kwargs.pop("bg", C["card"]), cursor="hand2", **kwargs)
        self.variable = variable
        self.enabled = True
        self.bind("<Button-1>", self._toggle)
        self.variable.trace_add("write", lambda *_: self._draw())
        self._draw()

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        self.configure(cursor="hand2" if enabled else "arrow")
        self._draw()

    def _toggle(self, _event=None) -> None:
        if self.enabled:
            self.variable.set(not self.variable.get())

    def _draw(self) -> None:
        self.delete("all")
        on = self.variable.get()
        color = SWITCH_ON if on else SWITCH_OFF
        if not self.enabled:
            color = C["switch_disabled"]
        self._pill(color)
        knob = self.H - 2 * self.PAD
        x = self.W - self.PAD - knob if on else self.PAD
        self.create_oval(x, self.PAD, x + knob, self.PAD + knob, fill="white", outline="white")

    def _pill(self, color: str) -> None:
        r = self.H / 2
        self.create_oval(0, 0, self.H, self.H, fill=color, outline=color)
        self.create_oval(self.W - self.H, 0, self.W, self.H, fill=color, outline=color)
        self.create_rectangle(r, 0, self.W - r, self.H, fill=color, outline=color)


class ThemeToggle(tk.Canvas):
    """Słońce / księżyc: przełącza motyw jasny i ciemny."""

    W, H, PAD = 60, 28, 3

    def __init__(self, master, dark: bool, command: Callable[[bool], None]) -> None:
        super().__init__(master, width=self.W, height=self.H, highlightthickness=0, bg=C["page"], cursor="hand2")
        self.dark = dark
        self.command = command
        self.bind("<Button-1>", self._toggle)
        self._draw()

    def _toggle(self, _event=None) -> None:
        self.dark = not self.dark
        self._draw()
        self.command(self.dark)

    def _draw(self) -> None:
        self.delete("all")
        track = C["border"]
        r = self.H / 2
        self.create_oval(0, 0, self.H, self.H, fill=track, outline=track)
        self.create_oval(self.W - self.H, 0, self.W, self.H, fill=track, outline=track)
        self.create_rectangle(r, 0, self.W - r, self.H, fill=track, outline=track)
        # Na torze ikona trybu, do którego można się przełączyć; na gałce ikona bieżącego.
        if self.dark:
            self.create_text(self.H / 2 + 1, self.H / 2, text="☀", font=GLYPH_FONT, fill=C["muted"])
        else:
            self.create_text(self.W - self.H / 2 - 1, self.H / 2, text="☽", font=GLYPH_FONT, fill=C["muted"])
        knob = self.H - 2 * self.PAD
        x = self.W - self.PAD - knob if self.dark else self.PAD
        self.create_oval(x, self.PAD, x + knob, self.PAD + knob, fill=C["card"], outline=C["muted"])
        glyph, color = ("☽", "#93c5fd") if self.dark else ("☀", "#f59e0b")
        self.create_text(x + knob / 2, self.H / 2, text=glyph, font=GLYPH_FONT, fill=color)


class ScrollFrame(ttk.Frame):
    """Ramka z pionowym paskiem przewijania. Zawartość wkładaj do .inner."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0, bg=C["page"], height=120)
        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vbar.set)
        self.vbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=C["page"])
        self._window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<Enter>", lambda _e: self.canvas.bind_all("<MouseWheel>", self._on_wheel))
        self.canvas.bind("<Leave>", lambda _e: self.canvas.unbind_all("<MouseWheel>"))

    def _on_inner_configure(self, _event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self.canvas.itemconfigure(self._window, width=event.width)

    def _on_wheel(self, event) -> None:
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def clear(self) -> None:
        for child in self.inner.winfo_children():
            child.destroy()


class HeadRow(tk.Frame):
    """Jeden wiersz: przełącznik, tytuł, opis, uwagi i status."""

    def __init__(self, master, head: Head, *, with_switch: bool, initial: bool = True,
                 description: str | None = None, extra: str | None = None) -> None:
        super().__init__(master, bg=C["card"], padx=14, pady=10, highlightbackground=C["border"], highlightthickness=1)
        self.head = head
        self.var = tk.BooleanVar(value=initial)
        self.switch: Switch | None = None

        self.columnconfigure(1, weight=1)
        if with_switch:
            self.switch = Switch(self, self.var)
            self.switch.grid(row=0, column=0, rowspan=3, sticky="n", padx=(0, 14), pady=(2, 0))

        self.title = tk.Label(self, text=head.title, font=TITLE_FONT, bg=C["card"], fg=C["text"], anchor="w")
        self.title.grid(row=0, column=1, sticky="w")
        self.desc = tk.Label(self, text=description or head.description, font=BODY_FONT, bg=C["card"], fg=C["text"],
                             justify="left", anchor="w", wraplength=520)
        self.desc.grid(row=1, column=1, sticky="we", pady=(2, 0))

        notes = [t(n) for n in head.notes]
        if extra:
            notes.append(extra)
        self.notes = tk.Label(self, text="\n".join(notes), font=SMALL_FONT, fg=C["muted"], bg=C["card"],
                              justify="left", anchor="w", wraplength=520)
        if notes:
            self.notes.grid(row=2, column=1, sticky="we", pady=(4, 0))

        self.badge = tk.Frame(self, bg=C["card"])
        self.badge.grid(row=0, column=2, rowspan=3, sticky="ne", padx=(14, 0))
        self.dot = tk.Canvas(self.badge, width=12, height=12, highlightthickness=0, bg=C["card"])
        self.dot.pack(side="left", padx=(0, 6), pady=3)
        self.status = tk.Label(self.badge, font=SMALL_FONT, bg=C["card"], width=22, anchor="w")
        self.status.pack(side="left")

        self.detail = tk.Label(self, text="", font=MONO_FONT, fg=C["muted"], bg=C["card"], justify="left", anchor="w")
        self.set_status(Status.UNKNOWN)
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event) -> None:
        width = max(event.width - 320, 200)
        self.desc.configure(wraplength=width)
        self.notes.configure(wraplength=width)
        self.detail.configure(wraplength=width)

    def set_status(self, status: Status, detail: str = "") -> None:
        color = C["status"][status]
        self.dot.delete("all")
        self.dot.create_oval(1, 1, 11, 11, fill=color, outline=color)
        self.status.configure(text=self.head.status_label(status), fg=color)
        if detail and detail != "-" and status != Status.UNKNOWN:
            self.detail.configure(text=detail)
            self.detail.grid(row=3, column=1, columnspan=2, sticky="we", pady=(6, 0))
        else:
            self.detail.grid_forget()

    def set_enabled(self, enabled: bool) -> None:
        if self.switch:
            self.switch.set_enabled(enabled)


class SettingRow(tk.Frame):
    """Wiersz ustawienia: przełącznik działający od razu, bez przycisku Zastosuj."""

    def __init__(self, master, title: str, description: str, initial: bool, command: Callable[[bool], None]) -> None:
        super().__init__(master, bg=C["card"], padx=14, pady=10, highlightbackground=C["border"], highlightthickness=1)
        self.var = tk.BooleanVar(value=initial)
        self.columnconfigure(1, weight=1)
        Switch(self, self.var).grid(row=0, column=0, rowspan=2, sticky="n", padx=(0, 14), pady=(2, 0))
        tk.Label(self, text=title, font=TITLE_FONT, bg=C["card"], fg=C["text"], anchor="w").grid(row=0, column=1, sticky="w")
        self.desc = tk.Label(self, text=description, font=BODY_FONT, bg=C["card"], fg=C["text"],
                             justify="left", anchor="w", wraplength=520)
        self.desc.grid(row=1, column=1, sticky="we", pady=(2, 0))
        self.var.trace_add("write", lambda *_: command(self.var.get()))
        self.bind("<Configure>", lambda e: self.desc.configure(wraplength=max(e.width - 320, 200)))


# ---------------------------------------------------------------------------
# Główne okno


class App:
    def __init__(self, journal: Journal) -> None:
        self.journal = journal
        self.heads = build_heads()
        self.audit_results: dict[str, AuditResult] = {}
        self.busy = False
        self.events: queue.Queue[Callable[[], None]] = queue.Queue()
        self.theme = journal.get_config("theme", "light")
        set_theme(self.theme)
        self.update_info: update.UpdateInfo | None = None
        self.update_banner: tk.Frame | None = None

        self.root = tk.Tk()
        self.root.title(t("app.title"))
        self.root.geometry("900x720")
        self.root.minsize(760, 560)
        icon = resource_path("build/jolaos.ico")
        if icon.exists():
            try:
                self.root.iconbitmap(str(icon))
            except tk.TclError:
                pass

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.main: ttk.Frame | None = None
        self.build_ui()
        self.root.after(100, self._pump)
        self.root.after(300, self.start_audit)
        if self.journal.get_config(update.CONFIG_KEY, True):
            self.root.after(1500, lambda: self.start_update_check(manual=False))

    # Budowa interfejsu --------------------------------------------------

    def _apply_styles(self) -> None:
        s = self.style
        self.root.configure(bg=C["page"])
        s.configure(".", background=C["page"], foreground=C["text"], font=BODY_FONT,
                    bordercolor=C["border"], lightcolor=C["page"], darkcolor=C["page"])
        s.configure("TFrame", background=C["page"])
        s.configure("TNotebook", background=C["page"], borderwidth=0, tabmargins=(0, 4, 0, 0))
        s.configure("TNotebook.Tab", background=C["tab"], foreground=C["text"], padding=(16, 8), borderwidth=0)
        s.map("TNotebook.Tab", background=[("selected", C["tab_active"])], foreground=[("selected", C["text"])],
              padding=[("selected", (16, 8))])
        s.configure("TButton", background=C["button"], foreground=C["text"], padding=(12, 5), borderwidth=0,
                    focuscolor=C["button"])
        s.map("TButton", background=[("active", C["button_hover"]), ("disabled", C["border"])],
              foreground=[("disabled", C["muted"])])
        s.configure("Accent.TButton", background=C["accent"], foreground=C["accent_fg"], padding=(14, 6))
        s.map("Accent.TButton", background=[("active", C["accent"]), ("disabled", C["border"])],
              foreground=[("disabled", C["muted"])])
        s.configure("TLabelframe", background=C["page"], bordercolor=C["border"])
        s.configure("TLabelframe.Label", background=C["page"], foreground=C["muted"], font=SMALL_FONT)
        s.configure("TPanedwindow", background=C["page"])
        s.configure("Sash", sashthickness=6, gripcount=0, background=C["page"])
        s.configure("Vertical.TScrollbar", background=C["button"], troughcolor=C["page"], bordercolor=C["page"],
                    arrowcolor=C["muted"], lightcolor=C["button"], darkcolor=C["button"])
        s.map("Vertical.TScrollbar", background=[("active", C["button_hover"])])

    def build_ui(self) -> None:
        if self.main is not None:
            self.main.destroy()
        self._apply_styles()
        self.root.title(t("app.title"))
        self._build_menu()

        self.main = ttk.Frame(self.root)
        self.main.pack(fill="both", expand=True)

        header = tk.Frame(self.main, bg=C["page"], padx=18, pady=12)
        header.pack(fill="x")
        titles = tk.Frame(header, bg=C["page"])
        titles.pack(side="left", fill="x", expand=True)
        tk.Label(titles, text=t("app.title"), font=HEADER_FONT, bg=C["page"], fg=C["text"]).pack(anchor="w")
        tk.Label(titles, text=t("app.subtitle"), font=SMALL_FONT, fg=C["muted"], bg=C["page"]).pack(anchor="w")
        ThemeToggle(header, dark=self.theme == "dark", command=self.change_theme).pack(side="right", anchor="n", pady=4)
        self.update_banner = None
        if self.update_info:
            self.show_update_banner(self.update_info)

        bottom = tk.Frame(self.main, bg=C["page"], padx=12, pady=8)
        bottom.pack(side="bottom", fill="x")
        self.log = ScrolledText(bottom, height=6, font=MONO_FONT, state="disabled", relief="flat",
                                bg=C["log_bg"], fg=C["log_fg"], insertbackground=C["log_fg"])
        self.log.pack(fill="x")
        self.status_var = tk.StringVar(value=t("status.ready"))
        tk.Label(bottom, textvariable=self.status_var, font=SMALL_FONT, fg=C["muted"], bg=C["page"], anchor="w").pack(fill="x", pady=(4, 0))

        self.notebook = ttk.Notebook(self.main)
        self.notebook.pack(fill="both", expand=True, padx=12)
        self.tab_audit = ttk.Frame(self.notebook)
        self.tab_disable = ttk.Frame(self.notebook)
        self.tab_restore = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_audit, text=t("tab.audit"))
        self.notebook.add(self.tab_disable, text=t("tab.disable"))
        self.notebook.add(self.tab_restore, text=t("tab.restore"))

        self._build_audit_tab()
        self._build_disable_tab()
        self._build_restore_tab()

        for hid, result in self.audit_results.items():
            self._show_result(hid, result)

    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)
        lang_menu = tk.Menu(menubar, tearoff=0)
        self.lang_var = tk.StringVar(value=i18n.language())
        for code, name in i18n.LANGUAGES.items():
            lang_menu.add_radiobutton(label=name, value=code, variable=self.lang_var, command=self.change_language)
        menubar.add_cascade(label=t("menu.language"), menu=lang_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=t("menu.open_journal"), command=lambda: winapi.open_in_shell(str(data_dir())))
        help_menu.add_command(label=t("menu.license"), command=lambda: winapi.open_in_shell(LICENSE_URL))
        help_menu.add_separator()
        help_menu.add_command(label=t("update.check_now"), command=lambda: self.start_update_check(manual=True))
        self.auto_update_var = tk.BooleanVar(value=bool(self.journal.get_config(update.CONFIG_KEY, True)))
        help_menu.add_checkbutton(label=t("update.auto"), variable=self.auto_update_var,
                                  command=lambda: self.journal.set_config(update.CONFIG_KEY, self.auto_update_var.get()))
        help_menu.add_separator()
        help_menu.add_command(label=t("menu.about"), command=self.show_about)
        menubar.add_cascade(label=t("menu.help"), menu=help_menu)
        self.root.config(menu=menubar)

    def _intro(self, parent, key: str) -> None:
        label = tk.Label(parent, text=t(key), font=BODY_FONT, bg=C["page"], fg=C["text"], justify="left", anchor="w", wraplength=800)
        label.pack(fill="x", padx=4, pady=(12, 8))
        label.bind("<Configure>", lambda e: label.configure(wraplength=max(e.width - 10, 200)))

    def _build_audit_tab(self) -> None:
        self._intro(self.tab_audit, "audit.intro")
        bar = ttk.Frame(self.tab_audit)
        bar.pack(fill="x", padx=4, pady=(0, 8))
        self.btn_audit = ttk.Button(bar, text=t("audit.run"), style="Accent.TButton", command=self.start_audit)
        self.btn_audit.pack(side="left")

        paned = ttk.Panedwindow(self.tab_audit, orient="vertical")
        paned.pack(fill="both", expand=True)
        scroll = ScrollFrame(paned)
        paned.add(scroll, weight=3)
        self.audit_rows: dict[str, HeadRow] = {}
        for head in self.heads:
            row = HeadRow(scroll.inner, head, with_switch=False)
            row.pack(fill="x", padx=4, pady=3)
            self.audit_rows[head.id] = row

        report_frame = ttk.Labelframe(paned, text=t("audit.guard_report"))
        paned.add(report_frame, weight=1)
        self.report_text = ScrolledText(report_frame, height=5, font=MONO_FONT, relief="flat", state="disabled",
                                        bg=C["field"], fg=C["text"], insertbackground=C["text"])
        self.report_text.pack(fill="both", expand=True, padx=6, pady=6)
        self.refresh_report()

    def _build_disable_tab(self) -> None:
        self._intro(self.tab_disable, "disable.intro")
        scroll = ScrollFrame(self.tab_disable)
        scroll.pack(fill="both", expand=True)
        self.disable_rows: dict[str, HeadRow] = {}
        for head in self.heads:
            row = HeadRow(scroll.inner, head, with_switch=True, initial=head.default_on)
            row.pack(fill="x", padx=4, pady=3)
            self.disable_rows[head.id] = row
        SettingRow(
            scroll.inner,
            t("setting.notify.title"),
            t("setting.notify.desc"),
            bool(self.journal.get_config(notify.CONFIG_KEY, True)),
            lambda on: self.journal.set_config(notify.CONFIG_KEY, on),
        ).pack(fill="x", padx=4, pady=3)
        bar = ttk.Frame(self.tab_disable)
        bar.pack(fill="x", padx=4, pady=8)
        self.btn_apply = ttk.Button(bar, text=t("disable.run"), style="Accent.TButton", command=self.start_apply)
        self.btn_apply.pack(side="left")
        self.btn_explorer = ttk.Button(bar, text=t("status.restart_explorer"), command=self.restart_explorer)

    def _build_restore_tab(self) -> None:
        self._intro(self.tab_restore, "restore.intro")
        self.restore_scroll = ScrollFrame(self.tab_restore)
        self.restore_scroll.pack(fill="both", expand=True)
        bar = ttk.Frame(self.tab_restore)
        bar.pack(fill="x", padx=4, pady=8)
        self.btn_restore = ttk.Button(bar, text=t("restore.run"), style="Accent.TButton", command=self.start_restore)
        self.btn_restore.pack(side="left")
        self.restore_rows: dict[str, HeadRow] = {}
        self.refresh_restore_tab()

    def refresh_restore_tab(self) -> None:
        self.restore_scroll.clear()
        self.restore_rows = {}
        applied = [h for h in self.heads if self.journal.has(h.id)]
        if not applied:
            tk.Label(self.restore_scroll.inner, text=t("restore.empty"), font=BODY_FONT, fg=C["muted"], bg=C["page"],
                     justify="left", anchor="w").pack(fill="x", padx=8, pady=12)
            self.btn_restore.state(["disabled"])
            return
        self.btn_restore.state(["!disabled"])
        for head in applied:
            entry = self.journal.get(head.id) or {}
            when = entry.get("applied", "?")
            row = HeadRow(self.restore_scroll.inner, head, with_switch=True, initial=True,
                          description=head.restore_description, extra=t("restore.applied_on", when=when))
            row.pack(fill="x", padx=4, pady=3)
            self.restore_rows[head.id] = row
            result = self.audit_results.get(head.id)
            if result:
                row.set_status(result.status)

    def refresh_report(self) -> None:
        report = last_report() or t("audit.no_report")
        self.report_text.configure(state="normal")
        self.report_text.delete("1.0", "end")
        self.report_text.insert("1.0", report)
        self.report_text.configure(state="disabled")

    # Zdarzenia ----------------------------------------------------------

    def change_language(self) -> None:
        code = self.lang_var.get()
        i18n.set_language(code)
        self.journal.set_config("language", code)
        self.build_ui()

    def change_theme(self, dark: bool) -> None:
        self.theme = "dark" if dark else "light"
        set_theme(self.theme)
        self.journal.set_config("theme", self.theme)
        self.build_ui()

    # Aktualizacje --------------------------------------------------------

    def start_update_check(self, manual: bool) -> None:
        def worker() -> None:
            latest = update.fetch_latest()
            self.post(lambda: self._update_checked(latest, manual))

        threading.Thread(target=worker, daemon=True).start()

    def _update_checked(self, latest: update.UpdateInfo | None, manual: bool) -> None:
        if latest and update.is_newer(latest.version):
            self.update_info = latest
            self.show_update_banner(latest)
            if manual and messagebox.askyesno(
                t("update.title"), t("update.ask_open", version=latest.version, current=__version__), parent=self.root
            ):
                winapi.open_in_shell(latest.download_url)
            return
        if not manual:
            return
        if latest is None:
            messagebox.showwarning(t("update.title"), t("update.error"), parent=self.root)
        else:
            messagebox.showinfo(t("update.title"), t("update.none", current=__version__), parent=self.root)

    def show_update_banner(self, info: update.UpdateInfo) -> None:
        if self.update_banner is not None:
            return
        banner = tk.Frame(self.main, bg=C["accent"], padx=18, pady=8)
        banner.pack(fill="x", after=self.main.winfo_children()[0])
        tk.Label(banner, text=t("update.available", version=info.version, current=__version__),
                 font=BODY_FONT, bg=C["accent"], fg=C["accent_fg"], anchor="w").pack(side="left")
        tk.Button(banner, text=t("update.dismiss"), font=SMALL_FONT, relief="flat", bg=C["accent"], fg=C["accent_fg"],
                  activebackground=C["accent"], activeforeground=C["accent_fg"], cursor="hand2",
                  command=self.hide_update_banner).pack(side="right")
        tk.Button(banner, text=t("update.download"), font=TITLE_FONT, relief="flat", bg=C["card"], fg=C["text"],
                  activebackground=C["card"], activeforeground=C["text"], cursor="hand2", padx=12,
                  command=lambda: winapi.open_in_shell(info.download_url)).pack(side="right", padx=(0, 12))
        self.update_banner = banner

    def hide_update_banner(self) -> None:
        if self.update_banner is not None:
            self.update_banner.destroy()
            self.update_banner = None
        self.update_info = None

    def show_about(self) -> None:
        messagebox.showinfo(t("menu.about"), t("about.text", version=__version__), parent=self.root)

    def restart_explorer(self) -> None:
        subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], capture_output=True, creationflags=winapi.CREATE_NO_WINDOW)
        subprocess.Popen(["explorer.exe"], creationflags=winapi.CREATE_NO_WINDOW)
        self.log_line(t("status.explorer_restarted"))
        self.btn_explorer.pack_forget()

    def log_line(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")
        append_log(text)

    def _pump(self) -> None:
        try:
            while True:
                self.events.get_nowait()()
        except queue.Empty:
            pass
        self.root.after(80, self._pump)

    def post(self, fn: Callable[[], None]) -> None:
        self.events.put(fn)

    def _set_busy(self, busy: bool, status: str | None = None) -> None:
        self.busy = busy
        state = ["disabled"] if busy else ["!disabled"]
        for btn in (self.btn_audit, self.btn_apply):
            btn.state(state)
        if busy:
            self.btn_restore.state(["disabled"])
        else:
            self.refresh_restore_tab()
        for rows in (self.disable_rows, self.restore_rows):
            for row in rows.values():
                row.set_enabled(not busy)
        if status:
            self.status_var.set(status)

    def _guard_busy(self) -> bool:
        if self.busy:
            messagebox.showinfo(t("app.title"), t("msg.busy"), parent=self.root)
            return True
        return False

    def _show_result(self, hid: str, result: AuditResult) -> None:
        for rows in (self.audit_rows, self.disable_rows, self.restore_rows):
            row = rows.get(hid)
            if row:
                row.set_status(result.status, result.detail if rows is self.audit_rows else "")

    # Operacje w tle -----------------------------------------------------

    def start_audit(self) -> None:
        if self._guard_busy():
            return
        self._set_busy(True, t("audit.running"))
        self.log_line(t("log.start_audit"))
        threading.Thread(target=self._audit_worker, args=(list(self.heads),), daemon=True).start()

    def _audit_worker(self, heads: list[Head]) -> None:
        for head in heads:
            try:
                result = head.audit()
            except Exception as exc:  # noqa: BLE001 - audyt nie może zabić okna
                result = AuditResult(Status.ERROR, str(exc))
            self.audit_results[head.id] = result
            self.post(lambda h=head.id, r=result: self._show_result(h, r))
        self.post(lambda: self._set_busy(False, t("status.done")))
        self.post(self.refresh_report)

    def start_apply(self) -> None:
        if self._guard_busy():
            return
        selected = [h for h in self.heads if self.disable_rows[h.id].var.get()]
        if not selected:
            messagebox.showinfo(t("app.title"), t("disable.nothing"), parent=self.root)
            return
        if not messagebox.askyesno(t("disable.confirm_title"), t("disable.confirm", count=len(selected)), parent=self.root):
            return
        # Strażnik zawsze na końcu, żeby pilnował już ściętych głów.
        selected.sort(key=lambda h: h.id == GUARD_ID)
        self._set_busy(True, t("disable.running"))
        self.log_line(t("log.start_apply"))
        threading.Thread(target=self._apply_worker, args=(selected,), daemon=True).start()

    def _apply_worker(self, heads: list[Head]) -> None:
        need_restart = need_relogin = False
        for head in heads:
            try:
                before = head.audit()
                if before.status == Status.ABSENT and not self.journal.has(head.id):
                    self._log_head(head, t("log.skipped_present"))
                    continue
                head.apply(self.journal)
                self._log_head(head, t("log.applied"))
                need_restart |= head.needs_restart
                need_relogin |= head.needs_relogin
            except (HeadError, OSError) as exc:
                self._log_head(head, t("log.failed", error=exc))
            except Exception as exc:  # noqa: BLE001 - jeden błąd nie przerywa reszty
                self._log_head(head, t("log.failed", error=exc))
            try:
                result = head.audit()
            except Exception as exc:  # noqa: BLE001
                result = AuditResult(Status.ERROR, str(exc))
            self.audit_results[head.id] = result
            self.post(lambda h=head.id, r=result: self._show_result(h, r))
        status = t("status.done")
        if need_restart:
            status = t("status.need_restart")
        elif need_relogin:
            status = t("status.need_relogin")
        self.post(lambda: self._set_busy(False, status))
        if need_relogin:
            self.post(lambda: self.btn_explorer.pack(side="left", padx=(10, 0)))

    def start_restore(self) -> None:
        if self._guard_busy():
            return
        selected = [h for h in self.heads if h.id in self.restore_rows and self.restore_rows[h.id].var.get()]
        if not selected:
            messagebox.showinfo(t("app.title"), t("restore.nothing"), parent=self.root)
            return
        if not messagebox.askyesno(t("restore.confirm_title"), t("restore.confirm", count=len(selected)), parent=self.root):
            return
        # Strażnik najpierw, żeby nie ścinał głów, które właśnie przywracamy.
        selected.sort(key=lambda h: h.id != GUARD_ID)
        self._set_busy(True, t("restore.running"))
        self.log_line(t("log.start_restore"))
        threading.Thread(target=self._restore_worker, args=(selected,), daemon=True).start()

    def _restore_worker(self, heads: list[Head]) -> None:
        need_restart = need_relogin = False
        for head in heads:
            try:
                head.restore(self.journal)
                self._log_head(head, t("log.restored"))
                need_restart |= head.needs_restart
                need_relogin |= head.needs_relogin
            except Exception as exc:  # noqa: BLE001 - jeden błąd nie przerywa reszty
                self._log_head(head, t("log.failed", error=exc))
            try:
                result = head.audit()
            except Exception as exc:  # noqa: BLE001
                result = AuditResult(Status.ERROR, str(exc))
            self.audit_results[head.id] = result
            self.post(lambda h=head.id, r=result: self._show_result(h, r))
        status = t("status.done")
        if need_restart:
            status = t("status.need_restart")
        elif need_relogin:
            status = t("status.need_relogin")
        self.post(lambda: self._set_busy(False, status))
        if need_relogin:
            self.post(lambda: self.btn_explorer.pack(side="left", padx=(10, 0)))

    def _log_head(self, head: Head, text: str) -> None:
        self.post(lambda: self.log_line(t("log.head", title=head.title, text=text)))

    def run(self) -> None:
        self.root.mainloop()


def run_gui(journal: Journal) -> int:
    App(journal).run()
    return 0
