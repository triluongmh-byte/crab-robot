// Execute the shipped, embedded web script in a deterministic mock browser.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('firmware/assets/ui.html','utf8');
const code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
class Element{
 constructor(id=''){this.id=id;this.value='';this.textContent='';this.listeners={};this.children=[];this.dataset={};this.hidden=false;this.classList={toggle:(name,on)=>{if(name==='hidden')this.hidden=on;}};}
 addEventListener(n,f){(this.listeners[n]??=[]).push(f);}
 appendChild(e){this.children.push(e);return e;}
 replaceChildren(){this.children=[];}
 setPointerCapture(id){this.capture=id;}
 fire(name){for(const f of this.listeners[name]||[])f({currentTarget:this,pointerId:1,preventDefault(){}});}
}
const elements={};const el=id=>elements[id]??=(new Element(id));
for(const id of [...html.matchAll(/id="([^"]+)"/g)].map(m=>m[1]))el(id);
const dirs=Array.from({length:8},(_,i)=>{let e=new Element();e.dataset.dir=String(i+1);return e;});
const steps=[-20,-4,-1,0,1,4,20].map(step=>{let e=new Element();e.dataset.testStep=String(step);return e;});
const events={},timers=[],calls=[],beacons=[];let failMove=false,deferMove=null;
let statusReply={message:'Quét QR để nối cua',url:'http://192.168.4.1/',online:false,driver:true,assembly:false};
let failStatus=false;
const document={hidden:false,getElementById:el,createElement:()=>new Element(),querySelectorAll:s=>s==='[data-dir]'?dirs:steps,addEventListener:(n,f)=>events[n]=f};
const fetch=async(path,options={})=>{
 const data=Object.fromEntries(options.body||[]);calls.push({path,data});
 if(path==='/api/move'&&deferMove)await deferMove;
 if(path==='/api/move'&&failMove)throw Error('offline');
 let response={};if(path==='/api/session')response={token:'42'};
 if(path==='/api/status'){if(failStatus)throw Error('offline');response=statusReply;}
 if(path==='/api/scan')response={busy:false,networks:['Nhà tôi','<script>danger</script>']};
 if(path==='/api/trim')response={offset:1};
 return {ok:true,json:async()=>response};
};
const ctx=vm.createContext({document,window:{confirm:()=>true,addEventListener:(n,f)=>events[n]=f},navigator:{sendBeacon:(path,data)=>beacons.push({path,data:Object.fromEntries(data)})},fetch,URLSearchParams,setInterval:(f,ms)=>timers.push({f,ms}),console});
vm.runInContext(code,ctx);
const flush=async()=>{for(let i=0;i<12;i++)await Promise.resolve();};
(async()=>{
 await flush();
 const page=()=>vm.runInContext('page',ctx);
 const poll=async(count=40)=>{for(let i=0;i<count;i++){await timers.find(t=>t.ms===2000).f();await flush();}};
 assert.equal(page(),'control','AP/captive portal first load must land on control');
 await poll();assert.equal(page(),'control');assert(el('status').textContent.includes('Wi-Fi nhà là tùy chọn'));
 assert(calls.some(c=>c.path==='/api/session'));assert(timers.find(t=>t.ms===150));
 dirs[0].fire('pointerdown');await flush();const releases=beacons.length;
 await poll();assert.equal(page(),'control');assert.equal(beacons.length,releases,'offline polls must not release a valid hold');
 await timers.find(t=>t.ms===150).f();await flush();assert.equal(calls.filter(c=>c.path==='/api/move').at(-1).data.dir,'1');dirs[0].fire('pointerup');
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
 statusReply.assembly=true;await poll();assert.equal(page(),'assembly');assert(!el('assembly').hidden&&el('setup').hidden);
 const before=calls.length;dirs[0].fire('pointerdown');await flush();assert(!calls.slice(before).some(c=>c.path==='/api/move'));
 assert.equal(el('trims').children.length,8);await el('trims').children[0].children[2].onclick();await flush();assert(calls.some(c=>c.path==='/api/trim'&&c.data.ch==='0'&&c.data.delta==='1'));
 await el('centre').onclick();await el('save').onclick();await el('done').onclick();await flush();assert(calls.some(c=>c.path==='/api/assembly'&&c.data.active==='0'));
 await poll();assert.equal(page(),'control');
 await el('showSetup').onclick();assert.equal(page(),'setup');assert(!el('setup').hidden);await poll();assert.equal(page(),'setup');
 await el('scan').onclick();await flush();assert.equal(el('networks').children[1].textContent,'<script>danger</script>'); // never inserted as HTML
 el('ssid').value='Nhà tôi';el('password').value='secret-only-request';await el('connect').onclick();await flush();assert.equal(el('password').value,'');
 assert(calls.some(c=>c.path==='/api/wifi'&&c.data.password==='secret-only-request'));
 statusReply={...statusReply,message:'Sai mật khẩu hoặc mất sóng',assembly:false};
 await poll();assert.equal(page(),'setup');assert(el('status').textContent.includes('Sai mật khẩu'));
 assert(!el('status').textContent.includes('secret-only-request'));
 await el('showControl').onclick();await poll();assert.equal(page(),'control');
 await el('showAssembly').onclick();await poll();assert.equal(page(),'assembly');
 await el('done').onclick();failStatus=true;await poll(2);assert.equal(page(),'control');failStatus=false;
 await poll();assert.equal(page(),'control','reconnect must not force setup');
 statusReply={...statusReply,online:true,message:'Đã vào Wi-Fi',url:'http://192.168.1.2/'};
 await poll(2);assert.equal(page(),'control');assert(el('status').textContent.includes('192.168.1.2'));
 statusReply={...statusReply,online:false};await poll(2);assert.equal(page(),'control');
 // Note11 test page remains manual; polling does not navigate or emit pulses.
 await el('showTest').onclick();await flush();assert.equal(page(),'test');
 assert(calls.some(c=>c.path==='/api/test'&&c.data.active==='1'));
 const beforeTestPolls=calls.filter(c=>c.path==='/api/test/hold').length;
 statusReply={...statusReply,testActive:false,testChannel:0,neutralCounts:307,pulseCounts:307,emittedChannel:0};
 await poll();assert.equal(page(),'test');assert.equal(calls.filter(c=>c.path==='/api/test/hold').length,beforeTestPolls);
 assert(el('testCounts').textContent.includes('307 count ≈ 1499.0 µs'));
 for(const b of steps){b.fire('pointerdown');await flush();assert.equal(calls.at(-1).path,'/api/test/hold');assert.equal(calls.at(-1).data.step,b.dataset.testStep);assert.equal(calls.at(-1).data.fresh,'1');
  await timers.find(t=>t.ms===150).f();assert.equal(calls.at(-1).data.fresh,'0');b.fire('pointerup');assert.equal(beacons.at(-1).data.dir,'0');}
 steps[0].fire('pointerdown');await flush();vm.runInContext('testSince=Date.now()-2000',ctx);await timers.find(t=>t.ms===150).f();await flush();assert.equal(vm.runInContext('testHeld',ctx),null);
 steps[1].fire('pointerdown');await flush();events.blur();assert.equal(vm.runInContext('testHeld',ctx),null);
 steps[1].fire('pointerdown');await flush();document.hidden=true;events.visibilitychange();document.hidden=false;assert.equal(vm.runInContext('testHeld',ctx),null);
 steps[1].fire('pointerdown');await flush();steps[1].fire('pointercancel');assert.equal(vm.runInContext('testHeld',ctx),null);
 el('testChannel').value='3';await el('testChannel').onchange();await el('neutralUp').onclick();await flush();assert(calls.some(c=>c.path==='/api/test/config'&&c.data.neutral==='308'));
 await el('testDone').onclick();await flush();assert.equal(page(),'control');assert(calls.some(c=>c.path==='/api/test'&&c.data.active==='0'));
 el('actuatorMode').value='positional';await el('applyActuator').onclick();await flush();assert(calls.some(c=>c.path==='/api/actuator'&&c.data.confirm==='1'));
 el('actuatorMode').value='unknown';await el('applyActuator').onclick();await flush();assert(calls.some(c=>c.path==='/api/actuator'&&c.data.value==='unknown'));
 // Captive probe URL/reload executes this same script: no hidden setup redirect.
 const reopened=vm.createContext({document,window:{addEventListener:()=>{}},navigator:{sendBeacon:()=>{}},fetch,URLSearchParams,setInterval:()=>{},console});
 vm.runInContext(code,reopened);await flush();assert.equal(vm.runInContext('page',reopened),'control');
 assert(!/https?:\/\/(?!192\.168\.4\.1)/.test(html));assert(!/\b(?:src|href)=["']https?:/.test(html));
 console.log('PASS: manual one-servo page/count display/hold/release/2s local cap/blur/cancel/config/RAM selection, direct AP first load, 40 repeated offline polls on control/Ráp/setup, manual setup, wrong password, reconnect; shipped UI, 8 hold directions, keepalive, release/cancel/blur/hide, offline, Ráp lock/trim, Wi-Fi and password clearing');
})().catch(e=>{console.error(e);process.exit(1);});
