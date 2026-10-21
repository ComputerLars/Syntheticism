"""Put source-video stills into the eight video fields in the PDF slide views."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib,json,posixpath,shutil,subprocess,zipfile
from lxml import etree
from PIL import Image,ImageOps,ImageDraw,ImageFont

R=Path(__file__).resolve().parents[1]
N={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
runtime=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override'
poppler=shutil.which('pdftoppm')or str(runtime/'pdftoppm')
ffmpeg=shutil.which('ffmpeg')or'/opt/homebrew/bin/ffmpeg'
pdf=R/'defence/Syntheticism-Defence-21-September-2026.pdf'
pptx=R/'defence/Syntheticism-Defence-21-September-2026.pptx'
records=[]
office=Path('/Applications/Microsoft PowerPoint.app/Contents/Resources/DFonts')
def font(size,italic=False):
    file=office/('GARAIT.ttf'if italic else'GARA.ttf')
    if not file.exists():file=R/'assets/fonts'/('EBGaramond-Italic.ttf'if italic else'EBGaramond.ttf')
    return ImageFont.truetype(str(file),size)
with TemporaryDirectory(prefix='slide-posters-')as tmp,zipfile.ZipFile(pptx)as z:
    work=Path(tmp)
    size=etree.fromstring(z.read('ppt/presentation.xml')).find('p:sldSz',N)
    sx,sy=1920/int(size.get('cx')),1080/int(size.get('cy'))
    for n in range(1,55):
        root=etree.fromstring(z.read(f'ppt/slides/slide{n}.xml'))
        rels={v.get('Id'):v.get('Target')for v in etree.fromstring(z.read(f'ppt/slides/_rels/slide{n}.xml.rels'))}
        shapes=[p for p in root.findall('.//p:pic',N)if p.find('.//a:videoFile',N)is not None]
        if not shapes:continue
        base=work/f'slide-{n}'
        subprocess.run([poppler,'-f',str(n),'-l',str(n),'-singlefile','-scale-to-x','1920','-scale-to-y','1080','-png',str(pdf),str(base)],check=True)
        with Image.open(base.with_suffix('.png'))as original:canvas=original.convert('RGB')
        for shape in shapes:
            video=shape.find('.//a:videoFile',N);rid=video.get('{'+N['r']+'}link')
            member=posixpath.normpath(posixpath.join('ppt/slides',rels[rid]));raw=z.read(member)
            clip=work/Path(member).name;clip.write_bytes(raw);frame=work/f'frame-{n}.png';seconds=2
            subprocess.run([ffmpeg,'-v','error','-y','-ss',str(seconds),'-i',str(clip),'-frames:v','1',str(frame)],check=True)
            transform=shape.find('p:spPr/a:xfrm',N);off=transform.find('a:off',N);ext=transform.find('a:ext',N)
            x,y=round(int(off.get('x'))*sx),round(int(off.get('y'))*sy)
            w,h=round(int(ext.get('cx'))*sx),round(int(ext.get('cy'))*sy)
            with Image.open(frame)as image:still=ImageOps.contain(image.convert('RGB'),(w,h),Image.Resampling.LANCZOS)
            canvas.paste(still,(x+(w-still.width)//2,y+(h-still.height)//2))
            records.append(dict(slide=n,source_member=member,source_sha256=hashlib.sha256(raw).hexdigest(),frame_seconds=seconds,field_pixels=[x,y,w,h]))
        # Restore the source PowerPoint's explicit line breaks where the PDF
        # export's substituted metrics made the title/caption overrun its box.
        if n==40:
            draw=ImageDraw.Draw(canvas);draw.rectangle((1140,284,1900,486),fill='white')
            for i,t in enumerate(['Isaac Asimov’s Incubation of Political','AI: An Immanent Critique?']):
                draw.text((1148,300+i*58),t,font=font(48,True),fill='black',anchor='lt')
            draw.text((1148,455),'Asker Bryld Staunæs (2026).',font=font(35),fill='black',anchor='lt')
        if n==45:
            draw=ImageDraw.Draw(canvas);draw.rectangle((0,857,1920,1080),fill='white')
            caption=['Synthetic Summit Simulator. Computer Lars in cooperation with DemAI, Kunsthal','Aarhus, 2025. Multi-agent roleplay environment: SillyTavern. Model: Hermes 3,','Nous Research. Eight political AI figures; visitor intervention through Citizen Cyborg.']
            for i,t in enumerate(caption):draw.text((960,871+i*42),t,font=font(35,True),fill='black',anchor='mt')
            draw.text((960,1024),'Staunæs 2026: 276–278.',font=font(30),fill='#555555',anchor='mt')
        canvas.save(R/f'assets/slides/slide-{n:02}.jpg',quality=92,optimize=True)
(R/'documentation/slide-posters.json').write_text(json.dumps(dict(source=pptx.relative_to(R).as_posix(),slides=records,restored_powerpoint_linebreaks=[40,45]),indent=2)+'\n')
print('Video stills:',len(records))
