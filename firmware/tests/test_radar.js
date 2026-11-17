// Execute the shipped radar page script against a minimal DOM, fake clock and fake robot.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('firmware/assets/radar.html','utf8'),code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements={};
class El{constructor(id='',tag=''){this.id=id;this.tag=tag;this.value='';this.textContent='';this.children=[];this.attrs={};this.className='';this.disabled=false;this.classList={on:new Set(),toggle:(c,v)=>v?this.classList.on.add(c):this.classList.on.delete(c)};}
 setAttribute(k,v){this.attrs[k]=String(v);if(k==='id')elements[v]=this;}appendChild(e){this.children.push(e);return e;}replaceChildren(){this.children=[];}
 insertBefore(e,ref){const i=this.children.indexOf(ref);if(i<0)this.children.push(e);else this.children.splice(i,0,e);return e;}
 get firstChild(){return this.children[0]||null;}get lastChild(){return this.children[this.children.length-1]||null;}
 removeChild(e){this.children.splice(this.children.indexOf(e),1);}remove(){}click(){this.clicked=true;}}
for(const m of html.matchAll(/id="([^"]+)"/g))elements[m[1]]=new El(m[1]);
elements.stopCm.value='25';elements.slowCm.value='45';
let now=1000;const timers=[],calls=[],beacons=[],listeners={};let robot,clip='',made=[];
const side=(cm,raw=cm,age=40)=>({cm,raw:cm===null?null:raw,age});
robot={t:5000,firmware:'positional180-v32',driver:true,positional:false,enabled:0,assembly:false,autoSupported:true,auto:false,state:'off',dir:0,avoids:0,stopCm:25,slowCm:45,maxCm:250,farCm:400,yawDeg:12,beamDeg:15,sides:[side(31),side(400)],events:[]};
const fetch=async(path,opt={})=>{const data=Object.fromEntries(opt.body||[]);calls.push({path,data});let d={ok:true};
 if(path==='/api/session')d={token:'42'};
 if(path==='/api/radar')d=JSON.parse(JSON.stringify(robot));
 if(path==='/api/actuator'){robot.positional=true;robot.enabled=8;}
 if(path==='/api/auto')robot.auto=data.active==='1';
 if(path==='/api/autotune'){robot.stopCm=Number(data.stop);robot.slowCm=Number(data.slow);}
 return {ok:true,json:async()=>d};};
const document={getElementById:id=>elements[id]||null,createElement:t=>{const e=new El('',t);made.push(e);return e;},createElementNS:(ns,t)=>new El('',t),
 addEventListener:(ev,f)=>{listeners['doc:'+ev]=f;},hidden:false,body:new El('body')};
class FakeDate extends Date{constructor(...a){super(...(a.length?a:[now]));}static now(){return now;}}
const ctx=vm.createContext({document,window:{addEventListener:(ev,f)=>{listeners[ev]=f;},prompt:()=>{}},navigator:{sendBeacon:(p,b)=>{beacons.push({p,data:Object.fromEntries(b)});return true;},clipboard:{writeText:async t=>{clip=t;}}},
 fetch,URLSearchParams,Blob:class{constructor(parts){this.text=parts.join('');}},URL:{createObjectURL:b=>{ctx.lastBlob=b;return 'blob:1';},revokeObjectURL:()=>{}},
 setTimeout:(f,ms)=>{const t={f,at:now+ms};timers.push(t);return t;},clearTimeout:t=>{const i=timers.indexOf(t);if(i>=0)timers.splice(i,1);},
 setInterval:(f,ms)=>{const t={f,at:now+ms,every:ms};timers.push(t);return t;},Date:FakeDate,JSON,Math,Number,String,Array,Object,Promise,Error,console});
vm.runInContext(code,ctx);
const C=ctx.window.CuaRadar;
const flush=async()=>{for(let i=0;i<40;i++)await Promise.resolve();};
async function advance(ms){const end=now+ms;for(;;){await flush();timers.sort((a,b)=>a.at-b.at);const t=timers[0];if(!t||t.at>end)break;now=t.at;if(t.every)t.at+=t.every;else timers.shift();t.f();}now=end;await flush();}
const texts=n=>[n.textContent].concat(...n.children.map(texts));
(async()=>{
 // Geometry: 0 deg = Tiến (up); the robot's left sensor (side 0, GPIO10/11) looks yaw degrees left.
 assert.deepEqual([...C.beam(0,12,15)],[-27,3]);assert.deepEqual([...C.beam(1,12,15)],[-3,27]);
 assert.deepEqual([...C.polar(100,0)],[0,-100]);assert.deepEqual([...C.polar(100,90)],[100,0]);assert(C.polar(200,-27)[0]<0&&C.polar(200,27)[0]>0);
 assert.equal(C.arcPath(100,-90,90),'M-100 0A100 100 0 0 1 100 0');assert(C.wedgePath(50,-10,10).startsWith('M0 0L'));
 assert.equal(C.zone(null,25,45,250),'lost');assert.equal(C.zone(400,25,45,250),'clear');assert.equal(C.zone(24,25,45,250),'stop');assert.equal(C.zone(25,25,45,250),'slow');assert.equal(C.zone(45,25,45,250),'ok');
 assert.deepEqual([...C.rings(100)],[25,50,75,100]);assert.deepEqual([...C.rings(250)],[50,100,150,200,250]);
 // Load: takes a session, then polls /api/radar every 200 ms with one request in flight.
 await advance(0);assert.equal(calls[0].path,'/api/session');assert.equal(C.state().token,'42');
 await advance(1000);const polls=calls.filter(c=>c.path==='/api/radar').length;assert(polls>=5&&polls<=6,polls);
 assert.equal(elements.cmL.textContent,'31 cm');assert.equal(elements.cmR.textContent,'xa');assert.equal(elements.sideL.className,'side slow');assert.equal(elements.sideR.className,'side clear');
 assert(!elements.auto.disabled&&/Tự đi/.test(elements.auto.textContent));
 const svgText=texts(elements.radar).join('|');assert(/Tiến/.test(svgText)&&/31/.test(svgText)&&/xa/.test(svgText));
 // A silent side greys out and blocks starting Tự đi.
 robot.sides[1]=side(null);await advance(400);assert.equal(elements.cmR.textContent,'—');assert(elements.auto.disabled);assert(/mất tín hiệu/.test(texts(elements.radar).join('|')));
 robot.sides[1]=side(120);await advance(400);assert(!elements.auto.disabled);
 // Tự đi: arms the servos first when off, waits for 8/8, then starts Auto.
 calls.length=0;const go=C.toggleAuto();await advance(1500);await go;
 const paths=calls.map(c=>c.path).filter(p=>p!=='/api/radar');assert.deepEqual(paths,['/api/actuator','/api/auto']);
 assert.equal(calls.find(c=>c.path==='/api/actuator').data.confirm,'1');assert.equal(calls.find(c=>c.path==='/api/auto').data.active,'1');
 await advance(400);assert(elements.auto.classList.on.has('on')&&/Đang tự đi/.test(elements.auto.textContent));
 // Auto transitions come once each, with the readings that caused them.
 robot.state='halt';robot.events=[[1,6000,'cruise',200,120,null],[2,6400,'halt',22,120,null]];await advance(600);
 robot.events.push([3,7000,'backoff',22,120,null]);await advance(600);
 const ev=C.state().rows.filter(r=>r[0]==='su_kien');assert.equal(ev.length,3);assert.deepEqual(ev[1].slice(2,5),[6400,22,120]);assert.equal(C.state().seenEvent,3);
 // Thresholds: dragging stop past slow pushes slow up; sent once after a pause, also while running.
 calls.length=0;elements.stopCm.value='50';elements.stopCm.oninput();assert.equal(elements.slowCm.value,55);
 elements.stopCm.value='52';elements.stopCm.oninput();await advance(300);assert.equal(calls.filter(c=>c.path==='/api/autotune').length,0);
 await advance(300);const tune=calls.filter(c=>c.path==='/api/autotune');assert.equal(tune.length,1);assert.deepEqual({...tune[0].data},{token:'42',stop:'52',slow:'57'});
 await advance(400);assert.equal(elements.stopVal.textContent,'52 cm');
 elements.slowCm.value='20';elements.slowCm.oninput();assert.equal(Number(elements.stopCm.value),15);await advance(500);
 // Hiding the page stops Tự đi (beacon), like the other pages.
 beacons.length=0;document.hidden=true;listeners['doc:visibilitychange']();assert.equal(beacons.length,1);assert.equal(beacons[0].p,'/api/auto');assert.deepEqual({...beacons[0].data},{token:'42',active:'0'});document.hidden=false;
 // DỪNG sends Auto off and a stand.
 beacons.length=0;elements.stop.onclick();assert.deepEqual(beacons.map(b=>b.p),['/api/auto','/api/move']);
 robot.auto=false;robot.state='off';await advance(400);
 // Lost link: noted once, backs off, recovers.
 const ok=ctx.fetch;let down=true;ctx.fetch=async(p,o)=>{if(down&&p==='/api/radar')throw Error('x');return ok(p,o);};
 vm.runInContext('fetch=globalThis.fetch',ctx);
 await advance(2000);const lostNotes=C.state().rows.filter(r=>r[15]==='Mất kết nối').length;assert.equal(lostNotes,1);
 down=false;await advance(4000);assert(C.state().rows.some(r=>r[15]==='Kết nối lại'));
 // CSV: header with geometry + thresholds, one row per sample/event/note; summary for chat.
 const csv=C.toCsv().split('\n');assert(csv[0].startsWith('# Cua Robot radar log'));assert(/xoay 12 do/.test(csv[2])&&/dung < 15 cm, ne < 20 cm/.test(csv[3]));
 assert.equal(csv[4],'kind,clock,robot_ms,left_cm,right_cm,left_raw,right_raw,left_age_ms,right_age_ms,state,dir,auto,stop_cm,slow_cm,avoids,note');
 assert.equal(csv.length,5+C.state().rows.length+1);assert(csv.some(l=>/^mau,\d\d:\d\d:\d\d\.\d{3},5000,31,120,/.test(l)));assert(csv.some(l=>l.startsWith('su_kien,')&&l.includes(',6400,22,120,')));
 const sum=C.summary();assert(/xoay tim duong 0/.test(sum)&&/dung \(halt\) 1/.test(sum)&&/Trai: gan nhat 31 cm/.test(sum)&&/6400 halt 22 120/.test(sum));
 elements.copy.onclick();await advance(10);assert.equal(clip,sum);
 elements.csv.onclick();assert(made.some(a=>a.clicked&&/^cua-radar-\d{8}-\d{4}\.csv$/.test(a.download)));assert.equal(ctx.lastBlob.text,C.toCsv());
 // Range toggle and the log cap.
 elements.range.onclick();assert.equal(C.state().range,250);assert(/2,5 m/.test(elements.range.textContent));
 elements.clear.onclick();assert.equal(C.state().rows.length,0);
 console.log('PASS: radar page geometry (robot left = screen left)/zones/rings, session + 5 Hz single-flight polling, stale side greys out and blocks Tự đi, Tự đi arms then starts, events once with readings, thresholds push/debounce/send, hide and DỪNG stop Auto, link loss noted once and recovers, CSV/summary/download');
})().catch(e=>{console.error(e);process.exit(1);});
