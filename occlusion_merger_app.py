#!/usr/bin/env python3
"""
Occlusion Merger (desktop app, English / Türkçe)

Keeps only the entries that exist in BOTH occlusion.ymap.xml files
(boxOccluders + occludeModels) and removes the ones found in only one of them.
"""
import ctypes
import threading
import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox, ttk

SECTIONS = ("boxOccluders", "occludeModels")

TEXTS = {
    "en": {
        "title": "Occlusion Merger",
        "language": "Language:",
        "file1": "Occlusion 1:",
        "file2": "Occlusion 2:",
        "browse": "Browse...",
        "merge": "Merge",
        "save": "Save...",
        "st_ready": "Select two XML files.",
        "st_working": "Working, this may take a while for large files...",
        "st_done": "Done. Click 'Save...' to store the result.",
        "st_error": "An error occurred.",
        "st_saved": "Saved: {}",
        "pick_title": "Select occlusion XML",
        "xml_files": "XML files",
        "all_files": "All files",
        "missing_title": "Missing file",
        "missing_msg": "Select both files first.",
        "err_title": "Error",
        "no_sections": "Could not find boxOccluders / occludeModels sections in the files.\n"
                       "Are these occlusion ymap XML files?",
        "save_title": "Save result",
        "ok_title": "Done",
        "ok_msg": "File saved.",
        "rep_counts": "  File 1: {}   File 2: {}   Common: {}",
        "rep_removed": "  Removed from 1: {}   Removed from 2: {}",
        "warn_none": "WARNING: No common entries found. You may have selected the wrong files.",
    },
    "tr": {
        "title": "Occlusion Birleştirici",
        "language": "Dil:",
        "file1": "1. Occlusion:",
        "file2": "2. Occlusion:",
        "browse": "Seç...",
        "merge": "Birleştir",
        "save": "Kaydet...",
        "st_ready": "İki XML dosyasını seç.",
        "st_working": "İşleniyor, büyük dosyalarda biraz sürebilir...",
        "st_done": "Hazır. Sonucu kaydetmek için 'Kaydet...' butonuna bas.",
        "st_error": "Hata oluştu.",
        "st_saved": "Kaydedildi: {}",
        "pick_title": "Occlusion XML seç",
        "xml_files": "XML dosyaları",
        "all_files": "Tüm dosyalar",
        "missing_title": "Eksik dosya",
        "missing_msg": "Önce iki dosyayı da seç.",
        "err_title": "Hata",
        "no_sections": "Dosyalarda boxOccluders / occludeModels bölümü bulunamadı.\n"
                       "Bunlar occlusion ymap XML dosyaları mı?",
        "save_title": "Sonucu kaydet",
        "ok_title": "Tamam",
        "ok_msg": "Dosya kaydedildi.",
        "rep_counts": "  Dosya 1: {}   Dosya 2: {}   Ortak: {}",
        "rep_removed": "  1'den silinen: {}   2'den silinen: {}",
        "warn_none": "UYARI: Hiç ortak kayıt yok. Dosyalar yanlış seçilmiş olabilir.",
    },
}

LANG_NAMES = {"English": "en", "Türkçe": "tr"}


class NoSectionsError(Exception):
    """The files contain neither boxOccluders nor occludeModels."""


def detect_lang():
    """Return 'tr' if the Windows UI language is Turkish, otherwise 'en'."""
    try:
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        return "tr" if (lang_id & 0xFF) == 0x1F else "en"
    except Exception:  # not Windows, or the call failed
        return "en"


def sig(el):
    """Build a comparable signature from an element's content."""
    text = "".join((el.text or "").split())
    attrs = tuple(sorted(el.attrib.items()))
    return (el.tag, attrs, text, tuple(sig(c) for c in el))


def merge(path1, path2):
    """Return (merged_tree, stats, no_common_entries).

    stats: list of (section, count1, count2, common, only_in_1, only_in_2)
    """
    tree1, tree2 = ET.parse(path1), ET.parse(path2)
    root1, root2 = tree1.getroot(), tree2.getroot()
    stats, found = [], False
    common_total = items_total = 0

    for section in SECTIONS:
        node1, node2 = root1.find(section), root2.find(section)
        items1 = list(node1) if node1 is not None else []
        items2 = list(node2) if node2 is not None else []
        if node1 is not None or node2 is not None:
            found = True

        sigs1 = [sig(e) for e in items1]
        set1, set2 = set(sigs1), {sig(e) for e in items2}
        common = set1 & set2
        common_total += len(common)
        items_total += len(set1) + len(set2)
        stats.append((section, len(set1), len(set2), len(common),
                      len(set1 - set2), len(set2 - set1)))

        if node1 is None:
            continue
        kept, seen = [], set()
        for el, s in zip(items1, sigs1):
            if s in common and s not in seen:
                seen.add(s)
                kept.append(el)
        for el in list(node1):
            node1.remove(el)
        node1.extend(kept)

    if not found:
        raise NoSectionsError()
    ET.indent(tree1, space="  ")
    return tree1, stats, (common_total == 0 and items_total > 0)


class App:
    def __init__(self, root):
        self.root = root
        self.lang = detect_lang()
        self.result = None
        self.stats = None
        self.no_common = False
        self.err_key = None
        self.err_raw = None
        self.status = ("st_ready", ())

        root.geometry("640x470")
        root.minsize(520, 390)

        frm = ttk.Frame(root, padding=14)
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(5, weight=1)

        # Language selector
        top = ttk.Frame(frm)
        top.grid(row=0, column=0, columnspan=3, sticky="e", pady=(0, 8))
        self.lbl_lang = ttk.Label(top)
        self.lbl_lang.pack(side="left", padx=(0, 6))
        self.lang_box = ttk.Combobox(top, values=list(LANG_NAMES), state="readonly", width=10)
        self.lang_box.set([n for n, c in LANG_NAMES.items() if c == self.lang][0])
        self.lang_box.pack(side="left")
        self.lang_box.bind("<<ComboboxSelected>>", self.on_lang_change)

        # File pickers
        self.p1, self.p2 = tk.StringVar(), tk.StringVar()
        self.file_labels, self.browse_btns = [], []
        for row, var in ((1, self.p1), (2, self.p2)):
            lbl = ttk.Label(frm)
            lbl.grid(row=row, column=0, sticky="w", pady=4)
            ttk.Entry(frm, textvariable=var).grid(row=row, column=1, sticky="ew", padx=8)
            btn = ttk.Button(frm, command=lambda v=var: self.pick(v))
            btn.grid(row=row, column=2)
            self.file_labels.append(lbl)
            self.browse_btns.append(btn)

        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=3, sticky="w", pady=10)
        self.go = ttk.Button(btns, command=self.run)
        self.go.pack(side="left")
        self.save = ttk.Button(btns, command=self.save_file, state="disabled")
        self.save.pack(side="left", padx=8)

        self.status_lbl = ttk.Label(frm)
        self.status_lbl.grid(row=4, column=0, columnspan=3, sticky="w")

        self.log = tk.Text(frm, height=12, state="disabled", font=("Consolas", 10), wrap="none")
        self.log.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(6, 0))

        self.apply_lang()

    # ---- translation helpers ----
    def t(self, key, *args):
        s = TEXTS[self.lang][key]
        return s.format(*args) if args else s

    def set_status(self, key, *args):
        self.status = (key, args)
        self.status_lbl.configure(text=self.t(key, *args))

    def on_lang_change(self, _event=None):
        self.lang = LANG_NAMES[self.lang_box.get()]
        self.apply_lang()

    def apply_lang(self):
        self.root.title(self.t("title"))
        self.lbl_lang.configure(text=self.t("language"))
        self.file_labels[0].configure(text=self.t("file1"))
        self.file_labels[1].configure(text=self.t("file2"))
        for btn in self.browse_btns:
            btn.configure(text=self.t("browse"))
        self.go.configure(text=self.t("merge"))
        self.save.configure(text=self.t("save"))
        key, args = self.status
        self.status_lbl.configure(text=self.t(key, *args))
        self.render_log()

    # ---- log ----
    def write_log(self, text):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.insert("end", text)
        self.log.configure(state="disabled")

    def render_log(self):
        if self.err_key or self.err_raw:
            text = self.t(self.err_key) if self.err_key else self.err_raw
        elif self.stats is not None:
            lines = []
            for name, n1, n2, common, o1, o2 in self.stats:
                lines += [f"[{name}]", self.t("rep_counts", n1, n2, common),
                          self.t("rep_removed", o1, o2), ""]
            if self.no_common:
                lines.append(self.t("warn_none"))
            text = "\n".join(lines)
        else:
            text = ""
        self.write_log(text)

    # ---- actions ----
    def pick(self, var):
        path = filedialog.askopenfilename(
            title=self.t("pick_title"),
            filetypes=[(self.t("xml_files"), "*.xml"), (self.t("all_files"), "*.*")],
        )
        if path:
            var.set(path)

    def run(self):
        a, b = self.p1.get().strip(), self.p2.get().strip()
        if not a or not b:
            messagebox.showwarning(self.t("missing_title"), self.t("missing_msg"))
            return
        self.result = self.stats = self.err_key = self.err_raw = None
        self.render_log()
        self.go.configure(state="disabled")
        self.save.configure(state="disabled")
        self.set_status("st_working")
        threading.Thread(target=self.work, args=(a, b), daemon=True).start()

    def work(self, a, b):
        try:
            out = merge(a, b)
            self.root.after(0, self.done, out, None)
        except Exception as e:  # noqa: BLE001
            self.root.after(0, self.done, None, e)

    def done(self, out, err):
        self.go.configure(state="normal")
        if err:
            if isinstance(err, NoSectionsError):
                self.err_key = "no_sections"
                msg = self.t("no_sections")
            else:
                self.err_raw = str(err)
                msg = self.err_raw
            self.set_status("st_error")
            self.render_log()
            messagebox.showerror(self.t("err_title"), msg)
            return
        self.result, self.stats, self.no_common = out
        self.render_log()
        self.set_status("st_done")
        self.save.configure(state="normal")

    def save_file(self):
        if self.result is None:
            return
        path = filedialog.asksaveasfilename(
            title=self.t("save_title"),
            initialfile="occlusion3.ymap.xml",
            defaultextension=".xml",
            filetypes=[(self.t("xml_files"), "*.xml")],
        )
        if not path:
            return
        self.result.write(path, encoding="UTF-8", xml_declaration=True)
        self.set_status("st_saved", path)
        messagebox.showinfo(self.t("ok_title"), self.t("ok_msg"))


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
