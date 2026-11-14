// Execute the actual180-degree page; missing DOM IDs stay missing.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('firmware/assets/ui.html','utf8'),code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements={};class Element{
 constructor(){this.value='';this.textContent='';this.id='';this.listeners={};this.children=[];this.dataset={};this.disabledWrites=0;this._disabled=false;this.capture=null;this.classList={toggle:(n,v)=>{if(n==='hidden')this.hidden=v;if(n==='holding')this.holding=v;}};}
 focus(options){this.focusOptions=options;}
 setAttribute(k,v){(this.attributes??={})[k]=v;}
 appendChild(e){this.children.push(e);if(e.id)elements[e.id]=e;return e;}replaceChildren(){this.children=[];}
 get disabled(){return this._disabled;}set disabled(v){this.disabledWrites++;this._disabled=v;}
 addEventListener(n,f){(this.listeners[n]??=[]).push(f);}setPointerCapture(id){this.capture=id;}
 hasPointerCapture(id){return this.capture===id;}releasePointerCapture(){this.capture=null;}
 fire(n,props={}){let prevented=false;for(const f of this.listeners[n]||[])f({currentTarget:this,pointerId:1,pointerType:'touch',button:0,preventDefault(){prevented=true;},...props});return prevented;}
}
for(const m of html.matchAll(/id="([^"]+)"/g)){const e=new Element();e.id=m[1];elements[e.id]=e;}
const el=id=>{assert(elements[id],id+' must actually exist');return elements[id];};
const dirs=[...html.matchAll(/data-dir="(\d+)"/g)].map(m=>{let e=new Element();e.dataset.dir=m[1];e.disabled=true;return e;});
const events={},timers=[],calls=[],beacons=[];let failMove=false,failStatus=false,failTelemetry=false,mobile=false,deferred=null;
const state={message:'Đã vào Wi-Fi',online:true,url:'http://192.168.4.1/',driver:true,positional:false,enabled:0,assembly:false,speed:0.65,gait:'trot',offsets:Array(8).fill(0)};
const samples=Array.from({length:8},(_,ch)=>({ch,known:true,active:false,angleDeg:null,pulseUs:null,counts:null}));
const document={body:new Element(),hidden:false,getElementById:id=>elements[id]||null,createElement:()=>new Element(),querySelectorAll:s=>s==='[data-dir]'?dirs:[],addEventListener:(n,f)=>events[n]=f};
const fetch=async(path,opt={})=>{const data=Object.fromEntries(opt.body||[]);calls.push({path,data});let d={};
 if(path==='/api/move'){if(deferred)await deferred;if(failMove)throw Error('offline');}
 if(path==='/api/status'){if(failStatus)throw Error('offline');d={...state};}
 if(path==='/api/servos'){if(failTelemetry)throw Error('telemetry offline');d={kind:'commanded',feedback:false,sampledAtMs:1234,servos:samples.map(x=>({...x}))};}
 if(path==='/api/session')d={token:'42'};
 if(path==='/api/actuator'){state.positional=data.value==='positional';state.enabled=0;}
 if(path==='/api/assembly')state.assembly=data.active==='1';
 if(path==='/api/auto'){state.auto=data.active==='1';state.autoState='cruise';}
 if(path==='/api/trim')state.offsets[Number(data.ch)]+=Number(data.delta);
 if(path==='/api/scan')d={busy:false,networks:['Nhà tôi','<script>bad</script>']};
 return {ok:true,json:async()=>d};};
const ctx=vm.createContext({document,window:{matchMedia:()=>({matches:mobile}),addEventListener:(n,f)=>events[n]=f},navigator:{sendBeacon:(path,b)=>beacons.push({path,data:Object.fromEntries(b)})},fetch,URLSearchParams,setInterval:(f,ms)=>timers.push({f,ms}),console});vm.runInContext(code,ctx);
const flush=async()=>{for(let i=0;i<20;i++)await Promise.resolve();};
(async()=>{
 await flush();const poll=async()=>{await timers.find(t=>t.ms===1000).f();await flush();};const hold=()=>timers.find(t=>t.ms===150).f();
 assert(dirs.length===8&&dirs.every(b=>b.disabled));assert.equal(el('speed').value,'65');assert.equal(el('speedValue').textContent,'65%');assert.equal(vm.runInContext('page',ctx),'control');
 const before=calls.length;dirs[0].fire('pointerdown');await flush();assert.equal(calls.length,before);await el('light').onclick();assert(calls.some(c=>c.path==='/api/light'));
 await el('arm').onclick();await flush();assert(state.positional&&dirs.every(b=>b.disabled));assert(calls.some(c=>c.path==='/api/actuator'&&c.data.confirm==='1'));
 state.enabled=8;await poll();assert(dirs.every(b=>!b.disabled));state.speed=1;el('speed').value='40';await poll();assert.equal(el('speed').value,'100');state.speed=0.4;await poll();assert.equal(el('speed').value,'40');
 // Slider: dragging is not overwritten by polls; release sends a decimal fraction.
 el('speed').value='75';el('speed').oninput();assert.equal(el('speedValue').textContent,'75%');state.speed=0.4;await poll();assert.equal(el('speed').value,'75');
 el('speed').onchange();await flush();assert(calls.some(c=>c.path==='/api/speed'&&c.data.value==='0.75'&&c.data.token==='42'));state.speed=.75;await poll();assert.equal(el('speed').value,'75');
 // Armed state is spelled out on the disabled arm button, and Trạng thái lists details.
 assert(el('arm').disabled&&/Servo đang bật/.test(el('arm').textContent));
 const detail=el('statusDetail').children.map(x=>x.textContent);assert(detail.includes('Bật đủ 8/8')&&detail.includes('75%')&&detail.includes('Chéo'));
 // Flick hip slider only shows in flick; release posts whole degrees.
 assert(el('flickHipBox').hidden);state.gait='flick';state.flickHip=90;await poll();assert(!el('flickHipBox').hidden&&el('flickHip').value==='90');
 el('flickHip').value='60';el('flickHip').oninput();await poll();assert.equal(el('flickHip').value,'60');el('flickHip').onchange();await flush();
 assert(calls.some(c=>c.path==='/api/flickhip'&&c.data.value==='60'));state.flickHip=60;await poll();assert(el('statusDetail').children.some(x=>x.textContent==='Búng gối · hông 60°'));state.gait='trot';await poll();assert(el('flickHipBox').hidden);
 // Heading trim slider posts signed whole percent; poll does not fight a drag.
 state.balance=0;await poll();assert.equal(el('balance').value,'0');el('balance').value='12';el('balance').oninput();assert.equal(el('balanceValue').textContent,'+12% phải');await poll();assert.equal(el('balance').value,'12');
 el('balance').onchange();await flush();assert(calls.some(c=>c.path==='/api/balance'&&c.data.value==='12'));state.balance=12;await poll();assert(el('statusDetail').children.some(x=>x.textContent==='+12% phải'));
 // Lamp colour picker beside the light button.
 state.lightColor='#00ff00';state.lightOn=true;await poll();assert.equal(el('lightColor').value,'#00ff00');el('lightColor').value='#ff8000';el('lightColor').oninput();await poll();assert.equal(el('lightColor').value,'#ff8000');el('lightColor').onchange();await flush();assert(calls.some(c=>c.path==='/api/lightcolor'&&c.data.value==='ff8000'&&c.data.token==='42'));
 // Knee lift slider.
 state.knee=45;await poll();assert.equal(el('knee').value,'45');el('knee').value='55';el('knee').oninput();assert.equal(el('kneeValue').textContent,'55°');await poll();assert.equal(el('knee').value,'55');
 el('knee').onchange();await flush();assert(calls.some(c=>c.path==='/api/knee'&&c.data.value==='55'));
 assert(/CH0 · Hông trước trái/.test(el('trim0').textContent)&&/CH6 · Hông sau phải/.test(el('trim6').textContent));
 assert.equal(el('gait').value,'trot');assert(/chéo/.test(el('gaitHint').textContent));state.gait='pairs';await poll();assert.equal(el('gait').value,'pairs');assert(/trước và sau/.test(el('gaitHint').textContent));
 el('gait').value='trot';await el('gait').onchange();await flush();assert(calls.some(c=>c.path==='/api/gait'&&c.data.value==='trot'&&c.data.token==='42'));state.gait='flick';await poll();assert.equal(el('gait').value,'flick');assert(/búng/.test(el('gaitHint').textContent));state.gait='trot';await poll();assert.equal(el('gait').value,'trot');
 for(const b of dirs){b.fire('pointerdown');await flush();let cmd=calls.filter(c=>c.path==='/api/move').at(-1);assert.equal(cmd.data.dir,b.dataset.dir);assert.equal(cmd.data.fresh,'1');await hold();await flush();assert.equal(calls.filter(c=>c.path==='/api/move').at(-1).data.fresh,'0');b.fire('pointerup');assert.equal(beacons.at(-1).data.dir,'0');}

 // Tự đi: needs both sensors and armed servos; toggles /api/auto. Only DỪNG (or a
 // drive button) ends it: blur, sleep and the menu must not stop the robot.
 assert(el('auto').disabled&&/Chưa thấy cảm biến/.test(el('autoInfo').textContent));
 state.sonarOk=true;state.sonar=[120,400];state.autoSupported=true;await poll();assert(!el('auto').disabled&&/trái 120 cm · phải xa/.test(el('autoInfo').textContent));
 assert(el('statusDetail').children.some(x=>x.textContent==='trái 120 cm · phải xa')&&el('statusDetail').children.some(x=>x.textContent==='Tay'));
 await el('auto').onclick();await flush();assert(calls.some(c=>c.path==='/api/auto'&&c.data.active==='1'&&c.data.token==='42'));
 assert.equal(el('auto').textContent,'🤖 Đang tự đi');assert.equal(el('auto').attributes['aria-pressed'],'true');assert(/đang đi/.test(el('autoInfo').textContent));assert.equal(el('readiness').textContent,'🤖 Tự đi');
 const quiet=beacons.length;events.blur();events.pagehide();document.hidden=true;events.visibilitychange();document.hidden=false;el('menuButton').onclick();el('menuButton').onclick();assert.equal(beacons.length,quiet);
 state.autoState='halt';await poll();assert(/thấy vật cản/.test(el('autoInfo').textContent));
 el('stop').onclick();assert.equal(beacons.length,quiet+1);assert.equal(beacons.at(-1).data.dir,'0');
 state.auto=false;state.autoNote='Đã về lái tay';await poll();assert.equal(el('auto').textContent,'🤖 Tự đi');assert.equal(el('autoInfo').textContent,'Đã về lái tay');
 state.auto=true;await poll();await el('auto').onclick();await flush();assert.equal(calls.filter(c=>c.path==='/api/auto').at(-1).data.active,'0');assert(!state.auto);
 state.autoNote=null;state.sonarOk=false;state.sonar=[null,null];await poll();assert(el('auto').disabled);
 // Polls and unrelated touches must not interrupt the captured finger.
 const first=dirs[0];assert(first.fire('pointerdown',{pointerId:7}));await flush();assert(first.holding&&first.capture===7);
 const writes=dirs.map(b=>b.disabledWrites);state.message='Đã vào Wi-Fi — trạng thái thay đổi';await poll();
 assert.deepEqual(dirs.map(b=>b.disabledWrites),writes);assert.equal(vm.runInContext('held',ctx),Number(first.dataset.dir));
 first.fire('pointerup',{pointerId:8});events.pointerup({pointerId:8,preventDefault(){}});assert(first.holding);
 assert(el('driveDeck').fire('contextmenu'));assert(el('driveDeck').fire('touchmove'));await hold();await flush();
 events.pointerup({pointerId:7,preventDefault(){}});assert(!first.holding&&first.capture===null);assert.equal(vm.runInContext('held',ctx),0);
 // Losing capture or readiness still stops immediately, never silently resumes.
 first.fire('pointerdown');await flush();first.fire('lostpointercapture');assert.equal(vm.runInContext('held',ctx),0);
 first.fire('pointerdown');await flush();state.assembly=true;await poll();assert.equal(vm.runInContext('held',ctx),0);state.assembly=false;await poll();
 first.fire('pointerdown',{pointerType:'mouse',button:2});assert.equal(vm.runInContext('held',ctx),0);
 assert(html.includes('grid-template-columns:minmax(300px,1fr) minmax(340px,430px)')&&html.includes('position:fixed')&&html.includes('overscroll-behavior:none')&&html.includes('-webkit-touch-callout:none'));
 assert.deepEqual(dirs.map(x=>Number(x.dataset.dir)).sort(),[1,2,3,4,5,6,7,8]);

 // The mobile settings drawer owns its own scroll; opening it cancels hold.
 mobile=true;const telemetry=()=>timers.find(t=>t.ms===500).f();
 const countTelemetry=()=>calls.filter(c=>c.path==='/api/servos').length;
 let previousTelemetry=countTelemetry();await telemetry();assert.equal(countTelemetry(),previousTelemetry);
 first.fire('pointerdown');await flush();el('menuButton').onclick();await flush();assert.equal(vm.runInContext('held',ctx),0);assert.equal(document.body.dataset.panel,'open');assert.equal(el('menuButton').attributes['aria-expanded'],'true');assert(countTelemetry()>previousTelemetry);
 samples[0]={ch:0,known:true,active:true,angleDeg:100.1,pulseUs:1556,counts:319};await telemetry();await flush();assert.equal(el('angle0').textContent,'100.1°');assert.equal(el('pulse0').textContent,'1556');assert.equal(el('counts0').textContent,'319');
 samples[0].active=false;await telemetry();await flush();assert.equal(el('angle0').textContent,'—');assert.equal(el('servoState0').textContent,'Tắt xung');
 first.fire('pointerdown');await flush();failTelemetry=true;await telemetry();await flush();assert.equal(vm.runInContext('held',ctx),Number(first.dataset.dir));assert.equal(el('angle0').textContent,'—');failTelemetry=false;first.fire('pointerup');
 events.keydown({key:'Escape'});assert.equal(document.body.dataset.panel,'closed');assert.equal(el('menuButton').attributes['aria-expanded'],'false');previousTelemetry=countTelemetry();await telemetry();assert.equal(countTelemetry(),previousTelemetry);
 el('menuButton').onclick();el('backdrop').onclick();assert.equal(document.body.dataset.panel,'closed');mobile=false;
 for(const event of ['blur','pagehide']){dirs[0].fire('pointerdown');await flush();events[event]();assert.equal(vm.runInContext('held',ctx),0);}
 dirs[0].fire('pointerdown');await flush();document.hidden=true;events.visibilitychange();assert.equal(vm.runInContext('held',ctx),0);document.hidden=false;
 dirs[1].fire('pointerdown');await flush();dirs[1].fire('pointercancel');assert.equal(beacons.at(-1).data.dir,'0');
 failMove=true;dirs[0].fire('pointerdown');await flush();assert.equal(vm.runInContext('held',ctx),0);failMove=false;
 await el('showAssembly').onclick();assert(state.assembly&&dirs.every(b=>b.disabled));assert.equal(document.body.dataset.page,'assembly');assert.equal(el('trims').children.length,8);
 await el('centre').onclick();await el('stand').onclick();assert.deepEqual(el('trims').children[0].children.slice(1).map(b=>b.textContent),['−3','−1','+1','+3']);await el('trims').children[0].children[3].onclick();assert.equal(state.offsets[0],1);assert(el('trim0').textContent.includes('(1°)'));await el('trims').children[0].children[4].onclick();assert.equal(state.offsets[0],4);await el('trims').children[0].children[1].onclick();assert.equal(state.offsets[0],1);
 await el('save').onclick();await el('showSetup').onclick();assert.equal(vm.runInContext('page',ctx),'assembly');await el('done').onclick();assert(!state.assembly&&vm.runInContext('page',ctx)==='control');
 await el('disarm').onclick();assert(!state.positional&&dirs.every(b=>b.disabled));
 await el('showAssembly').onclick();await el('arm').onclick();assert(state.assembly&&state.positional);await el('done').onclick();
 state.enabled=8;await poll();let release;deferred=new Promise(r=>release=r);dirs[0].fire('pointerdown');await flush();dirs[0].fire('pointerup');release();deferred=null;await flush();assert.equal(vm.runInContext('held',ctx),0);
 await el('showSetup').onclick();state.online=false;for(let i=0;i<40;i++)await poll();assert.equal(vm.runInContext('page',ctx),'setup');
 await el('scan').onclick();assert.equal(el('networks').children[1].textContent,'<script>bad</script>');
 // Scan fills the SSID with the first network; the password is visible text (owner mistyped hidden ones).
 assert.equal(el('ssid').value,'Nhà tôi');assert(/id="password" type="text"/.test(html)&&/id="ssid"[^>]*autocapitalize="none"/.test(html)&&/id="password"[^>]*autocapitalize="none"/.test(html));
 el('ssid').value=' Home ';el('password').value='example-password';await el('connect').onclick();assert.equal(el('password').value,'example-password');assert(calls.some(c=>c.path==='/api/wifi'&&c.data.ssid==='Home'&&c.data.password==='example-password'));
 const wifiCalls=calls.filter(c=>c.path==='/api/wifi').length;el('ssid').value='';await el('connect').onclick();assert.equal(calls.filter(c=>c.path==='/api/wifi').length,wifiCalls);
 failStatus=true;await poll();assert(dirs.every(b=>b.disabled));assert.equal(vm.runInContext('held',ctx),0);
 assert(!calls.some(c=>c.path.includes('/360')||c.path.includes('/test')));assert(!html.includes('id="show360"'));
 console.log('PASS: Tự đi toggle (sensors/armed gating, DỪNG ends it, blur/sleep/menu do not), actual180-only UI, auto-arm/explicit arm, enable8 readiness, 8-direction (4 straight + 4 turning arcs) split UI/mobile drawer/read-only commanded telemetry/keepalive/captured hold through status polls/other-finger release/contextmenu/touchmove/global release/capture loss/blur/cancel/hide, disarm, assembly lock/centre/trim/save, delayed-response stop, AP page persistence, Wi-Fi scan/password clearing, legacy pages removed');
})().catch(e=>{console.error(e);process.exitCode=1;});
