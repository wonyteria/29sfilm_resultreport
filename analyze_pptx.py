from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import json, re

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}

def nkey(path):
    m = re.search(r'slide(\d+)\.xml$', path)
    return int(m.group(1)) if m else 0

def analyze(path):
    with ZipFile(path) as z:
        names = z.namelist()
        slides = sorted((x for x in names if re.fullmatch(r'ppt/slides/slide\d+\.xml', x)), key=nkey)
        out = {'file': path.name, 'slides': len(slides), 'media': len([x for x in names if x.startswith('ppt/media/')]), 'pages': []}
        for sp in slides:
            root = ET.fromstring(z.read(sp))
            texts = [''.join(t.itertext()).strip() for t in root.findall('.//a:t', NS)]
            texts = [t for t in texts if t]
            page = {
                'no': nkey(sp),
                'text': ' | '.join(texts),
                'shapes': len(root.findall('.//p:sp', NS)),
                'pictures': len(root.findall('.//p:pic', NS)),
                'tables': len(root.findall('.//a:tbl', NS)),
                'charts': 0,
            }
            rp = sp.replace('slides/', 'slides/_rels/') + '.rels'
            if rp in names:
                rel = ET.fromstring(z.read(rp))
                page['charts'] = sum(1 for x in rel if '/chart' in x.attrib.get('Type',''))
            out['pages'].append(page)
        return out

files = sorted(Path('.').glob('*.pptx'))
data = [analyze(p) for p in files]
Path('pptx_analysis.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
for d in data:
    print(f"{d['file']}\t{d['slides']} slides\t{d['media']} media")
    for p in d['pages']:
        print(f"  {p['no']:03d}\tsh={p['shapes']} pic={p['pictures']} tbl={p['tables']} chart={p['charts']}\t{p['text'][:180]}")
