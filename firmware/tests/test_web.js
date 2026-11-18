// Execute the actual180-degree page; missing DOM IDs stay missing.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('firmware/assets/ui.html','utf8'),code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements={};class Element{
 constructor(){this.value='';this.textContent='';this.id='';this.listeners={};this.children=[];this.dataset={};this.disabledWrites=0;this._disabled=false;this.capture=null;this.style={};this.cls=new Set();this.classList={toggle:(n,v)=>{v=v===undefined?!this.cls.has(n):!!v;if(v)this.cls.add(n);else this.cls.delete(n);if(n==='hidden')this.hidden=v;if(n==='holding')this.holding=v;},contains:n=>this.cls.has(n)};}
 getBoundingClientRect(){return {left:0,top:0,width:200,height:200};}
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
const events={},timers=[],calls=[],beacons=[];let failMove=false,failStatus=false,failTelemetry=false,mobile=false,deferred=null;
const state={message:'Đã vào Wi-Fi',online:true,url:'http://192.168.4.1/',driver:true,positional:false,enabled:0,assembly:false,speed:0.65,offsets:Array(8).fill(0)};
const samples=Array.from({length:8},(_,ch)=>({ch,known:true,active:false,angleDeg:null,pulseUs:null,counts:null}));
const document={body:new Element(),hidden:false,getElementById:id=>elements[id]||null,createElement:()=>new Element(),querySelectorAll:()=>[],addEventListener:(n,f)=>events[n]=f};
class FormData{constructor(){this.items=[];}append(k,v,name){this.items.push([k,name||v]);}[Symbol.iterator](){return this.items[Symbol.iterator]();}}
const location={reloads:0,reload(){this.reloads++;}};const timeouts=[];let otaReply={ok:true,d:{ok:true,restarting:true}};
const fetch=async(path,opt={})=>{const data=Object.fromEntries(opt.body||[]);calls.push({path,data});let d={};
 if(path.startsWith('/api/ota?')){if(deferred)await deferred;return {ok:otaReply.ok,json:async()=>otaReply.d};}
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
const ctx=vm.createContext({document,window:{matchMedia:()=>({matches:mobile}),addEventListener:(n,f)=>events[n]=f},navigator:{sendBeacon:(path,b)=>beacons.push({path,data:Object.fromEntries(b)})},fetch,URLSearchParams,FormData,location,setTimeout:(f,ms)=>timeouts.push({f,ms}),setInterval:(f,ms)=>timers.push({f,ms}),console});vm.runInContext(code,ctx);
const flush=async()=>{for(let i=0;i<20;i++)await Promise.resolve();};
(async()=>{
 await flush();const poll=async()=>{await timers.find(t=>t.ms===1000).f();await flush();};const hold=()=>timers.find(t=>t.ms===150).f();
 // Joystick pad is 200 px; these points sit on each of the 8 direction rays near the rim.
 const joy=el('joy'),P={1:[100,10],6:[164,36],4:[190,100],8:[164,164],2:[100,190],7:[36,164],3:[10,100],5:[36,36]};
 const press=(d,props={})=>joy.fire('pointerdown',{clientX:P[d][0],clientY:P[d][1],...props}),drag=(x,y,props={})=>joy.fire('pointermove',{clientX:x,clientY:y,...props});
 const off=()=>joy.classList.contains('off'),held=()=>vm.runInContext('held',ctx),lastMove=()=>calls.filter(c=>c.path==='/api/move').at(-1);
 assert(off()&&!/data-dir=/.test(html)&&el('joyKnob'));assert.equal(el('speed').value,'65');assert.equal(el('speedValue').textContent,'65%');assert.equal(vm.runInContext('page',ctx),'control');
 const before=calls.length;press(1);await flush();assert.equal(calls.length,before);assert(!joy.holding);assert(el('spinL').disabled&&el('spinR').disabled);el('spinL').fire('pointerdown');await flush();assert.equal(calls.length,before);await el('light').onclick();assert(calls.some(c=>c.path==='/api/light'));
 // Lamp button sits under the joystick and shows its state.
 state.lightOn=true;await poll();assert.equal(el('light').textContent,'💡 Đèn: bật');assert.equal(el('light').attributes['aria-pressed'],'true');state.lightOn=false;await poll();assert.equal(el('light').textContent,'💡 Đèn: tắt');
 assert.equal(el('power').textContent,'⚡ Servo: TẮT');assert(!el('power').disabled);
 await el('arm').onclick();await flush();assert(state.positional&&off());assert.equal(el('power').textContent,'⚡ Đang bật 0/8');assert(calls.some(c=>c.path==='/api/actuator'&&c.data.confirm==='1'));
 state.enabled=8;await poll();assert(!off());assert.equal(el('power').textContent,'⚡ Servo: BẬT');assert.equal(el('power').attributes['aria-pressed'],'true');state.speed=1;el('speed').value='40';await poll();assert.equal(el('speed').value,'100');state.speed=0.4;await poll();assert.equal(el('speed').value,'40');
 // Slider: dragging is not overwritten by polls; release sends a decimal fraction.
 el('speed').value='75';el('speed').oninput();assert.equal(el('speedValue').textContent,'75%');state.speed=0.4;await poll();assert.equal(el('speed').value,'75');
 el('speed').onchange();await flush();assert(calls.some(c=>c.path==='/api/speed'&&c.data.value==='0.75'&&c.data.token==='42'));state.speed=.75;await poll();assert.equal(el('speed').value,'75');
 // Armed state is spelled out on the disabled arm button, and Trạng thái lists details.
 assert(el('arm').disabled&&/Servo đang bật/.test(el('arm').textContent));
 const detail=el('statusDetail').children.map(x=>x.textContent);assert(detail.includes('Bật đủ 8/8')&&detail.includes('75%')&&detail.includes('Bình thường'));
 // Station signal strength row (v25).
 state.rssi=-58;await poll();assert(el('statusDetail').children.some(x=>x.textContent==='-58 dBm · mạnh'));state.rssi=-84;await poll();assert(el('statusDetail').children.some(x=>/-84 dBm · rất yếu/.test(x.textContent)));
 state.rssi=null;await poll();assert(vm.runInContext("rssiText(-65)",ctx)==='-65 dBm · khá'&&vm.runInContext("rssiText(-75)",ctx)==='-75 dBm · yếu');
 // Only the trot is left (v23): no gait picker or flick-hip slider.
 assert(!elements.gait&&!elements.flickHip&&!elements.flickHipBox&&/id="gaitHint">Hai cặp chân chéo/.test(html));
 // Brownout reset: servos stayed off, the page says why.
 state.brownoutHold=true;state.positional=false;state.enabled=0;await poll();assert.equal(el('readiness').textContent,'Sụt áp');assert(/sụt áp/.test(el('status').textContent)&&el('statusDetail').children.some(x=>x.textContent==='Sụt áp — servo chưa bật'));
 state.brownoutHold=false;state.updateHold=true;await poll();assert.equal(el('readiness').textContent,'Đã cập nhật');assert(/cập nhật firmware/.test(el('status').textContent)&&el('statusDetail').children.some(x=>x.textContent==='Vừa cập nhật — servo chưa bật'));
 state.updateHold=false;state.positional=true;state.enabled=8;await poll();assert(el('statusDetail').children.some(x=>x.textContent==='Bình thường'));
 // Heading trim slider posts signed whole percent; poll does not fight a drag.
 state.balance=0;await poll();assert.equal(el('balance').value,'0');el('balance').value='12';el('balance').oninput();assert.equal(el('balanceValue').textContent,'+12% phải');await poll();assert.equal(el('balance').value,'12');
 el('balance').onchange();await flush();assert(calls.some(c=>c.path==='/api/balance'&&c.data.value==='12'));state.balance=12;await poll();assert(el('statusDetail').children.some(x=>x.textContent==='+12% phải'));
 // Lamp colour picker beside the light button.
 state.lightColor='#00ff00';state.lightOn=true;await poll();assert.equal(el('lightColor').value,'#00ff00');el('lightColor').value='#ff8000';el('lightColor').oninput();await poll();assert.equal(el('lightColor').value,'#ff8000');el('lightColor').onchange();await flush();assert(calls.some(c=>c.path==='/api/lightcolor'&&c.data.value==='ff8000'&&c.data.token==='42'));
 // Knee lift slider.
 state.knee=45;await poll();assert.equal(el('knee').value,'45');el('knee').value='55';el('knee').oninput();assert.equal(el('kneeValue').textContent,'55°');await poll();assert.equal(el('knee').value,'55');
 el('knee').onchange();await flush();assert(calls.some(c=>c.path==='/api/knee'&&c.data.value==='55'));
 assert(/CH0 · Hông trước trái/.test(el('trim0').textContent)&&/CH6 · Hông sau phải/.test(el('trim6').textContent));
 // Joystick: each of the 8 rays drives that direction; holding keeps it alive; release stops.
 for(const d of [1,2,3,4,5,6,7,8]){press(d);await flush();assert.equal(lastMove().data.dir,String(d));assert.equal(lastMove().data.fresh,'1');assert(joy.holding&&joy.capture===1&&el('joyKnob').style.transform);await hold();await flush();assert.equal(lastMove().data.fresh,'0');assert.equal(lastMove().data.dir,String(d));joy.fire('pointerup');assert.equal(beacons.at(-1).data.dir,'0');assert(!joy.holding&&el('joyKnob').style.transform==='');assert.equal(el('joyDir').textContent,'Đứng yên');}
 // v35 spin buttons: hold ↺ = dir 9, ↻ = dir 10, renewed while held; release stops; off with the joystick.
 {const L=el('spinL'),R=el('spinR');assert(!L.disabled&&!R.disabled);
  assert.deepEqual(vm.runInContext('DIR_NAMES.slice(9)',ctx),['↺ Xoay trái','Xoay phải ↻']);
  for(const [b,d] of [[L,'9'],[R,'10']]){b.fire('pointerdown');await flush();assert.equal(lastMove().data.dir,d);assert.equal(lastMove().data.fresh,'1');assert(b.cls.has('holding')&&b.capture===1);
   await hold();await flush();assert.equal(lastMove().data.dir,d);assert.equal(lastMove().data.fresh,'0');assert.equal(el('joyDir').textContent,d==='9'?'↺ Xoay trái':'Xoay phải ↻');
   b.fire('pointerup');assert.equal(beacons.at(-1).data.dir,'0');assert(!b.cls.has('holding'));assert.equal(held(),0);}
  // a second finger on the joystick is ignored while spinning; DỪNG releases the button highlight
  L.fire('pointerdown',{pointerId:5});await flush();joy.fire('pointerdown',{pointerId:6,clientX:100,clientY:10});await flush();assert.equal(held(),9);
  el('stop').onclick();assert.equal(held(),0);assert(!L.cls.has('holding'));L.fire('pointerup',{pointerId:5});
  R.fire('pointerdown',{pointerType:'mouse',button:2});assert.equal(held(),0);}
 // Pressing the centre (dead zone) does not walk; dragging out picks a direction, swinging round changes it in place.
 let moves=calls.filter(c=>c.path==='/api/move').length;joy.fire('pointerdown',{clientX:105,clientY:95});await flush();assert(joy.holding&&held()===0);assert.equal(calls.filter(c=>c.path==='/api/move').length,moves);
 drag(100,20);await flush();assert.equal(lastMove().data.dir,'1');assert.equal(el('joyDir').textContent,'↑ Tiến');drag(185,100);await flush();assert.equal(lastMove().data.dir,'4');assert.equal(lastMove().data.fresh,'1');assert(joy.holding);
 // back to the centre: the crab stands, but the finger is still on the knob
 let bc=beacons.length;drag(102,100);assert.equal(beacons.length,bc+1);assert.equal(beacons.at(-1).data.dir,'0');assert(held()===0&&joy.holding);drag(100,15);await flush();assert.equal(lastMove().data.dir,'1');
 // a finger on the 22.5 deg boundary does not flicker: it stays in its sector until 8 deg past it
 const ray=deg=>{const r=deg*Math.PI/180;return [100+80*Math.sin(r),100-80*Math.cos(r)];};drag(...ray(28));await flush();assert.equal(held(),1);drag(...ray(33));await flush();assert.equal(held(),6);drag(...ray(15));await flush();assert.equal(held(),6);drag(...ray(10));await flush();assert.equal(held(),1);
 // the knob stops at the rim however far the finger goes
 drag(600,100);await flush();assert.equal(el('joyKnob').style.transform,'translate(66.0px,0.0px)');assert.equal(held(),4);joy.fire('pointerup');assert(held()===0&&el('joyKnob').style.transform==='');
 // a second finger cannot steal the stick
 press(1,{pointerId:3});await flush();press(2,{pointerId:4});drag(100,190,{pointerId:4});await flush();assert.equal(held(),1);joy.fire('pointerup',{pointerId:4});assert.equal(held(),1);joy.fire('pointerup',{pointerId:3});assert.equal(held(),0);
 // Arrow keys: one key = straight, two keys = diagonal, releasing all stops.
 joy.fire('keydown',{key:'ArrowUp'});await flush();assert.equal(lastMove().data.dir,'1');joy.fire('keydown',{key:'ArrowRight'});await flush();assert.equal(lastMove().data.dir,'6');joy.fire('keyup',{key:'ArrowUp'});await flush();assert.equal(lastMove().data.dir,'4');bc=beacons.length;joy.fire('keyup',{key:'ArrowRight'});assert(held()===0&&beacons.length===bc+1&&!joy.holding);
 assert.equal(vm.runInContext('joyDir(0.1,-0.1,0)',ctx),0);assert.equal(vm.runInContext('joyDir(-0.7,0.7,0)',ctx),7);assert.equal(vm.runInContext('joyDir(-0.7,-0.7,0)',ctx),5);

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
 assert(press(1,{pointerId:7}));await flush();assert(joy.holding&&joy.capture===7);
 state.message='Đã vào Wi-Fi — trạng thái thay đổi';await poll();
 assert(!off()&&joy.holding);assert.equal(held(),1);
 joy.fire('pointerup',{pointerId:8});events.pointerup({pointerId:8,preventDefault(){}});assert(joy.holding);
 assert(el('driveDeck').fire('contextmenu'));assert(el('driveDeck').fire('touchmove'));await hold();await flush();
 events.pointerup({pointerId:7,preventDefault(){}});assert(!joy.holding&&joy.capture===null);assert.equal(vm.runInContext('held',ctx),0);
 // Losing capture or readiness still stops immediately, never silently resumes.
 press(1);await flush();joy.fire('lostpointercapture');assert.equal(vm.runInContext('held',ctx),0);
 press(1);await flush();state.assembly=true;await poll();assert.equal(vm.runInContext('held',ctx),0);state.assembly=false;await poll();
 press(1,{pointerType:'mouse',button:2});assert.equal(vm.runInContext('held',ctx),0);
 assert(html.includes('grid-template-columns:minmax(300px,1fr) minmax(340px,430px)')&&html.includes('position:fixed')&&html.includes('overscroll-behavior:none')&&html.includes('-webkit-touch-callout:none'));
 assert.deepEqual(vm.runInContext('SECTORS',ctx).slice().sort(),[1,2,3,4,5,6,7,8]);

 // The mobile settings drawer owns its own scroll; opening it cancels hold.
 mobile=true;const telemetry=()=>timers.find(t=>t.ms===500).f();
 const countTelemetry=()=>calls.filter(c=>c.path==='/api/servos').length;
 let previousTelemetry=countTelemetry();await telemetry();assert.equal(countTelemetry(),previousTelemetry);
 press(1);await flush();el('menuButton').onclick();await flush();assert.equal(vm.runInContext('held',ctx),0);assert.equal(document.body.dataset.panel,'open');assert.equal(el('menuButton').attributes['aria-expanded'],'true');assert(countTelemetry()>previousTelemetry);
 samples[0]={ch:0,known:true,active:true,angleDeg:100.1,pulseUs:1556,counts:319};await telemetry();await flush();assert.equal(el('angle0').textContent,'100.1°');assert.equal(el('pulse0').textContent,'1556');assert.equal(el('counts0').textContent,'319');
 samples[0].active=false;await telemetry();await flush();assert.equal(el('angle0').textContent,'—');assert.equal(el('servoState0').textContent,'Tắt xung');
 press(1);await flush();failTelemetry=true;await telemetry();await flush();assert.equal(held(),1);assert.equal(el('angle0').textContent,'—');failTelemetry=false;joy.fire('pointerup');
 events.keydown({key:'Escape'});assert.equal(document.body.dataset.panel,'closed');assert.equal(el('menuButton').attributes['aria-expanded'],'false');previousTelemetry=countTelemetry();await telemetry();assert.equal(countTelemetry(),previousTelemetry);
 el('menuButton').onclick();el('backdrop').onclick();assert.equal(document.body.dataset.panel,'closed');mobile=false;
 for(const event of ['blur','pagehide']){press(1);await flush();events[event]();assert.equal(vm.runInContext('held',ctx),0);}
 press(1);await flush();document.hidden=true;events.visibilitychange();assert.equal(vm.runInContext('held',ctx),0);document.hidden=false;
 press(2);await flush();joy.fire('pointercancel');assert.equal(beacons.at(-1).data.dir,'0');
 failMove=true;press(1);await flush();assert.equal(vm.runInContext('held',ctx),0);failMove=false;
 await el('showAssembly').onclick();assert(state.assembly&&off());assert.equal(document.body.dataset.page,'assembly');assert.equal(el('trims').children.length,8);
 await el('centre').onclick();await el('stand').onclick();assert.deepEqual(el('trims').children[0].children.slice(1).map(b=>b.textContent),['−15','−3','−1','+1','+3','+15']);await el('trims').children[0].children[4].onclick();assert.equal(state.offsets[0],1);assert(el('trim0').textContent.includes('(1°)'));await el('trims').children[0].children[5].onclick();assert.equal(state.offsets[0],4);await el('trims').children[0].children[2].onclick();assert.equal(state.offsets[0],1);await el('trims').children[0].children[6].onclick();assert.equal(state.offsets[0],16);await el('trims').children[0].children[1].onclick();assert.equal(state.offsets[0],1); // v36 ±15 jump
 await el('save').onclick();await el('showSetup').onclick();assert.equal(vm.runInContext('page',ctx),'assembly');await el('done').onclick();assert(!state.assembly&&vm.runInContext('page',ctx)==='control');
 await el('disarm').onclick();assert(!state.positional&&off());
 // ⚡ beside the joystick: on → off → on
 state.enabled=0;await poll();assert.equal(el('power').textContent,'⚡ Servo: TẮT');await el('power').onclick();await flush();const lastAct=()=>calls.filter(c=>c.path==='/api/actuator').at(-1);assert(state.positional&&lastAct().data.value==='positional'&&lastAct().data.confirm==='1');state.enabled=8;await poll();await el('power').onclick();await flush();assert(!state.positional&&off());assert.equal(lastAct().data.value,'unknown');
 await el('showAssembly').onclick();await el('arm').onclick();assert(state.assembly&&state.positional);await el('done').onclick();
 state.enabled=8;await poll();let release;deferred=new Promise(r=>release=r);press(1);await flush();joy.fire('pointerup');release();deferred=null;await flush();assert.equal(vm.runInContext('held',ctx),0);
 await el('showSetup').onclick();state.online=false;for(let i=0;i<40;i++)await poll();assert.equal(vm.runInContext('page',ctx),'setup');
 await el('scan').onclick();assert.equal(el('networks').children[1].textContent,'<script>bad</script>');
 // Scan fills the SSID with the first network; the password is visible text (owner mistyped hidden ones).
 assert.equal(el('ssid').value,'Nhà tôi');assert(/id="password" type="text"/.test(html)&&/id="ssid"[^>]*autocapitalize="none"/.test(html)&&/id="password"[^>]*autocapitalize="none"/.test(html));
 el('ssid').value=' Home ';el('password').value='example-password';await el('connect').onclick();assert.equal(el('password').value,'example-password');assert(calls.some(c=>c.path==='/api/wifi'&&c.data.ssid==='Home'&&c.data.password==='example-password'));
 const wifiCalls=calls.filter(c=>c.path==='/api/wifi').length;el('ssid').value='';await el('connect').onclick();assert.equal(calls.filter(c=>c.path==='/api/wifi').length,wifiCalls);
 // OTA: PIN first, then file + 6 digits; polls pause during the upload; errors are shown.
 await el('otaPin').onclick();await flush();assert(calls.some(c=>c.path==='/api/ota/begin'&&c.data.token==='42')&&/6 số/.test(el('otaInfo').textContent));
 el('otaFile').files=[];el('otaCode').value='123456';await el('otaSend').onclick();assert(!calls.some(c=>c.path.startsWith('/api/ota?'))&&/Chọn file/.test(el('otaInfo').textContent));
 el('otaFile').files=[{name:'crab.ino.bin',size:860000}];el('otaCode').value='12345';await el('otaSend').onclick();assert(!calls.some(c=>c.path.startsWith('/api/ota?')));
 otaReply={ok:false,d:{error:'Mã sai hoặc hết hạn. Bấm Hiện mã để lấy mã mới.'}};el('otaCode').value='123456';await el('otaSend').onclick();await flush();
 assert(calls.some(c=>c.path==='/api/ota?token=42&pin=123456'&&c.data.firmware==='crab.ino.bin')&&/Mã sai/.test(el('otaInfo').textContent)&&!el('otaSend').disabled&&!vm.runInContext('otaBusy',ctx));
 let otaRelease;deferred=new Promise(r=>otaRelease=r);otaReply={ok:true,d:{ok:true,restarting:true}};const sending=el('otaSend').onclick();await flush();
 assert(el('otaSend').disabled&&vm.runInContext('otaBusy',ctx));const polls=calls.filter(c=>c.path==='/api/status').length;await poll();assert.equal(calls.filter(c=>c.path==='/api/status').length,polls); // no status poll mid-upload
 otaRelease();deferred=null;await sending;await flush();assert(/Nạp xong/.test(el('otaInfo').textContent));const t=timeouts.find(x=>x.ms===15000);assert(t);t.f();assert.equal(location.reloads,1);
 vm.runInContext('otaBusy=false',ctx);
 failStatus=true;await poll();assert(off()&&el('power').disabled);assert.equal(vm.runInContext('held',ctx),0);
 assert(!calls.some(c=>c.path.includes('/360')||c.path.includes('/test')));assert(!html.includes('id="show360"'));
 console.log('PASS: Wi-Fi signal row, OTA PIN/file/6-digit checks/upload error shown/polls paused/reload after success, Tự đi toggle (sensors/armed gating, DỪNG ends it, blur/sleep/menu do not), actual180-only UI, auto-arm/explicit arm, enable8 readiness, joystick 8-direction (dead zone, in-place swing, sticky sectors, rim clamp, one finger, arrow keys) + ⚡/💡 quick buttons, split UI/mobile drawer/read-only commanded telemetry/keepalive/captured hold through status polls/other-finger release/contextmenu/touchmove/global release/capture loss/blur/cancel/hide, disarm, assembly lock/centre/trim/save, delayed-response stop, AP page persistence, Wi-Fi scan/password clearing, legacy pages removed');
})().catch(e=>{console.error(e);process.exitCode=1;});
