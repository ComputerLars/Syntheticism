"""Public defence book: reading transcript, photographs, slides and linked references."""
from pathlib import Path
import json,re
from lxml import html
from reportlab.platypus import Spacer,PageBreak,KeepTogether,CondPageBreak
from archive_pdf import Book,E,link
R=Path(__file__).resolve().parents[1];SITE='https://computerlars.github.io/Syntheticism-How-I-Learned-to-Love-Democracy/'
tree=html.fromstring((R/'index.html').read_text());data=json.loads((R/'assets/defence.json').read_text())
b=Book(R,body='EBGaramond.ttf',italic='EBGaramond-Italic.ttf',bold='EBGaramond.ttf',body_size=11.2,leading=14.1,serif=True)
def inline(el):
 out=E(el.text or'')
 for c in el:
  tag=c.tag;body=inline(c)
  if tag=='a':
   href=c.get('href','')
   if href:body='<a href="'+E(href if href.startswith(('http','#'))else SITE+href)+'" color="#000000">'+body+'</a>'
  elif tag=='em':body='<i>'+body+'</i>'
  elif tag=='br':body='<br/>'
  elif tag=='sup':body='<super><font name="BookMeta" size="6.4">'+body+'</font></super>'
  elif tag=='span'and c.get('class')=='source-anchor':body='<a name="'+c.get('id')+'"/>'
  elif tag=='span'and c.get('class')=='formal-label':body='<font name="BookMeta" color="#ff0000">'+body+'</font>'
  elif tag=='span'and c.get('class')=='reference-number':body='<font name="BookMeta">'+body+'</font>'
  out+=body+E(c.tail or'')
 return out

def figure(el,height=330):
 im=el.xpath('.//img')[0];cap=el.xpath('./figcaption')[0].text_content();b.image(im.get('src'),cap,SITE+im.get('src'),maxheight=height)

b.story.append(Spacer(1,40));b.p('Syntheticism:<br/>How I Learned to Love Democracy','cover',True);b.p('Asker Bryld Staunæs','centre');b.p('Public PhD defence<br/>Aarhus University · 21 September 2026<br/>Kasernen · Lille Sal · Aarhus','centre',True)
figure(tree.xpath('//figure[@class="opening-image"]')[0],210)
b.contents('Contents')
backlinks={}
for p in tree.xpath('//p[@class="speech"]'):
 anchor=p.get('data-anchor')
 for a in p.xpath('.//sup/a'):
  backlinks.setdefault(a.get('href','').lstrip('#'),[]).append(anchor)
for el in tree.xpath('//article[@class="transcript"]/*'):
 if el.tag=='figure':figure(el);continue
 if el.tag!='section':continue
 sid=el.get('id');title=el.xpath('./header/h2')[0].text_content();b.heading(title,sid,0,new=True)
 recording=int(el.xpath('./header/p')[0].text_content().strip().split()[-1]);rec=next(x for x in data['recordings']if x['id']==recording)
 b.p('Recording '+str(recording)+' · '+link(rec['audio'],'Audio')+' · '+link(rec['video'],'Video'),'source',True)
 for child in el:
  if child.tag=='figure':figure(child,260)
  elif child.get('class')=='speaker-turn':
   sp=child.xpath('./p[@class="speaker"]')[0];name=sp.xpath('./span')[0].text_content();button=sp.xpath('./button')[0];sec=button.get('data-time');clock=button.text_content()
   b.p(E(name)+' · '+link(SITE+'#'+child.xpath('./p[@class="speech"]')[0].get('data-anchor'),clock),'meta',True)
   for p in child.xpath('./p[@class="speech"]'):b.p(inline(p),raw=True)
b.heading('Slides','slides',0,new=True)
b.p('54 displayed states · 21 September 2026','source')
b.p(link(SITE+'defence/Syntheticism-Defence-21-September-2026.pptx','PowerPoint')+' · '+link(SITE+'defence/Syntheticism-Defence-21-September-2026.pdf','Slides as PDF'),'source',True)
for s in data['slides']:
 b.image(s['src'],'Slide '+str(s['number']),SITE+'defence/Syntheticism-Defence-21-September-2026.pdf#page='+str(s['number']),maxheight=195,anchor='slide-'+str(s['number']))
b.heading('References','references',0,new=True)
for el in tree.xpath('//section[@id="references"]/*'):
 first=len(b.story)
 if el.tag=='h2':continue
 if el.tag=='h3':b.story.append(CondPageBreak(105));b.p(el.text_content(),'h2')
 elif el.tag=='div'and el.get('class')=='article-record':
  label=el.xpath('./a')[0];b.p('<font color="#ff0000">'+E(label.text_content())+'</font>','meta',True);b.p(el.xpath('./h4')[0].text_content(),'h3');b.p(inline(el.xpath('./p')[0]),'source',True)
  b.p(link(label.get('href'),'Read article in the dissertation'),'source',True)
 elif el.tag=='p':
  ident=el.get('id');b.p(inline(el),'source',True,anchor=ident)
  if ident and backlinks.get(ident):b.p('Transcript: '+' · '.join(link('#'+a,a[3:5]+':'+a[5:7]+':'+a[7:9])for a in dict.fromkeys(backlinks[ident])),'source',True)
 if el.tag in ('div','p'):b.story[first:]=[KeepTogether(b.story[first:])]
b.heading('Recordings','recordings',0,new=True)
for rec in data['recordings']:
 b.p('Recording '+str(rec['id'])+' · '+rec['label'],'h3');b.p(link(rec['audio'],rec['audio'])+'<br/>'+link(rec['video'],rec['video']),'source',True)
b.heading('Colophon','colophon',0,new=True)
for p in tree.xpath('//footer[@class="colophon"]/p'):b.p(inline(p),'source'if p.get('class')=='metadata'else'body',True)
b.p('Reading edition with the complete defence transcript, documentary photographs, 54 slide states and references. Timestamps restart for recording 2. Dissertation references use printed folios; the PDF viewer page is one higher.','source')
b.p(link(SITE,SITE),'source',True)
OUT=R/'transcript/Syntheticism-Defence-Reading-Edition.pdf'
print(json.dumps(b.build(OUT,'Syntheticism: How I Learned to Love Democracy — Public Defence','Asker Bryld Staunæs','Syntheticism · Public defence')))
