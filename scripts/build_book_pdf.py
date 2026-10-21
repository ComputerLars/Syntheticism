"""Typeset the defence transcript, photographs, slides and sources with Typst."""
from pathlib import Path
import json
from lxml import html
from typst_book import Book,rich,link
R=Path(__file__).resolve().parents[1];SITE='https://computerlars.github.io/Syntheticism-How-I-Learned-to-Love-Democracy/'
tree=html.fromstring((R/'index.html').read_text());data=json.loads((R/'assets/defence.json').read_text())
def inline(el):
 out=rich(el.text or'')
 for c in el:
  body=inline(c);tag=c.tag
  if tag=='a':
   href=c.get('href','')
   if href:body=[dict(t='link',url=href if href.startswith(('http','#'))else SITE+href,body=body)]
  elif tag=='em':body=[dict(t='italic',body=body)]
  elif tag=='br':body=[dict(t='br')]
  elif tag=='sup':body=[dict(t='sup',body=body)]
  elif tag=='span'and c.get('class')=='source-anchor':body=[dict(t='anchor',id=c.get('id'))]
  elif tag=='span'and c.get('class')=='formal-label':body=[dict(t='formal',body=body)]
  out+=body+rich(c.tail or'')
 return out
imprint=[
 rich('Asker Bryld Staunæs. ',dict(t='italic',body=['Syntheticism: How I Learned to Love Democracy.'])),
 rich('Public PhD defence. Aarhus University, Kasernen, Lille Sal. 21 September 2026. Reading edition, October 2026.'),
 rich('Asker Bryld Staunæs’ own text is licensed under CC BY 4.0, except where another notice applies. Contributions by other speakers, photographs and third-party works retain their separate rights.'),
 rich('Typeset in Garamond and Consolas. A5. Typst.'),
 rich(link(SITE+'documentation/rights.md','Rights and reuse'),' · ',link(SITE+'dissertation/Syntheticism-How-I-Learned-to-Love-Democracy.pdf','Dissertation'))]
b=Book(R,'defence','Syntheticism: How I Learned to Love Democracy','Public PhD defence · Transcript, photographs, slides and references','Asker Bryld Staunæs','Aarhus University · 21 September 2026',SITE,'Syntheticism:','How I Learned to\nLove Democracy','PUBLIC PHD DEFENCE',imprint)
def figure(el,height=115,append=True):
 im=el.xpath('.//img')[0];cap=el.xpath('./figcaption')[0].text_content()
 return b.image(im.get('src'),cap,SITE+im.get('src'),height=height,append=append)
b.data['cover-image']=figure(tree.xpath('//figure[@class="opening-image"]')[0],62,append=False)
backlinks={}
for p in tree.xpath('//p[@class="speech"]'):
 for a in p.xpath('.//sup/a'):backlinks.setdefault(a.get('href','').lstrip('#'),[]).append(p.get('data-anchor'))
for el in tree.xpath('//article[@class="transcript"]/*'):
 if el.tag=='figure':figure(el);continue
 if el.tag!='section':continue
 sid=el.get('id');title=el.xpath('./header/h2')[0].text_content();b.chapter(title,sid)
 recording=int(el.xpath('./header/p')[0].text_content().strip().split()[-1]);rec=next(x for x in data['recordings']if x['id']==recording)
 b.p(rich('Recording '+str(recording)+' · ',link(rec['audio'],'Audio'),' · ',link(rec['video'],'Video')),'source')
 for child in el:
  if child.tag=='figure':figure(child,100)
  elif child.get('class')=='speaker-turn':
   sp=child.xpath('./p[@class="speaker"]')[0];name=sp.xpath('./span')[0].text_content();button=sp.xpath('./button')[0]
   paragraphs=[dict(id=None,body=inline(p))for p in child.xpath('./p[@class="speech"]')]
   b.add('turn',speaker=name,clock=button.text_content(),url=SITE+'#'+child.xpath('./p[@class="speech"]')[0].get('data-anchor'),paragraphs=paragraphs)
b.chapter('Slides','slides','54 displayed states · 21 September 2026')
b.p(rich(link(SITE+'defence/Syntheticism-Defence-21-September-2026.pptx','PowerPoint'),' · ',link(SITE+'defence/Syntheticism-Defence-21-September-2026.pdf','Slides as PDF')),'source')
for s in data['slides']:b.image(s['src'],'Slide '+str(s['number']),SITE+'defence/Syntheticism-Defence-21-September-2026.pdf#page='+str(s['number']),height=64,id='slide-'+str(s['number']))
b.chapter('References','references')
for el in tree.xpath('//section[@id="references"]/*'):
 if el.tag=='h2':continue
 if el.tag=='h3':b.section(el.text_content(),'references-'+el.text_content().lower().replace(' ','-'))
 elif el.tag=='div'and el.get('class')=='article-record':
  label=el.xpath('./a')[0];b.add('article',label=label.text_content(),title=el.xpath('./h4')[0].text_content(),url=label.get('href'),body=inline(el.xpath('./p')[0]))
 elif el.tag=='p':
  ident=el.get('id');backs=[]
  if ident and backlinks.get(ident):
   backs=['Transcript: ']
   for i,a in enumerate(dict.fromkeys(backlinks[ident])):
    if i:backs.append(' · ')
    backs.append(link('#'+a,a[3:5]+':'+a[5:7]+':'+a[7:9]))
  b.add('bibliography',id=ident,citation=inline(el),note='',backlinks=backs)
b.chapter('Recordings','recordings')
for rec in data['recordings']:
 b.section('Recording '+str(rec['id']),'recording-'+str(rec['id']),rec['label'])
 b.p(rich(link(rec['audio'],'Audio'),' · ',link(rec['video'],'Video')),'source')
b.chapter('Colophon','colophon')
for p in tree.xpath('//footer[@class="colophon"]/p'):b.p(inline(p),'source'if p.get('class')=='metadata'else'body',first=True)
b.p('Reading edition with the complete defence transcript, documentary photographs, 54 slide states and references. Timestamps restart for recording 2. Dissertation references use printed folios; the PDF viewer page is one higher.','source',first=True)
b.p('Typeset in Garamond and Consolas. A5. Typst.','source',first=True)
b.p(rich(link(SITE,SITE)),'source')
print(json.dumps(b.build(R/'transcript/Syntheticism-Defence-Reading-Edition.pdf')))
