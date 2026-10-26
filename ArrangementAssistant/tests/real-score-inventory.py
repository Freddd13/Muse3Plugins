"""Print independent XML counts for the optional native real-score check."""
from collections import Counter
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile


def inventory(path):
    source = Path(path).read_bytes()
    if source.startswith(b"PK"):
        with ZipFile(BytesIO(source)) as archive:
            container = ET.fromstring(archive.read("META-INF/container.xml"))
            member = container.find(".//rootfile").attrib["full-path"]
            document = ET.fromstring(archive.read(member))
    else:
        document = ET.fromstring(source)
    score = document.find("Score")
    staffs = score.findall("Staff")
    notes = [note for staff in staffs for note in staff.iter("Note")]
    fingers = [finger.text or "" for note in notes for finger in note.findall("Fingering/text")]
    hands = [symbol for staff in staffs for symbol in staff.iter("Symbol")
             if (symbol.findtext("name") or "").startswith("keyboardPlayWith")]
    return {"sha256": sha256(source).hexdigest(), "notes": len(notes),
            "hands": len(hands), "fingerings": len(fingers), "fingerTexts": dict(Counter(fingers))}


if __name__ == "__main__":
    print(json.dumps(inventory(sys.argv[1]), ensure_ascii=False, indent=2))
