"""Typeset the existing reading edition, with its source anchors and slide states."""
from pathlib import Path
import hashlib,html,json,re,zipfile
from lxml import etree

R=Path(__file__).resolve().parents[1]
E=html.escape
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
SLUG='Syntheticism-How-I-Learned-to-Love-Democracy'
REPO='https://github.com/ComputerLars/'+SLUG
RELEASE=REPO+'/releases/download/defence-recordings-20260921/'

def inline(text):
 text=E(text)
 text=re.sub(r'&lt;a id=&quot;([\w-]+)&quot;&gt;&lt;/a&gt;',r'<span class="source-anchor" id="\1"></span>',text)
 text=re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+|#[\w-]+)\)',lambda m:'<a href="'+m[2]+'">'+m[1]+'</a>',text)
 text=re.sub(r'\[\^ref(\d+)\]',r'<sup><a href="#ref\1" aria-label="Reference \1">\1</a></sup>',text)
 text=re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)',r'<em>\1</em>',text)
 return text

def build():
 meta=json.loads((R/'metadata.json').read_text())
 md=(R/'transcript/defence-transcript.md').read_text()
 articles=json.loads((R/'transcript/navigation.json').read_text())['articles']
 sections=[];recording=1;turn=None;section=None;pending=[];refs=False;reference_parts=[]
 slugs={'Opening remarks':'opening-remarks','Opening lecture':'opening-lecture','Discussion with Jan Bäcklund':'jan-backlund','Discussion with Sine Nørholm Just':'sine-norholm-just','Discussion with Jussi Parikka':'jussi-parikka'}
 for block in md.split('\n\n'):
  block=block.strip()
  if block=='## References':refs=True;continue
  if refs:
   if block.startswith('### '):reference_parts.append('<h3>'+E(block[4:])+'</h3>')
   elif block.startswith('- [Article '):
    n=int(re.match(r'- \[Article ([1-7])',block)[1]);a=next(a for a in articles if a['number']==n)
    reference_parts.append('<div class="article-record"><a class="formal-label" href="'+a['url']+'">ARTICLE '+str(n)+'</a><h4>'+E(a['title'])+'</h4><p>'+E(a['authors'])+'<br>In dissertation: pp. '+str(a['printed_pages'][0])+'–'+str(a['printed_pages'][1])+'.</p></div>')
   elif block.startswith('- '):reference_parts.append('<p>'+inline(block[2:])+'</p>')
   elif re.match(r'\[\^ref\d+\]:',block):
    m=re.match(r'\[\^ref(\d+)\]: (.*)',block,re.S);reference_parts.append('<p id="ref'+m[1]+'"><span class="reference-number">'+m[1]+'</span>. '+inline(m[2])+'</p>')
   elif block:reference_parts.append('<p>'+inline(block)+'</p>')
   continue
  if block=='## Recording 2':recording=2;continue
  if block.startswith('### '):
   title=block[4:];section={'title':title,'id':slugs[title],'recording':recording,'turns':[]};sections.append(section);turn=None;continue
  m=re.fullmatch(r'\*\*(.*?) · (\d\d:\d\d:\d\d)\*\*',block)
  if m:
   turn={'speaker':m[1],'time':m[2],'recording':recording,'paragraphs':[]};section['turns'].append(turn);continue
  if section and turn:
   if re.fullmatch(r'<a id="[\w-]+"></a>',block):pending.append(block);continue
   block=''.join(pending)+block;pending=[];turn['paragraphs'].append(block)
 assert not pending
 slides=[]
 with zipfile.ZipFile(R/meta['slides']['file'])as z:
  for n in range(1,55):
   root=etree.fromstring(z.read(f'ppt/slides/slide{n}.xml'))
   paras=[''.join(p.xpath('.//a:t/text()',namespaces=NS))for p in root.findall('.//a:p',NS)]
   text=' '.join(p for p in paras if p.strip())
   slides.append({'number':n,'src':f'assets/slides/slide-{n:02}.jpg','title':paras[0]or 'Defence slide','text':text})
 data={'title':meta['title'],'recordings':[
  {'id':1,'label':'Opening and Jan Bäcklund','video':RELEASE+'Syntheticism-Defence-Recording-1.mp4','audio':RELEASE+'Syntheticism-Defence-Recording-1.m4a','video_offset':766,'start':766,'duration':5383.483333},
  {'id':2,'label':'Sine Nørholm Just and Jussi Parikka','video':RELEASE+'Syntheticism-Defence-Recording-2.mp4','audio':RELEASE+'Syntheticism-Defence-Recording-2.m4a','video_offset':0,'start':149,'duration':4646.582}
 ],'slides':slides}
 (R/'assets/defence.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
 body=[]
 photos={x['id']:x for x in json.loads((R/'assets/photos/sources.json').read_text())}if (R/'assets/photos/sources.json').exists()else{}
 def plate(key,speaker=False):
  if key not in photos:return ''
  p=photos[key]
  cls='speaker-portrait'+(' portrait'if p['height']>p['width']else'')if speaker else'documentary-plate'
  return '<figure class="'+cls+'"><a href="'+p['src']+'"><img src="'+p['src']+'" width="'+str(p['width'])+'" height="'+str(p['height'])+'" loading="lazy" alt="'+E(p['caption'],quote=True)+'"></a><figcaption>'+E(p['caption'])+'</figcaption></figure>'
 for s in sections:
  body.append('<section class="transcript-section" id="'+s['id']+'"><header><p class="section-meta"><span class="formal-label">RECORDING '+str(s['recording'])+'</span></p><h2>'+E(s['title'])+'</h2></header>')
  if s['id'] in {'jan-backlund','sine-norholm-just','jussi-parikka'}:body.append(plate(s['id'],speaker=True))
  for t in s['turns']:
   sec=sum(int(v)*w for v,w in zip(t['time'].split(':'),[3600,60,1]))
   body.append('<div class="speaker-turn"><p class="speaker"><span>'+E(t['speaker'])+'</span> <button data-play="'+str(t['recording'])+'" data-time="'+str(sec)+'" aria-label="Play recording '+str(t['recording'])+' at '+t['time']+'">'+t['time']+'</button></p>')
   for p in t['paragraphs']:
    ids=re.findall(r'<a id="([\w-]+)"',p);time=ids[-1][3:]if ids else''
    a=ids[0]if ids else''
    body.append('<p class="speech"'+(' data-anchor="'+a+'"'if a else'')+'>'+inline(p)+('</p>'))
   body.append('</div>')
  body.append('</section>')
  if s['id']=='opening-lecture':body.append(plate('lecture'))
  if s['id']=='sine-norholm-just':body.append(plate('audience'))
  if s['id']=='jussi-parikka':body.extend([plate('audience-after-defence'),plate('following-defence',speaker=True)])
 nav=''.join('<a href="#'+s['id']+'">'+E(s['title'].replace('Discussion with ',''))+'</a>'for s in sections)
 thumbs=''.join('<button class="slide-thumb" data-slide="'+str(s['number'])+'"><img src="'+s['src']+'" loading="lazy" width="1920" height="1080" alt="'+E(s['title'],quote=True)+'"><span>'+str(s['number'])+'</span></button>'for s in slides)
 document='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Syntheticism: How I Learned to Love Democracy</title>
<meta name="author" content="Asker Bryld Staunæs"><meta name="description" content="The public PhD defence of Syntheticism: How I Learned to Love Democracy. Aarhus University, 21 September 2026. Transcript, recordings, slides and dissertation.">
<link rel="stylesheet" href="defence.css"><script src="defence.js" defer></script></head><body>
<header class="masthead"><a href="#top" class="archive-name">Syntheticism</a><nav aria-label="Archive"><a href="#opening-lecture">Lecture</a><a href="#jan-backlund">Discussion</a><a href="#slides">Slides</a><a href="dissertation/Syntheticism-How-I-Learned-to-Love-Democracy.pdf">Dissertation</a><a href="REPOSITORY">Repository</a></nav></header>
<main id="top"><header class="title-page"><p class="event-meta"><span class="formal-label">DEFENCE</span>: 21 September 2026 · Aarhus University</p><h1>Syntheticism: How I Learned to Love Democracy</h1><p class="author">Asker Bryld Staunæs</p><p class="venue">Kasernen · Lille Sal · Aarhus</p>
<figure class="opening-image"><img id="poster" src="assets/defence-poster.jpg" width="960" height="540" alt="Asker Bryld Staunæs presenting the dissertation in Lille Sal, with the assessment committee and audience."><figcaption>Public PhD defence, Kasernen, Aarhus University, 21 September 2026.</figcaption></figure>
<div class="media-choices"><button data-mode="audio">Audio</button><button data-mode="video">Video</button><button id="background-toggle" aria-pressed="false">Video as background</button><label class="text-size" for="reading-size">Type <input id="reading-size" type="range" min="24" max="40" step="1" value="29"></label></div>
<div class="media-dock" id="media-dock" hidden><div class="media-heading"><span id="record-label">Recording 1</span><button id="close-media" aria-label="Close and pause recording">Close</button></div><video id="film" controls playsinline preload="none" poster="assets/defence-poster.jpg" hidden></video><audio id="sound" controls preload="none" hidden></audio><p class="media-status" id="media-status" aria-live="polite"></p></div>
<p class="event-detail">Chair: Stefan Iversen.<br>Assessment committee: Jussi Parikka, Sine Nørholm Just and Jan Bäcklund.</p></header>
<nav class="reading-contents" aria-label="Defence transcript">NAVIGATION</nav>
<article class="transcript">TRANSCRIPT</article>
<section class="slides-section" id="slides"><p class="section-meta"><span class="formal-label">DEFENCE</span> · 54 slide states</p><h2>Slides</h2><p class="downloads"><a href="defence/Syntheticism-Defence-21-September-2026.pptx">PowerPoint</a> · <a href="defence/Syntheticism-Defence-21-September-2026.pdf">PDF</a></p><div class="slide-grid">THUMBNAILS</div></section>
<section class="references" id="references"><h2>References</h2>REFERENCES</section>
<footer class="colophon"><h2>Colophon</h2><p>Asker Bryld Staunæs. <em>Syntheticism: How I Learned to Love Democracy.</em> Article-based PhD dissertation in artistic research, Aarhus University, 2026.</p><p class="metadata"><span class="formal-label">DEGREE</span>: PhD awarded 6 October 2026.<br><span class="formal-label">SUPERVISORS</span>: Lotte Philipsen; Cristina Maria Flesher Fominaya.<br><span class="formal-label">FUNDING</span>: Novo Nordisk Fonden · Mads Øvlisen PhD Scholarship in practice-based research in art · NNF23OC0081575.</p><p class="metadata"><a href="https://arts.au.dk/en/news-and-events/events/show/artikel/phd-defence-asker-bryld-staunaes">Official announcement</a> · <a href="transcript/defence-transcript.md">Transcript</a> · <a href="transcript/Syntheticism-Defence-21-September-2026-Reading-Edition.docx">Word</a> · <a href="documentation/rights.md">Rights</a> · <a href="REPOSITORY">Repository</a></p></footer></main>
<dialog id="slide-view"><div class="slide-controls"><button id="previous-slide" aria-label="Previous slide">Previous</button><span id="slide-number"></span><button id="next-slide" aria-label="Next slide">Next</button><button id="close-slide">Close</button></div><img id="slide-image" alt=""><p class="slide-title" id="slide-title"></p></dialog>
</body></html>'''
 document=document.replace('REPOSITORY',REPO).replace('NAVIGATION',nav).replace('TRANSCRIPT',''.join(body)).replace('THUMBNAILS',thumbs).replace('REFERENCES',''.join(reference_parts))
 if 'opening'in photos:
  p=photos['opening'];document=document.replace('<img id="poster" src="assets/defence-poster.jpg" width="960" height="540" alt="Asker Bryld Staunæs presenting the dissertation in Lille Sal, with the assessment committee and audience.">','<img id="poster" src="'+p['src']+'" width="'+str(p['width'])+'" height="'+str(p['height'])+'" alt="Presenting Syntheticism from the lectern in Lille Sal, 21 September 2026.">')
 (R/'index.html').write_text(document+'\n')
 print('Defence page:',len(sections),'sections;',sum(len(s['turns'])for s in sections),'turns;',len(slides),'slides')
if __name__=='__main__':build()
