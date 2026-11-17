// Execute the shipped emotion page script against a minimal DOM and fake clock.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('firmware/assets/emote.html','utf8'),code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements={};
class El{constructor(id=''){this.id=id;this.value='';this.textContent='';this.children=[];this.style={};this.checked=false;this.disabled=false;}
 appendChild(e){this.children.push(e);if(e.id)elements[e.id]=e;return e;}append(...es){for(const e of es)this.appendChild(typeof e==='string'?new El():e);}replaceChildren(){this.children=[];}}
for(const m of html.matchAll(/id="([^"]+)"/g))elements[m[1]]=new El(m[1]);
elements.color.value='#ffc400';elements.ms.value='300';elements.hold.value='0';elements.mirror.checked=true;
let now=1000;const timers=[],intervals=[],calls=[],beacons=[];
const document={getElementById:id=>elements[id]||null,createElement:()=>new El(),addEventListener:()=>{},hidden:false};
const fetch=async(path,opt={})=>{const data=Object.fromEntries(opt.body||[]);calls.push({path,data});let d={ok:true};
 if(path==='/api/session')d={token:'42'};if(path==='/api/status')d={driver:true,positional:true,enabled:8,assembly:false};
 if(path==='/api/emotions')d=[{n:'Mine',f:[[0,0,0,0,0,0,0,0,'#000000',100,0]]},{bad:1}];
 return {ok:true,json:async()=>d};};
const FakeDate={now:()=>now};
const ctx=vm.createContext({document,window:{addEventListener:()=>{}},navigator:{sendBeacon:(p,b)=>beacons.push({p,data:Object.fromEntries(b)})},fetch,URLSearchParams,
 setTimeout:(f,ms)=>{timers.push({f,at:now+ms});},setInterval:(f,ms)=>intervals.push({f,ms}),Date:FakeDate,JSON,Math,Number,String,Array,Object,Promise,Error,parseInt,console});
vm.runInContext(code,ctx);
const E=ctx.window.CuaEmote;
const flush=async()=>{for(let i=0;i<30;i++)await Promise.resolve();};
async function advance(ms){const end=now+ms;for(;;){await flush();timers.sort((a,b)=>a.at-b.at);const t=timers[0];if(!t||t.at>end)break;timers.shift();now=t.at;t.f();}now=end;await flush();}
(async()=>{
 await flush();
 // Page units -> firmware frame: left hips negate (forward), knees negate (lift).
 // Owner leg names: front-left slider (leg 0) is CH0/CH1, rear right CH6/CH7.
 assert.equal(E.toCommand([10,20,10,20,-5,0,-5,0]),'-10,-20,10,-20,5,0,-5,0');
 assert.equal(E.toCommand([99,-99,0,0,0,0,0,0]),'-99,99,0,0,0,0,0,0');assert.equal(E.toCommand([999,-999,0,0,0,0,0,0]),'-170,170,0,0,0,0,0,0');
 assert.deepEqual({...E.hexRgb('#ff4000')},{r:255,g:64,b:0});
 // Every preset frame is 8 bounded angles, a colour, move and hold times; ends standing.
 // Owner, 2026-11-16: each slider moves only its own joint unless Đối xứng is ticked.
assert(!/id="mirror"[^>]*checked/.test(html));
// Chào (v34): CH3's knee lifts high (150) and waves down to 95; it maps to CH3 in the command, the others hold.
{const hi=E.PRESETS.find(p=>p.n==='👋 Chào');assert(hi&&hi.f.some(f=>f[3]===150)&&hi.f.some(f=>f[3]===95));const c=vm.runInContext("toCommand(PRESETS.find(p=>p.n==='👋 Chào').f[0])",ctx).split(',').map(Number);assert.equal(c[3],-150);assert(c.every((v,i)=>i===3||Math.abs(v)<=35));
 assert.equal(vm.runInContext('clampKnee(199)',ctx),170);assert.equal(vm.runInContext('clampKnee(-199)',ctx),-170);assert.equal(vm.runInContext('clampDeg(99)',ctx),99);}
// v33 "Mở hết biên": sliders start at hips +-30 / knees -30..100, open to +-170, and close back clamping values.
assert.equal(elements.j0.max,30);assert.equal(elements.j1.max,100);assert.equal(elements.j1.min,-30);assert(!elements.wide.checked);
E.setWide(true);assert.equal(elements.j0.min,-170);assert.equal(elements.j0.max,170);assert.equal(elements.j1.max,170);
elements.j1.value='150';E.setWide(false);assert.equal(Number(elements.j1.value),100);assert.equal(elements.v1.textContent,'100°');
// Opening a frame with big angles turns it on so they are not cut.
E.writeEditor([0,150,0,0,-120,0,0,0,'#ffffff',300,0]);assert(elements.wide.checked);assert.equal(elements.j1.max,170);
E.setWide(false);E.writeEditor([0,0,0,0,0,0,0,0,'#ffffff',300,0]);
// v34 bounds: hips +-40, knees -55..150; never more than one leg lifted past 80 (it would fall);
// front and rear hips of one side never converge by more than 20 deg each; big moves get time.
let widest=0;
for(const p of E.PRESETS){assert(p.f.length>=2);let prev=Array(8).fill(0);for(const f of p.f){assert.equal(f.length,11);for(let i=0;i<8;i++)assert(i%2?f[i]>=-55&&f[i]<=150:Math.abs(f[i])<=40,p.n);
  assert([1,3,5,7].filter(i=>f[i]>80).length<=1,p.n);assert(f[0]-f[4]>=-40&&f[2]-f[6]>=-40,p.n);
  const step=Math.max(...f.slice(0,8).map((v,i)=>Math.abs(v-prev[i])));assert(step<50||f[9]>=150,p.n+' '+step);prev=f.slice(0,8);
  widest=Math.max(widest,...f.slice(0,8).map(Math.abs));assert(/^#[0-9a-f]{6}$/i.test(f[8]));assert(f[9]>=0&&f[9]<=3000&&f[10]>=0&&f[10]<=5000);}
  assert(p.f.at(-1).slice(0,8).every(v=>v===0));}
assert(widest>=150);for(const p of E.PRESETS)assert(p.f.some(f=>f.slice(0,8).some(v=>Math.abs(v)>30)),p.n+' should use the wider range');
 assert.equal(elements.presets.children.length,E.PRESETS.length);
 assert.equal(elements.legs.children.length,4);
 // Saved list ignores malformed entries.
 assert.equal(E.state().saved.length,1);
 // Playback: first pose fresh, renewals every 150 ms with shrinking move time, colour once per change, stop at end.
 E.setReady(true);calls.length=0;beacons.length=0;
 const frames=[[0,30,0,30,0,30,0,30,'#ff0000',300,200],[0,0,0,0,0,0,0,0,'#00ff00',0,0]];
 const done=E.playFrames(frames,false);await advance(2000);await done;
 const poses=calls.filter(c=>c.path==='/api/pose');
 assert(poses.length>=4,'renewed while moving and holding');
 assert.equal(poses[0].data.fresh,'1');assert(poses.slice(1).every(c=>c.data.fresh==='0'));
 assert.equal(poses[0].data.a,'0,-30,0,-30,0,-30,0,-30');assert.equal(poses[0].data.ms,'300');
 assert(Number(poses[1].data.ms)<300&&Number(poses[1].data.ms)>=0);
 const seqs=poses.map(c=>Number(c.data.seq));for(let i=1;i<seqs.length;i++)assert(seqs[i]>seqs[i-1]);
 const leds=calls.filter(c=>c.path==='/api/led');assert.equal(leds.length,2);assert.equal(leds[0].data.r,'255');assert.equal(leds[1].data.g,'255');
 assert.equal(beacons.length,1);assert.equal(beacons[0].data.dir,'0');
 // Stop interrupts a looping playback.
 calls.length=0;beacons.length=0;const loop=E.playFrames(frames,true);await advance(400);E.halt();await advance(1000);await loop;
 const after=calls.filter(c=>c.path==='/api/pose').length;await advance(1000);assert.equal(calls.filter(c=>c.path==='/api/pose').length,after);
 assert(beacons.length>=1);
 // Touching a slider starts live preview (owner: sliders looked dead); not ready -> hint.
 E.halt();await advance(500);calls.length=0;E.setReady(false);elements.j0.value='12';elements.j0.oninput();await advance(300);assert(!E.state().liveOn&&/Bật servo/.test(elements.status.textContent));assert.equal(calls.filter(c=>c.path==='/api/pose').length,0);
 E.setReady(true);elements.j0.value='12';elements.j0.oninput();assert(E.state().liveOn);await advance(400);
 const live=calls.filter(c=>c.path==='/api/pose');assert(live.length>=2&&live[0].data.fresh==='1');assert.equal(live[0].data.a.split(',')[0],'-12'); // front-left hip = CH0
 assert.equal(elements.j2.value,'12'); // mirrored to front-right
 E.halt();await advance(500);assert(!E.state().liveOn);
 // Eye moods: every preset names one; playback sends it once, frames may override.
 const moods=['normal','happy','sad','angry','sleepy','surprised','love','asleep','wink'];assert.deepEqual([...E.MOODS],moods);
 for(const p of E.PRESETS)assert(moods.includes(p.e)&&p.e!=='normal',p.n);
 calls.length=0;const sad=E.PRESETS.find(p=>p.e==='sad');let run=E.playFrames(sad.f,false,sad.e);await advance(8000);await run;
 const eyeCalls=calls.filter(c=>c.path==='/api/eyes');assert.equal(eyeCalls.length,1);assert.equal(eyeCalls[0].data.mood,'sad');assert.equal(eyeCalls[0].data.token,'42');
 calls.length=0;run=E.playFrames([[0,0,0,0,0,0,0,0,'#ff0000',0,0,'love'],[0,0,0,0,0,0,0,0,'#ff0000',0,0]],false,'happy');await advance(1000);await run;
 assert.deepEqual(calls.filter(c=>c.path==='/api/eyes').map(c=>c.data.mood),['love','happy']);
 // After a stop the same colour/mood is sent again on the next play (lamp/eyes were restored).
 calls.length=0;run=E.playFrames([[0,0,0,0,0,0,0,0,'#ff0000',0,0]],false,'happy');await advance(500);await run;
 assert.equal(calls.filter(c=>c.path==='/api/led').length,1);assert.equal(calls.filter(c=>c.path==='/api/eyes').length,1);
 // Live preview that loses readiness turns itself off, so the next slider move restarts it.
 E.setReady(true);elements.j0.value='5';elements.j0.oninput();await advance(300);assert(E.state().liveOn);
 E.setReady(false);await advance(400);assert(!E.state().liveOn);
 E.setReady(true);calls.length=0;elements.j0.value='6';elements.j0.oninput();await advance(300);assert(E.state().liveOn&&calls.some(c=>c.path==='/api/pose'));E.halt();await advance(300);
 console.log('PASS: emotion page unit mapping/preset bounds/saved-list filter/timeline renewals with fresh-first lease/colour changes/stop at end and on halt/eye moods per preset and frame/live preview recovers after lost readiness');
})().catch(e=>{console.error(e);process.exit(1);});
