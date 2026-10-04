#!/usr/bin/env python3
"""
Occlusion Birleştirici (masaüstü uygulaması)

İki occlusion.ymap.xml (CodeWalker XML) dosyasında sadece ORTAK olan kayıtları
(boxOccluders + occludeModels) tutar, birinde olup diğerinde olmayanları siler.
"""
import threading
import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox, ttk

SECTIONS = ("boxOccluders", "occludeModels")


def sig(el):
    """Elementin içeriğine göre karşılaştırılabilir imza üretir."""
    text = "".join((el.text or "").split())
    attrs = tuple(sorted(el.attrib.items()))
    return (el.tag, attrs, text, tuple(sig(c) for c in el))


def merge(path1, path2):
    """İki dosyanın ortak kayıtlarını döndürür: (tree, rapor_satırları, uyarı)."""
    tree1, tree2 = ET.parse(path1), ET.parse(path2)
    root1, root2 = tree1.getroot(), tree2.getroot()
    lines, found = [], False
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

        lines.append(f"[{section}]")
        lines.append(f"  Dosya 1: {len(set1)}   Dosya 2: {len(set2)}   Ortak: {len(common)}")
        lines.append(f"  1'den silinecek: {len(set1 - set2)}   2'den silinecek: {len(set2 - set1)}")
        lines.append("")

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
        raise ValueError(
            "Dosyalarda boxOccluders / occludeModels bölümü bulunamadı.\n"
            "Bunlar occlusion ymap XML dosyaları mı?"
        )
    warn = ""
    if common_total == 0 and items_total > 0:
        warn = "UYARI: Hiç ortak kayıt yok. Dosyalar yanlış seçilmiş olabilir."
    ET.indent(tree1, space="  ")
    return tree1, lines, warn


class App:
    def __init__(self, root):
        self.root = root
        self.result = None
        root.title("Occlusion Birleştirici")
        root.geometry("640x460")
        root.minsize(520, 380)

        frm = ttk.Frame(root, padding=14)
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(4, weight=1)

        self.p1, self.p2 = tk.StringVar(), tk.StringVar()
        for row, (label, var) in enumerate((("1. Occlusion:", self.p1), ("2. Occlusion:", self.p2))):
            ttk.Label(frm, text=label).grid(row=row, column=0, sticky="w", pady=4)
            ttk.Entry(frm, textvariable=var).grid(row=row, column=1, sticky="ew", padx=8)
            ttk.Button(frm, text="Seç...", command=lambda v=var: self.pick(v)).grid(row=row, column=2)

        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, columnspan=3, sticky="w", pady=10)
        self.go = ttk.Button(btns, text="Birleştir", command=self.run)
        self.go.pack(side="left")
        self.save = ttk.Button(btns, text="Kaydet...", command=self.save_file, state="disabled")
        self.save.pack(side="left", padx=8)

        self.status = ttk.Label(frm, text="İki XML dosyasını seç.")
        self.status.grid(row=3, column=0, columnspan=3, sticky="w")

        self.log = tk.Text(frm, height=12, state="disabled", font=("Consolas", 10), wrap="none")
        self.log.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=(6, 0))

    def pick(self, var):
        path = filedialog.askopenfilename(
            title="Occlusion XML seç",
            filetypes=[("XML dosyaları", "*.xml"), ("Tüm dosyalar", "*.*")],
        )
        if path:
            var.set(path)

    def write_log(self, text):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.insert("end", text)
        self.log.configure(state="disabled")

    def run(self):
        a, b = self.p1.get().strip(), self.p2.get().strip()
        if not a or not b:
            messagebox.showwarning("Eksik dosya", "Önce iki dosyayı da seç.")
            return
        self.go.configure(state="disabled")
        self.save.configure(state="disabled")
        self.status.configure(text="İşleniyor, büyük dosyalarda biraz sürebilir...")
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
            self.status.configure(text="Hata oluştu.")
            self.write_log(str(err))
            messagebox.showerror("Hata", str(err))
            return
        tree, lines, warn = out
        self.result = tree
        self.write_log("\n".join(lines) + ("\n" + warn if warn else ""))
        self.status.configure(text="Hazır. Sonucu kaydetmek için 'Kaydet...' butonuna bas.")
        self.save.configure(state="normal")

    def save_file(self):
        if self.result is None:
            return
        path = filedialog.asksaveasfilename(
            title="Sonucu kaydet",
            initialfile="occlusion3.ymap.xml",
            defaultextension=".xml",
            filetypes=[("XML dosyaları", "*.xml")],
        )
        if not path:
            return
        self.result.write(path, encoding="UTF-8", xml_declaration=True)
        self.status.configure(text=f"Kaydedildi: {path}")
        messagebox.showinfo("Tamam", "Dosya kaydedildi.")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
