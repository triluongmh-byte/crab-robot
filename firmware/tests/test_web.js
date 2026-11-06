'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const root=require('path').resolve(__dirname,'../..');
const html=fs.readFileSync(root+'/firmware/crab/Web.cpp','utf8').split('R"WEB(')[1].split(')WEB"')[0];
const script=html.match(/<script>([\s\S]*)<\/script>/)[1];
class Element {
 constructor(tag='div'){this.tag=tag;this.listeners={};this.children=[];this.dataset={};this.hidden=false;this.disabled=false;this.textContent='';this.value='';this.classes=new Set();this.classList={add:c=>this.classes.add(c),remove:c=>this.classes.delete(c)};}
 addEventListener(name,fn){this.listeners[name]=fn;}
 append(x){this.children.push(x);}
 replaceChildren(){this.children=[];}
 setAttribute(){} setPointerCapture(){}
}
const elements={};for(const id of ['notice','setup','drive','assembly','scan','ssid','wifi','password','join','stop','light','trims','center','save','reset','exit'])elements[id]=new Element();
const dirs=['fl','forward','fr','left','right','bl','back','br'];const buttons=dirs.map(dir=>{const e=new Element('button');e.dataset.dir=dir;return e;});
const calls=[],beacons=[],intervals=new Map(),events={};let nextTimer=1,fail=false;
const status={wifi:'Đã vào Wi-Fi',online:true,ready:true,assembly:false,fault:false,light:false,trim:[0,0,0,0,0,0,0,0]};
const ctx=vm.createContext({console,URLSearchParams,AbortSignal,crypto:crypto.webcrypto,location:{pathname:'/',href:'/'},
 document:{hidden:false,getElementById:id=>elements[id]||(elements[id]=new Element()),createElement:tag=>new Element(tag),querySelectorAll:selector=>selector==='[data-dir]'?buttons:buttons.filter(b=>b.classes.has('held')),addEventListener:(name,fn)=>events[name]=fn},
 window:{addEventListener:(name,fn)=>events[name]=fn},navigator:{sendBeacon:(path,body)=>{beacons.push({path,args:Object.fromEntries(body)});return true;}},
 setInterval:fn=>{const id=nextTimer++;intervals.set(id,fn);return id;},clearInterval:id=>intervals.delete(id),setTimeout:()=>{},
 fetch:async(path,options={})=>{calls.push({path,args:options.body?Object.fromEntries(options.body):{}});if(fail)throw Error('offline');return {ok:true,json:async()=>path==='/api/status'?status:path==='/api/scan'?{pending:false,ssids:['Home','<img src=x onerror=alert(1)>']}:{message:'OK'}};}
});
vm.runInContext(script,ctx);
const flush=()=>new Promise(r=>setImmediate(r));
const run=code=>vm.runInContext(code,ctx);
const pointer={button:0,pointerId:1,preventDefault(){}};
(async()=>{
 await flush();run('state='+JSON.stringify(status));
 assert.equal(buttons.length,8);assert.equal(elements.trims.children.length,8);
 buttons[1].listeners.pointerdown(pointer);await flush();
 assert.equal(calls.at(-1).path,'/api/move');assert.equal(calls.at(-1).args.dir,'forward');assert.equal(intervals.size,1);
 const firstSeq=Number(calls.at(-1).args.seq);await [...intervals.values()][0]();await flush();assert(Number(calls.at(-1).args.seq)>firstSeq);
 buttons[1].listeners.pointerup();assert.equal(intervals.size,0);assert.equal(beacons.at(-1).path,'/api/stop');const stopSeq=Number(beacons.at(-1).args.seq);assert(stopSeq>Number(calls.at(-1).args.seq));
 const count=calls.length;await run('beat()');assert.equal(calls.length,count);
 for(const event of ['pointercancel','lostpointercapture']){buttons[0].listeners.pointerdown(pointer);await flush();buttons[0].listeners[event]();assert.equal(intervals.size,0);}
 for(const event of ['blur','offline','pagehide']){buttons[0].listeners.pointerdown(pointer);await flush();events[event]();assert.equal(intervals.size,0);}
 buttons[0].listeners.pointerdown(pointer);await flush();ctx.document.hidden=true;events.visibilitychange();assert.equal(intervals.size,0);ctx.document.hidden=false;
 run('state.assembly=true');const prev=calls.length;buttons[1].listeners.pointerdown(pointer);await flush();assert.equal(calls.length,prev);run('state.assembly=false');
 buttons[2].listeners.pointerdown(pointer);await flush();fail=true;await run('beat()');assert.equal(intervals.size,0);assert(elements.notice.textContent.includes('Đã dừng'));fail=false;
 await run('scan()');const options=elements.ssid.children;assert.equal(options.length,2);assert.equal(options[1].textContent,'<img src=x onerror=alert(1)>');
 assert(!html.match(/<script[^>]+src=|<link[^>]+href=|https?:\/\/[^<\s]*(cdn|google)/i));
 assert(html.includes('lang="vi"'));assert(html.includes('type="password"'));assert(html.includes("setInterval(beat,200)"));
 buttons[3].listeners.keydown({key:' ',repeat:false,preventDefault(){}});await flush();assert(intervals.size===1);buttons[3].listeners.keyup({key:' '});assert.equal(intervals.size,0);
 console.log('PASS web: 8 buttons, hold/release, heartbeat, stale-command sequence, pointer cancel, blur/hidden/offline, assembly lock, fetch failure, SSID escaping, keyboard');
})().catch(e=>{console.error(e);process.exit(1);});
