// Execute the shipped, embedded web script in a deterministic mock browser.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('firmware/assets/ui.html','utf8');
const code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
class Element{
 constructor(id=''){this.id=id;this.value='';this.textContent='';this.listeners={};this.children=[];this.dataset={};this.classList={toggle:()=>{}};}
 addEventListener(n,f){(this.listeners[n]??=[]).push(f);}
 appendChild(e){this.children.push(e);return e;}
 replaceChildren(){this.children=[];}
 setPointerCapture(id){this.capture=id;}
 fire(name){for(const f of this.listeners[name]||[])f({currentTarget:this,pointerId:1,preventDefault(){}});}
}
const elements={};const el=id=>elements[id]??=(new Element(id));
for(const id of [...html.matchAll(/id="([^"]+)"/g)].map(m=>m[1]))el(id);
const dirs=Array.from({length:8},(_,i)=>{let e=new Element();e.dataset.dir=String(i+1);return e;});
const events={},timers=[],calls=[],beacons=[];let failMove=false,deferMove=null;
const document={hidden:false,getElementById:el,createElement:()=>new Element(),querySelectorAll:()=>dirs,addEventListener:(n,f)=>events[n]=f};
const fetch=async(path,options={})=>{
 const data=Object.fromEntries(options.body||[]);calls.push({path,data});
 if(path==='/api/move'&&deferMove)await deferMove;
 if(path==='/api/move'&&failMove)throw Error('offline');
 let response={};if(path==='/api/session')response={token:'42'};
 if(path==='/api/status')response={message:'Đã vào Wi-Fi',url:'http://192.168.1.2/',online:true,driver:true,assembly:false};
 if(path==='/api/scan')response={busy:false,networks:['Nhà tôi','<script>danger</script>']};
 if(path==='/api/trim')response={offset:1};
 return {ok:true,json:async()=>response};
};
const ctx=vm.createContext({document,window:{addEventListener:(n,f)=>events[n]=f},navigator:{sendBeacon:(path,data)=>beacons.push({path,data:Object.fromEntries(data)})},fetch,URLSearchParams,setInterval:(f,ms)=>timers.push({f,ms}),console});
vm.runInContext(code,ctx);
const flush=async()=>{for(let i=0;i<12;i++)await Promise.resolve();};
(async()=>{
 await flush();assert(calls.some(c=>c.path==='/api/session'));assert(timers.find(t=>t.ms===150));
 for(const d of dirs){d.fire('pointerdown');await flush();const last=calls.filter(c=>c.path==='/api/move').at(-1);assert.equal(last.data.dir,d.dataset.dir);assert.equal(last.data.fresh,'1');
  await timers.find(t=>t.ms===150).f();await flush();assert.equal(calls.filter(c=>c.path==='/api/move').at(-1).data.fresh,'0');
  d.fire('pointerup');assert.equal(beacons.at(-1).data.dir,'0');assert(Number(beacons.at(-1).data.seq)>Number(last.data.seq));
 }
 dirs[0].fire('pointerdown');await flush();events.blur();assert.equal(beacons.at(-1).data.dir,'0');
 dirs[1].fire('pointerdown');await flush();document.hidden=true;events.visibilitychange();assert.equal(beacons.at(-1).data.dir,'0');document.hidden=false;
 dirs[2].fire('pointerdown');await flush();events.pagehide();assert.equal(beacons.at(-1).data.dir,'0');
 dirs[3].fire('pointerdown');await flush();dirs[3].fire('pointercancel');assert.equal(beacons.at(-1).data.dir,'0');
 failMove=true;dirs[0].fire('pointerdown');await flush();assert.equal(beacons.at(-1).data.dir,'0');failMove=false;
 await el('showAssembly').onclick();await flush();assert(calls.some(c=>c.path==='/api/assembly'&&c.data.active==='1'));
 const before=calls.length;dirs[0].fire('pointerdown');await flush();assert(!calls.slice(before).some(c=>c.path==='/api/move'));
 assert.equal(el('trims').children.length,8);await el('trims').children[0].children[2].onclick();await flush();assert(calls.some(c=>c.path==='/api/trim'&&c.data.ch==='0'&&c.data.delta==='1'));
 await el('centre').onclick();await el('save').onclick();await el('done').onclick();await flush();assert(calls.some(c=>c.path==='/api/assembly'&&c.data.active==='0'));
 await el('showSetup').onclick();await el('scan').onclick();await flush();assert.equal(el('networks').children[1].textContent,'<script>danger</script>'); // never inserted as HTML
 el('ssid').value='Nhà tôi';el('password').value='secret-only-request';await el('connect').onclick();await flush();assert.equal(el('password').value,'');
 assert(calls.some(c=>c.path==='/api/wifi'&&c.data.password==='secret-only-request'));
 assert(!el('status').textContent.includes('secret-only-request'));
 assert(!/https?:\/\/(?!192\.168\.4\.1)/.test(html));assert(!/\b(?:src|href)=["']https?:/.test(html));
 console.log('PASS: shipped UI, 8 hold directions, keepalive, release/cancel/blur/hide, offline, Ráp lock/trim, Wi-Fi and password clearing');
})().catch(e=>{console.error(e);process.exit(1);});
