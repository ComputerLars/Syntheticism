/* Public defence: reading, recordings and the preserved slide states. */
'use strict';
let archive,record=1,mode='audio',slide=1,request=0;
const film=document.getElementById('film'),sound=document.getElementById('sound'),dock=document.getElementById('media-dock'),status=document.getElementById('media-status'),background=document.getElementById('background-toggle');
const current=()=>mode==='video'?film:sound;
function stopBackground(){document.body.classList.remove('video-background');background.setAttribute('aria-pressed','false');film.muted=false;film.controls=true}
async function playAt(number,time){
 const token=++request;record=number;const r=archive.recordings.find(x=>x.id===number),media=current(),url=mode==='video'?r.video:r.audio,seek=mode==='video'?Math.max(0,time-r.video_offset):time;
 dock.hidden=false;film.hidden=mode!=='video';sound.hidden=mode!=='audio';(mode==='video'?sound:film).pause();document.getElementById('record-label').textContent='Recording '+number+' · '+r.label;status.textContent='';
 try{
  if(media.dataset.source!==url){media.src=url;media.dataset.source=url;media.load();await new Promise((resolve,reject)=>{media.addEventListener('loadedmetadata',resolve,{once:true});media.addEventListener('error',()=>reject(Error('The recording could not be loaded.')),{once:true})})}
  if(token!==request)return;media.currentTime=Math.min(seek,Math.max(0,media.duration-.1));await media.play();
 }catch(error){if(token===request)status.textContent=error.message}
}
function openSlide(n){slide=Math.max(1,Math.min(archive.slides.length,n));const s=archive.slides[slide-1],dialog=document.getElementById('slide-view');document.getElementById('slide-image').src=s.src;document.getElementById('slide-image').alt=s.text;document.getElementById('slide-number').textContent=slide+' / '+archive.slides.length;document.getElementById('slide-title').textContent=s.title;document.getElementById('previous-slide').disabled=slide===1;document.getElementById('next-slide').disabled=slide===archive.slides.length;if(!dialog.open)dialog.showModal()}
document.addEventListener('click',ev=>{
 const b=ev.target.closest('button');if(!b||!archive)return;
 if(b.dataset.play){stopBackground();playAt(Number(b.dataset.play),Number(b.dataset.time))}
 else if(b.dataset.mode){const old=current(),r=archive.recordings.find(x=>x.id===record),time=old.currentTime+(mode==='video'?r.video_offset:0);old.pause();stopBackground();mode=b.dataset.mode;playAt(record,time||r.start)}
 else if(b.dataset.slide)openSlide(Number(b.dataset.slide));
});
background.addEventListener('click',()=>{if(!archive)return;if(document.body.classList.contains('video-background')){stopBackground();film.pause();dock.hidden=true;return}const r=archive.recordings.find(x=>x.id===record);sound.pause();mode='video';film.muted=true;film.controls=false;document.body.classList.add('video-background');background.setAttribute('aria-pressed','true');playAt(record,record===1?943:r.start)});
document.getElementById('close-media').addEventListener('click',()=>{request++;film.pause();sound.pause();dock.hidden=true;stopBackground()});
document.getElementById('reading-size').addEventListener('input',ev=>document.documentElement.style.setProperty('--reading',ev.target.value+'px'));
document.getElementById('previous-slide').addEventListener('click',()=>openSlide(slide-1));document.getElementById('next-slide').addEventListener('click',()=>openSlide(slide+1));document.getElementById('close-slide').addEventListener('click',()=>document.getElementById('slide-view').close());
document.getElementById('slide-view').addEventListener('keydown',ev=>{if(ev.key==='ArrowLeft'){ev.preventDefault();openSlide(slide-1)}if(ev.key==='ArrowRight'){ev.preventDefault();openSlide(slide+1)}});
for(const media of[film,sound])media.addEventListener('timeupdate',()=>{if(media!==current()||!archive)return;const r=archive.recordings.find(x=>x.id===record),time=media.currentTime+(mode==='video'?r.video_offset:0),prefix='r'+record+'-',nodes=[...document.querySelectorAll('.speech .source-anchor[id^="'+prefix+'"]')];let selected;for(const anchor of nodes){const a=anchor.id.slice(3,9),seconds=Number(a.slice(0,2))*3600+Number(a.slice(2,4))*60+Number(a.slice(4,6));if(seconds<=time)selected=anchor.closest('.speech')}const old=document.querySelector('.speech.playing');if(old!==selected){old?.classList.remove('playing');selected?.classList.add('playing')}});
fetch('assets/defence.json').then(r=>{if(!r.ok)throw Error('Archive data '+r.status);return r.json()}).then(d=>{archive=d}).catch(e=>{status.textContent=e.message;dock.hidden=false});
