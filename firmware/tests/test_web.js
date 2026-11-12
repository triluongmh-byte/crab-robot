// Execute the actual180-degree page; missing DOM IDs stay missing.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('firmware/assets/ui.html','utf8'),code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements={};class Element{
 constructor(){this.value='';this.textContent='';this.id='';this.listeners={};this.children=[];this.dataset={};this.disabled=false;this.classList={toggle:(n,v)=>{if(n==='hidden')this.hidden=v;}};}
 appendChild(e){this.children.push(e);if(e.id)elements[e.id]=e;return e;}replaceChildren(){this.children=[];}
 addEventListener(n,f){(this.listeners[n]??=[]).push(f);}setPointerCapture(){}
 fire(n){for(const f of this.listeners[n]||[])f({currentTarget:this,pointerId:1,preventDefault(){}});}
}
for(const m of html.matchAll(/id="([^"]+)"/g)){const e=new Element();e.id=m[1];elements[e.id]=e;}
const el=id=>{assert(elements[id],id+' must actually exist');return elements[id];};
const dirs=[...html.matchAll(/data-dir="(\d+)"/g)].map(m=>{let e=new Element();e.dataset.dir=m[1];e.disabled=true;return e;});
const events={},timers=[],calls=[],beacons=[];let failMove=false,failStatus=false,deferred=null;
const state={message:'Đã vào Wi-Fi',online:true,url:'http://192.168.4.1/',driver:true,positional:false,enabled:0,assembly:false,speed:0.4,offsets:Array(8).fill(0)};
const document={hidden:false,getElementById:id=>elements[id]||null,createElement:()=>new Element(),querySelectorAll:s=>s==='[data-dir]'?dirs:[],addEventListener:(n,f)=>events[n]=f};
const fetch=async(path,opt={})=>{const data=Object.fromEntries(opt.body||[]);calls.push({path,data});let d={};
 if(path==='/api/move'){if(deferred)await deferred;if(failMove)throw Error('offline');}
 if(path==='/api/status'){if(failStatus)throw Error('offline');d={...state};}
 if(path==='/api/session')d={token:'42'};
 if(path==='/api/actuator'){state.positional=data.value==='positional';state.enabled=0;}
 if(path==='/api/assembly')state.assembly=data.active==='1';
 if(path==='/api/trim')state.offsets[Number(data.ch)]+=Number(data.delta);
 if(path==='/api/scan')d={busy:false,networks:['Nhà tôi','<script>bad</script>']};
 return {ok:true,json:async()=>d};};
const ctx=vm.createContext({document,window:{addEventListener:(n,f)=>events[n]=f},navigator:{sendBeacon:(path,b)=>beacons.push({path,data:Object.fromEntries(b)})},fetch,URLSearchParams,setInterval:(f,ms)=>timers.push({f,ms}),console});vm.runInContext(code,ctx);
const flush=async()=>{for(let i=0;i<20;i++)await Promise.resolve();};
(async()=>{
 await flush();const poll=async()=>{await timers.find(t=>t.ms===1000).f();await flush();};const hold=()=>timers.find(t=>t.ms===150).f();
 assert(dirs.length===8&&dirs.every(b=>b.disabled));assert.equal(vm.runInContext('page',ctx),'control');
 const before=calls.length;dirs[0].fire('pointerdown');await flush();assert.equal(calls.length,before);await el('light').onclick();assert(calls.some(c=>c.path==='/api/light'));
 await el('arm').onclick();await flush();assert(state.positional&&dirs.every(b=>b.disabled));assert(calls.some(c=>c.path==='/api/actuator'&&c.data.confirm==='1'));
 state.enabled=8;await poll();assert(dirs.every(b=>!b.disabled));state.speed=1;el('speed').value='0.4';await poll();assert.equal(el('speed').value,'1');state.speed=0.4;await poll();assert.equal(el('speed').value,'0.4');
 for(const b of dirs){b.fire('pointerdown');await flush();let cmd=calls.filter(c=>c.path==='/api/move').at(-1);assert.equal(cmd.data.dir,b.dataset.dir);assert.equal(cmd.data.fresh,'1');await hold();await flush();assert.equal(calls.filter(c=>c.path==='/api/move').at(-1).data.fresh,'0');b.fire('pointerup');assert.equal(beacons.at(-1).data.dir,'0');}
 for(const event of ['blur','pagehide']){dirs[0].fire('pointerdown');await flush();events[event]();assert.equal(vm.runInContext('held',ctx),0);}
 dirs[0].fire('pointerdown');await flush();document.hidden=true;events.visibilitychange();assert.equal(vm.runInContext('held',ctx),0);document.hidden=false;
 dirs[1].fire('pointerdown');await flush();dirs[1].fire('pointercancel');assert.equal(beacons.at(-1).data.dir,'0');
 failMove=true;dirs[0].fire('pointerdown');await flush();assert.equal(vm.runInContext('held',ctx),0);failMove=false;
 await el('showAssembly').onclick();assert(state.assembly&&dirs.every(b=>b.disabled));assert.equal(el('trims').children.length,8);
 await el('centre').onclick();await el('stand').onclick();await el('trims').children[0].children[2].onclick();assert.equal(state.offsets[0],1);assert(el('trim0').textContent.includes('(1°)'));
 await el('save').onclick();await el('showSetup').onclick();assert.equal(vm.runInContext('page',ctx),'assembly');await el('done').onclick();assert(!state.assembly&&vm.runInContext('page',ctx)==='control');
 await el('disarm').onclick();assert(!state.positional&&dirs.every(b=>b.disabled));
 await el('showAssembly').onclick();await el('arm').onclick();assert(state.assembly&&state.positional);await el('done').onclick();
 state.enabled=8;await poll();let release;deferred=new Promise(r=>release=r);dirs[0].fire('pointerdown');await flush();dirs[0].fire('pointerup');release();deferred=null;await flush();assert.equal(vm.runInContext('held',ctx),0);
 await el('showSetup').onclick();state.online=false;for(let i=0;i<40;i++)await poll();assert.equal(vm.runInContext('page',ctx),'setup');
 await el('scan').onclick();assert.equal(el('networks').children[1].textContent,'<script>bad</script>');
 el('ssid').value='Home';el('password').value='example-password';await el('connect').onclick();assert.equal(el('password').value,'');assert(calls.some(c=>c.path==='/api/wifi'&&c.data.ssid==='Home'));
 failStatus=true;await poll();assert(dirs.every(b=>b.disabled));assert.equal(vm.runInContext('held',ctx),0);
 assert(!calls.some(c=>c.path.includes('/360')||c.path.includes('/test')));assert(!html.includes('id="show360"'));
 console.log('PASS: actual180-only UI, default off/explicit arm, enable8 readiness,8 directions/keepalive/release/blur/cancel/hide, disarm, assembly lock/centre/trim/save, delayed-response stop, AP page persistence, Wi-Fi scan/password clearing, legacy pages removed');
})().catch(e=>{console.error(e);process.exitCode=1;});
