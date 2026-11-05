"""Extract the A-J SQL blocks from the Gold/Warehouse Word guide.

This reads the DOCX as OOXML and never executes its SQL. Each output keeps the
guide's exact paragraph text and order, with a source comment for review.
"""

import ast
import json
from pathlib import Path
import re
from xml.etree import ElementTree
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/source/Gold_Warehouse_Huong_dan_chi_tiet (3).docx"
OUTPUT = ROOT / "fabric/sql/gold"
NOTEBOOK_OUTPUT = ROOT / "fabric/notebooks"
BLOCKS = ("A", "B", "C", "D", "E", "F", "G", "H", "J")
NAMES = {
    "A": "source_adapters",
    "B": "gold_tables",
    "C": "policy_draft",
    "D": "silver_manifest",
    "E": "business_views",
    "F": "report_tables",
    "G": "load_gold",
    "H": "publish_forecast",
    "J": "approve_policy",
}


def paragraphs_from_docx(path: Path) -> list[str]:
    with ZipFile(path) as archive:
        document = ElementTree.fromstring(archive.read("word/document.xml"))
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []
    for paragraph in document.findall(".//w:p", ns):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", ns))
        paragraphs.append(text)
    return paragraphs


def extract_blocks(paragraphs: list[str]) -> dict[str, list[str]]:
    blocks: dict[str, list[str]] = {}
    active = None
    for line in paragraphs:
        start = re.fullmatch(r"-- BEGIN ([A-J])", line.strip())
        end = re.fullmatch(r"-- END ([A-J])", line.strip())
        if start:
            name = start.group(1)
            if active is not None or name in blocks or name not in BLOCKS:
                raise ValueError(f"Unexpected block start: {line}")
            blocks[name] = [line]
            active = name
        elif end:
            name = end.group(1)
            if active != name:
                raise ValueError(f"Unexpected block end: {line}")
            blocks[name].append(line)
            active = None
        elif active is not None:
            blocks[active].append(line)
    if active is not None or set(blocks) != set(BLOCKS):
        raise ValueError(f"Incomplete SQL blocks: {sorted(blocks)}; active={active}")
    return blocks


def extract_notebook_cells(paragraphs: list[str], notebook: str, count: int) -> list[str]:
    section_start = next(
        i for i, line in enumerate(paragraphs)
        if line.startswith(f"9 Notebook Train") and notebook == "train"
        or line.startswith(f"11 Notebook Score") and notebook == "score"
    )
    cells = []
    for number in range(1, count + 1):
        heading = re.compile(rf"Cell {number} .+")
        start = next(
            i for i in range(section_start + 1, len(paragraphs))
            if heading.fullmatch(paragraphs[i].strip())
        )
        if not paragraphs[start + 1].startswith("Nơi dán:"):
            raise ValueError(f"Missing notebook instruction after {notebook} cell {number}")
        end = next(
            i for i in range(start + 2, len(paragraphs))
            if paragraphs[i].startswith("Checkpoint:")
        )
        source = "\n".join(paragraphs[start + 2 : end]).strip() + "\n"
        if not source.strip():
            raise ValueError(f"Empty {notebook} cell {number}")
        ast.parse(source, filename=f"{notebook}_cell_{number}.py")
        cells.append(source)
        section_start = end
    return cells


def write_notebook(name: str, cells: list[str]) -> None:
    NOTEBOOK_OUTPUT.mkdir(parents=True, exist_ok=True)
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {"tags": ["parameters"]} if index == 0 else {},
                "outputs": [],
                "source": source.splitlines(keepends=True),
            }
            for index, source in enumerate(cells)
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    destination = NOTEBOOK_OUTPUT / name
    destination.write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{destination.relative_to(ROOT)}: {len(cells)} syntax-checked cells")


def main() -> None:
    paragraphs = paragraphs_from_docx(SOURCE)
    blocks = extract_blocks(paragraphs)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name in BLOCKS:
        destination = OUTPUT / f"{name}_{NAMES[name]}.sql"
        content = f"-- Source: {SOURCE.relative_to(ROOT).as_posix()}\n"
        content += "\n".join(blocks[name]) + "\n"
        destination.write_text(content, encoding="utf-8")
        print(f"{destination.relative_to(ROOT)}: {len(blocks[name])} lines")
    write_notebook("nb_gold_train.ipynb", extract_notebook_cells(paragraphs, "train", 6))
    write_notebook("nb_gold_score.ipynb", extract_notebook_cells(paragraphs, "score", 4))


if __name__ == "__main__":
    main()
