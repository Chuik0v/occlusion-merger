#!/usr/bin/env python3
"""
İki occlusion.ymap.xml (CodeWalker XML) dosyasını karşılaştırır.
Sadece İKİSİNDE DE bulunan kayıtları (boxOccluders + occludeModels) tutar,
yalnızca birinde olanları siler ve sonucu tek dosyaya yazar.

Kullanım:
    python occlusion_merge.py occlusion1.ymap.xml occlusion2.ymap.xml occlusion3.ymap.xml

Gereksinim: Python 3.9+
"""
import sys
import xml.etree.ElementTree as ET

SECTIONS = ("boxOccluders", "occludeModels")


def sig(el):
    """Bir elementin içeriğine göre karşılaştırılabilir imza üretir."""
    text = "".join((el.text or "").split())  # boşluk/satır farklarını yok say
    attrs = tuple(sorted(el.attrib.items()))
    kids = tuple(sig(c) for c in el)
    return (el.tag, attrs, text, kids)


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    path1, path2, out_path = sys.argv[1:]
    tree1, tree2 = ET.parse(path1), ET.parse(path2)
    root1, root2 = tree1.getroot(), tree2.getroot()

    for section in SECTIONS:
        node1, node2 = root1.find(section), root2.find(section)
        items1 = list(node1) if node1 is not None else []
        items2 = list(node2) if node2 is not None else []

        sigs1 = [sig(e) for e in items1]
        set1, set2 = set(sigs1), {sig(e) for e in items2}
        common = set1 & set2

        print(f"[{section}]")
        print(f"  Dosya 1: {len(set1)} | Dosya 2: {len(set2)} | Ortak: {len(common)}")
        print(f"  Sadece 1'de olan (silinecek): {len(set1 - set2)}")
        print(f"  Sadece 2'de olan (silinecek): {len(set2 - set1)}")

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

    ET.indent(tree1, space="  ")
    tree1.write(out_path, encoding="UTF-8", xml_declaration=True)
    print(f"\nTamamlandı -> {out_path}")


if __name__ == "__main__":
    main()
