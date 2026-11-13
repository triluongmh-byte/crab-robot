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
 // Physical front-left (slider leg 0) is CH0/CH1; CH6 is the rear right.
 assert.equal(E.toCommand([10,20,10,20,-5,0,-5,0]),'-10,-20,10,-20,5,0,-5,0');
 assert.equal(E.toCommand([99,-99,0,0,0,0,0,0]),'-30,30,0,0,0,0,0,0');
 assert.deepEqual({...E.hexRgb('#ff4000')},{r:255,g:64,b:0});
 // Every preset frame is 8 bounded angles, a colour, move and hold times; ends standing.
 for(const p of E.PRESETS){assert(p.f.length>=2);for(const f of p.f){assert.equal(f.length,11);for(let i=0;i<8;i++)assert(Math.abs(f[i])<=30);assert(/^#[0-9a-f]{6}$/i.test(f[8]));assert(f[9]>=0&&f[9]<=3000&&f[10]>=0&&f[10]<=5000);}
  assert(p.f.at(-1).slice(0,8).every(v=>v===0));}
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
 console.log('PASS: emotion page unit mapping/preset bounds/saved-list filter/timeline renewals with fresh-first lease/colour changes/stop at end and on halt');
})().catch(e=>{console.error(e);process.exit(1);});
