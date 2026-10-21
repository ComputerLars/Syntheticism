"""The author’s defence script, with corresponding recording and slide anchors."""
from pathlib import Path
from copy import deepcopy
from difflib import SequenceMatcher
from bisect import bisect_left,bisect_right
from zipfile import ZipFile
from lxml import etree
import json,posixpath,re

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'documentation/lecture-layout.json'
LAYOUT=json.loads(PATH.read_text())
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
CUE=re.compile(r'\[→\s*([\d.]+)\]')
STAGE=re.compile(r'\((?:hold up|video starts|Aarhus video|Warsaw video|Linz video|hold 3 s · reception figures)\)')

def script_paragraphs():
    """Extract spoken notes; source apparatus and performance directions stay out."""
    paragraphs=[];states=[];current=None
    with ZipFile(ROOT/LAYOUT['source'])as z:
        for section in LAYOUT['source_sections']:
            n=section['slide']
            rel=etree.fromstring(z.read(f'ppt/slides/_rels/slide{n}.xml.rels'))
            target=next(v.get('Target')for v in rel if v.get('Type').endswith('/notesSlide'))
            body=etree.fromstring(z.read(posixpath.normpath(posixpath.join('ppt/slides',target))))
            ps=body.xpath('.//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]/p:txBody/a:p',namespaces=NS)
            for pi,p in enumerate(ps[:section['spoken_paragraphs']]):
                text=''.join(p.xpath('.//a:t/text()',namespaces=NS))
                if not states:current='1.0';states.append(current)
                cursor=0
                fragments=[]
                for cue in CUE.finditer(text):
                    fragments.append((None,text[cursor:cue.start()]));fragments.append((cue[1],''));cursor=cue.end()
                fragments.append((None,text[cursor:]))
                for cue,item in fragments:
                    if cue:current=cue;states.append(current);continue
                    spoken=re.sub(r'\s+([,.;:!?])',r'\1',STAGE.sub('',item)).strip()
                    if not spoken:continue
                    for change in LAYOUT['script_corrections']:spoken=spoken.replace(change['before'],change['after'])
                    paragraphs.append(dict(id=f'lecture-p{len(paragraphs)+1:02}',text=spoken,cue=current,source_slide=n,source_paragraph=pi))
    assert len(states)==54 and len(set(states))==54,states
    for p in paragraphs:p['slides_after']=[]
    for number,cue in enumerate(states,1):
        indices=[i for i,p in enumerate(paragraphs)if p['cue']==cue]
        if indices:
            target=LAYOUT.get('image_after_source_paragraph',{}).get(cue)
            chosen=next((i for i in indices if paragraphs[i]['source_paragraph']==target),indices[-1])
            paragraphs[chosen]['slides_after'].append(number)
        else:
            # The reception-statistics hold has no spoken words of its own.
            following=next(i for i,p in enumerate(paragraphs)if states.index(p['cue'])>states.index(cue))
            paragraphs[following-1]['slides_after'].append(number)
    return paragraphs

def _key(token):return re.sub(r'[^\w]+','',token.lower().replace('’',"'"))

def reparagraph(events):
    """Use the script literally; retain recording anchors as passage locators."""
    first=next(i for i,e in enumerate(events)if e['type']=='speech'and e['parts'][0]['anchor']=='r1-001543')
    last=next(i for i,e in enumerate(events)if e['type']=='speech'and e['parts'][-1]['anchor']=='r1-004817')
    selected=events[first:last+1];assert all(e['type']=='speech'for e in selected)
    entries=[p for e in selected for p in e['parts']]
    source=script_paragraphs();new=' '.join(p['text']for p in source)
    old_tokens=[];old_starts=[]
    for entry in entries:old_starts.append(len(old_tokens));old_tokens+=entry['text'].split()
    new_matches=list(re.finditer(r'\S+',new));new_tokens=[m[0]for m in new_matches]
    matcher=SequenceMatcher(None,[_key(t)for t in old_tokens],[_key(t)for t in new_tokens],autojunk=False)
    pairs=[(a+j,b+j)for a,b,size in matcher.get_matching_blocks()for j in range(size)]
    ox=[p[0]for p in pairs];positions=[]
    for index,old in enumerate(old_starts):
        k=bisect_left(ox,old)
        if k==len(pairs):k-=1
        if k and old-pairs[k-1][0]<pairs[k][0]-old:k-=1
        position=new_matches[pairs[k][1]].start()
        if index==0:position=0
        positions.append(position)
    assert positions==sorted(positions)
    ranges=[];cursor=0
    for p in source:ranges.append((cursor,cursor+len(p['text'])));cursor+=len(p['text'])+1
    replacement=[];emitted=set()
    for p,(a,b)in zip(source,ranges):
        cuts=sorted(set([a,b]+[v for v in positions if a<=v<b]));parts=[]
        for x,y in zip(cuts,cuts[1:]):
            at=[i for i,v in enumerate(positions)if v==x and i not in emitted]
            if not at:at=[max(0,bisect_right(positions,x)-1)]
            for i in at[:-1]:
                part=deepcopy(entries[i]);part.update(text='',emit_anchor=True,emit_reference=False);parts.append(part);emitted.add(i)
            i=at[-1];part=deepcopy(entries[i]);part.update(text=new[x:y].strip(),emit_anchor=i not in emitted,emit_reference=False)
            if i not in emitted:emitted.add(i)
            parts.append(part)
        replacement.append(dict(type='speech',paragraph=selected[0]['paragraph'],parts=parts,paragraph_id=p['id']))
    assert len(emitted)==len(entries),(len(emitted),len(entries))
    assert re.sub(r'\s+',' ',' '.join(p['text']for e in replacement for p in e['parts'])).strip()==re.sub(r'\s+',' ',new).strip()
    for entry in entries:
        destination=LAYOUT.get('reference_after_source_paragraph',{}).get(entry['anchor'])
        if destination:
            index=next(i for i,p in enumerate(source)if p['source_slide']==destination['slide']and p['source_paragraph']==destination['paragraph'])
            target=replacement[index]
        else:
            target=[e for e in replacement if any(p['anchor']==entry['anchor']for p in e['parts'])][-1]
        target['parts'][-1].setdefault('references',[]).append(entry['anchor'])
    LAYOUT['paragraphs']=[{k:p[k]for k in ['id','cue','source_slide','source_paragraph','slides_after']}for p in source]
    PATH.write_text(json.dumps(LAYOUT,ensure_ascii=False,indent=2)+'\n')
    return events[:first]+replacement+events[last+1:]
