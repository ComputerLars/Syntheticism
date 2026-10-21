"""Render the native PowerPoint slide PDF as whole-frame access images.

The PDF is exported in PowerPoint with the installed Garamond and Consolas
fonts (Best for printing). Its video posters are embedded source images. The
anagram on page 27 is exported at its motion paths’ completed positions.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib,json,shutil,subprocess,sys,re,zipfile
from lxml import etree
from PIL import Image
from pypdf import PdfReader

R=Path(__file__).resolve().parents[1]
runtime=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override'
poppler=shutil.which('pdftoppm')or str(runtime/'pdftoppm')
pdf=R/'defence/Syntheticism-Defence-21-September-2026.pdf'
pptx=R/'defence/Syntheticism-Defence-21-September-2026.pptx'
if '--prepare-access' in sys.argv:
    ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
    target=R/'.book-build/defence-static-access.pptx';target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(pptx)as source,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED)as dest:
        for item in source.infolist():
            data=source.read(item.filename)
            if item.filename=='ppt/slides/slide27.xml':
                root=etree.fromstring(data);letters=[]
                for motion in root.findall('.//p:animMotion',ns):
                    sid=motion.find('.//p:spTgt',ns).get('spid')
                    dx,dy=map(float,re.findall(r'-?\d+(?:\.\d+)?',motion.get('path'))[-2:])
                    shape=root.xpath(f'.//p:sp[p:nvSpPr/p:cNvPr[@id="{sid}"]]',namespaces=ns)[0]
                    off=shape.find('p:spPr/a:xfrm/a:off',ns)
                    off.set('x',str(round(int(off.get('x'))+dx*12192000)))
                    off.set('y',str(round(int(off.get('y'))+dy*6858000)))
                    letters.append((int(off.get('x')),''.join(shape.xpath('.//a:t/text()',namespaces=ns))))
                assert ''.join(t for x,t in sorted(letters))=='COMPUTERLARS '
                root.remove(root.find('p:timing',ns))
                data=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
            dest.writestr(item,data)
    print(target);sys.exit(0)
assert len(PdfReader(pdf).pages)==54
records=[]
with TemporaryDirectory(prefix='native-slide-views-')as tmp:
    work=Path(tmp)
    subprocess.run([poppler,'-scale-to-x','1920','-scale-to-y','1080','-jpeg','-jpegopt','quality=93,optimize=y',str(pdf),str(work/'slide')],check=True)
    for n in range(1,55):
        source=work/f'slide-{n:02}.jpg';dest=R/f'assets/slides/slide-{n:02}.jpg'
        with Image.open(source)as image:assert image.size==(1920,1080)
        shutil.copyfile(source,dest)
        records.append(dict(slide=n,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
record=dict(source=pptx.relative_to(R).as_posix(),source_sha256=hashlib.sha256(pptx.read_bytes()).hexdigest(),pdf=pdf.relative_to(R).as_posix(),pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),renderer='Microsoft PowerPoint for Mac; local print export; embedded Garamond and Consolas',dimensions=[1920,1080],completed_motion_state=[27],embedded_video_posters=[16,33,34,35,37,40,41,45],slides=records)
(R/'documentation/slide-posters.json').write_text(json.dumps(record,indent=2)+'\n')
print('Native whole-frame slide views:',len(records))
