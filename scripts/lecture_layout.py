"""Paragraph and slide placement for the opening lecture's reading edition."""
from pathlib import Path
from copy import deepcopy
import json

ROOT=Path(__file__).resolve().parents[1]
LAYOUT=json.loads((ROOT/'documentation/lecture-layout.json').read_text())

def reparagraph(events):
    """Reflow continuous speech without changing words or source-time anchors."""
    first=next(i for i,e in enumerate(events) if e['type']=='speech' and e['parts'][0]['anchor']=='r1-001543')
    last=next(i for i,e in enumerate(events) if e['type']=='speech' and e['parts'][-1]['anchor']=='r1-004817')
    selected=events[first:last+1]
    assert all(e['type']=='speech' for e in selected)
    entries=[p for e in selected for p in e['parts']]
    text='';ranges=[]
    for part in entries:
        if text:text+=' '
        start=len(text);text+=part['text'];ranges.append((start,len(text),part))
    boundaries=[]
    for p in LAYOUT['paragraphs']:
        phrase=p['starts_with']
        assert text.count(phrase)==1,(p['id'],phrase,text.count(phrase))
        boundaries.append(text.index(phrase))
    assert boundaries[0]==0 and boundaries==sorted(set(boundaries))
    boundaries.append(len(text));replacement=[]
    for i,p in enumerate(LAYOUT['paragraphs']):
        a,b=boundaries[i:i+2];parts=[]
        for x,y,original in ranges:
            lo,hi=max(a,x),min(b,y)
            if lo>=hi:continue
            part=deepcopy(original);part['text']=text[lo:hi].strip()
            part['emit_anchor']=lo==x
            part['emit_reference']=hi==y
            if part['text']:parts.append(part)
        assert parts
        replacement.append(dict(type='speech',paragraph=selected[0]['paragraph'],parts=parts,paragraph_id=p['id']))
    assert ' '.join(p['text'] for e in replacement for p in e['parts'])==' '.join(p['text'] for p in entries)
    return events[:first]+replacement+events[last+1:]
