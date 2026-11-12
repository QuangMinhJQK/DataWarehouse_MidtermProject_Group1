"""Create page-free TOC entries for the unwritten DW chapters from the outline."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1] / 'docs' / 'data_warehouse'
source = (root / 'source' / 'content' / 'tableofcontent.md').read_text(encoding='utf-8')
lines = ['% Chương 3–7: chỉ xuất hiện trong mục lục, không tạo trang nội dung.']
active = False

for raw in source.splitlines():
    m = re.match(r'^(#{1,4})\s+(.+)', raw)
    if not m:
        continue
    title = m.group(2).strip().strip('*').strip()
    if title.startswith('CHƯƠNG 3:'):
        active = True
    if not active:
        continue
    if title.startswith('CHƯƠNG '):
        level, label = 'section', title
    else:
        numbered = re.match(r'^(\d+(?:\.\d+)*)(?:\.)?\s+(.+)', title)
        if not numbered:
            continue
        number, caption = numbered.groups()
        level = 'subsection' if number.count('.') == 1 else 'subsubsection'
        label = rf'\protect\numberline{{{number}}}{caption.strip().strip("*")}'
    lines.append(rf'\addtocontents{{toc}}{{\protect\contentsline{{{level}}}{{{label}}}{{--}}{{}}}}')

if not lines[1:]:
    raise SystemExit('No chapter 3–7 headings found in tableofcontent.md')
(root / 'planned-toc.tex').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'Wrote {len(lines) - 1} planned TOC entries')
