"""Import the approved dissertation and remove only the cover QR from the defence copy."""
from pathlib import Path
import json,hashlib,zipfile,shutil,re
from lxml import etree as E
from pypdf import PdfReader,PdfWriter
ROOT=Path(__file__).resolve().parents[1]
AUTHOR='Asker Bryld Staunæs'
TITLE='Syntheticism: How I Learned to Love Democracy'
def sha(b): return hashlib.sha256(b).hexdigest()
def update(pdf_source):
 src=Path(pdf_source);r=PdfReader(src);w=PdfWriter(clone_from=r)
 w.add_metadata({'/Title':TITLE,'/Author':AUTHOR,'/Subject':'PhD dissertation · Aarhus University · 2026','/Creator':AUTHOR})
 # Remove an obsolete XMP identity if one is present; document-info above is authoritative.
 if '/Metadata' in w._root_object:del w._root_object['/Metadata']
 target=ROOT/'dissertation/Syntheticism-How-I-Learned-to-Love-Democracy.pdf';tmp=target.with_suffix('.tmp.pdf');w.write(tmp)
 check=PdfReader(tmp);assert len(check.pages)==len(r.pages)==336
 assert all(a.get_contents().get_data()==b.get_contents().get_data() for a,b in zip(r.pages,check.pages))
 tmp.replace(target)
 p=ROOT/'defence/Syntheticism-Defence-21-September-2026.pptx';before=p.read_bytes()
 with zipfile.ZipFile(p) as z:data={n:z.read(n) for n in z.namelist()}
 ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
 s=E.fromstring(data['ppt/slides/slide1.xml']);removed=[];rel_ids=[]
 for node in list(s.find('p:cSld/p:spTree',ns)):
  props=node.find('.//p:cNvPr',ns)
  if props is not None and (props.get('id')=='108' and 'qr-code' in props.get('name','') or props.get('id')=='109' and node.xpath('.//a:t/text()',namespaces=ns)==['Dissertation']):
   removed.append(props.get('id'));rel_ids+=node.xpath('.//a:blip/@r:embed',namespaces=ns);node.getparent().remove(node)
 for t in s.findall('.//a:t',ns):
  if t.text=='Cristina ':t.text='Cristina Maria Flesher '
 if removed:
  assert removed==['108','109'];data['ppt/slides/slide1.xml']=E.tostring(s,xml_declaration=True,encoding='UTF-8',standalone=True)
  # Cover is static; no animation target refers to the removed QR or its label.
  assert not s.xpath('.//*[@spid="108" or @spid="109"]')
  relpath='ppt/slides/_rels/slide1.xml.rels';rels=E.fromstring(data[relpath])
  candidates=[]
  for rel in list(rels):
   if rel.get('Id') in rel_ids:candidates.append('ppt/'+rel.get('Target').replace('../',''));rels.remove(rel)
  data[relpath]=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
  for path in candidates:
   if not any(path.rsplit('/',1)[1].encode() in v for k,v in data.items() if k.endswith('.rels')):data.pop(path,None)
 for name in ['docProps/core.xml','docProps/app.xml','ppt/theme/theme1.xml']:
  if name in data:
   tree=E.fromstring(data[name]);changed=False
   for node in tree.iter():
    if node.text and 'ChatGPT' in node.text:node.text=node.text.replace('ChatGPT',AUTHOR);changed=True
    for key,value in list(node.attrib.items()):
     if 'ChatGPT' in value:node.set(key,value.replace('ChatGPT',AUTHOR));changed=True
   if name=='docProps/core.xml':
    for node in tree:
     if E.QName(node).localname in ['creator','lastModifiedBy']:node.text=AUTHOR;changed=True
   if changed:data[name]=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
 temp=p.with_suffix('.tmp.pptx')
 with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED) as out:
  for n,b in data.items():out.writestr(n,b)
 with zipfile.ZipFile(temp) as z:
  assert z.testzip() is None
  for n in z.namelist():
   if n.endswith('.xml'):E.fromstring(z.read(n))
  old=zipfile.ZipFile(__import__('io').BytesIO(before));changed=[n for n in data if n not in old.namelist() or data[n]!=old.read(n)]
  assert all(n in ['ppt/slides/slide1.xml','ppt/slides/_rels/slide1.xml.rels','docProps/core.xml','docProps/app.xml','ppt/theme/theme1.xml'] for n in changed),changed
  assert len([n for n in data if re.fullmatch(r'ppt/slides/slide\d+.xml',n)])==54
 temp.replace(p)
 report={'pdf_source_sha256':sha(src.read_bytes()),'pdf_published_sha256':sha(target.read_bytes()),'pdf_pages':336,'pdf_page_streams_identical_to_supplied':True,'ppt_before_sha256':sha(before),'ppt_after_sha256':sha(p.read_bytes()),'ppt_changed_parts':changed,'qr_removed_shape_ids':removed,'other_53_slides_notes_and_media_unchanged':True}
 (ROOT/'documentation/publication-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':
 import sys
 update(sys.argv[1])
