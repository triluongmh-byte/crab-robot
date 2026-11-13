#pragma once
#include <pgmspace.h>
static const char WEB_UI[] PROGMEM=R"CRABHTML(<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>Cua Robot · Điều khiển</title>
<style>
*{box-sizing:border-box}html,body{height:100%;margin:0;overflow:hidden;overscroll-behavior:none}body{font:17px/1.4 system-ui,sans-serif;background:#eff5fa;color:#172333;overflow-anchor:none}button,input,select{font:inherit;min-height:46px;border-radius:10px;padding:10px;border:1px solid #879bad}button{background:#fff;color:inherit;cursor:pointer;touch-action:manipulation;-webkit-touch-callout:none}button:disabled{opacity:.45;cursor:default}button:active,button.holding{background:#addaff;border-color:#2671ae}button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #4289bd;outline-offset:3px}h1,h2,h3,p{margin:0}h1{font-size:22px}h2{font-size:20px}h3{font-size:17px}a{color:#195f95}.dim,small{color:#526778}small{display:block}.hidden{display:none!important}
.topbar{height:64px;display:flex;align-items:center;justify-content:space-between;padding:8px 22px;border-bottom:1px solid #d1dee8;background:#fff;gap:10px}.top-actions{display:flex;align-items:center;gap:12px}#readiness{font-size:14px;display:inline-block;width:144px;text-align:right;white-space:nowrap}#menuButton{display:none}.workspace{display:grid;grid-template-columns:minmax(300px,1fr) minmax(340px,430px);height:calc(100% - 64px);max-width:1320px;margin:auto;min-height:0}
#control{min-width:0;min-height:0;display:flex;align-items:center;justify-content:center;padding:24px;overflow:hidden}.drive-deck{width:100%;max-width:490px;text-align:center;display:flex;flex-direction:column;gap:22px}.drive-heading p{font-size:15px;color:#526778;margin-top:6px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-template-rows:repeat(3,clamp(64px,12vh,100px));gap:12px;touch-action:none;user-select:none;-webkit-user-select:none;-webkit-touch-callout:none}.grid button{font-size:clamp(19px,2.5vw,25px);font-weight:650;touch-action:none;padding:8px}.forward{grid-area:1/2}.left{grid-area:2/1}#stop{grid-area:2/2;background:#ffeded;border-color:#d68e8e}.right{grid-area:2/3}.backward{grid-area:3/2}.drive-hint{font-size:14px;color:#526778}
#tools{min-height:0;min-width:0;overflow-y:auto;overscroll-behavior:contain;padding:20px;background:#fff;border-left:1px solid #d1dee8;scrollbar-gutter:stable}#status{background:#dfeffc;border:1px solid #c7dff1;border-radius:12px;padding:14px;white-space:pre-line;overflow-wrap:anywhere;min-height:98px;font-size:16px}#tools p{margin:8px 0}.wide{width:100%;margin:5px 0}#arm{margin-top:14px}#disarm{border-color:#d68e8e}nav{display:flex;gap:6px;margin:14px 0}nav button{flex:1;padding:8px;font-size:15px}label{display:block;margin:12px 0}input,select{width:100%;margin-top:5px}#controlTools,#setup,#assembly{padding-bottom:18px;border-bottom:1px solid #dbe5ed}#trims>div{display:flex;align-items:center;justify-content:space-between;gap:6px;margin:8px 0}#trims span{font-size:13px;flex:1}#trims button{min-width:44px;padding:6px}.servo-monitor{margin-top:18px}.servo-monitor p{font-size:13px;color:#526778}table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:12px;margin-top:10px}th{text-align:left;font-weight:600;border-bottom:1px solid #bccfdf;padding:8px 3px}td{padding:8px 3px;border-bottom:1px solid #e1eaf1;overflow-wrap:anywhere}th:first-child{width:43%}td:not(:first-child){font-variant-numeric:tabular-nums;font-family:ui-monospace,monospace;white-space:nowrap}td small{font-size:11px}#telemetryStamp{font-size:12px;min-height:18px}#eventLog{height:128px;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;background:#dfeffc;border-radius:10px;padding:12px;font:12px/1.5 ui-monospace,monospace;margin:8px 0 0}.event-heading{margin-top:18px}#backdrop{display:none}#statusDetail{display:grid;grid-template-columns:auto 1fr;gap:4px 12px;margin:10px 0 4px;font-size:15px}#statusDetail dt{color:#526778}#statusDetail dd{margin:0;font-weight:600;overflow-wrap:anywhere}.light-row{display:flex;gap:8px;margin:5px 0}.light-row button{flex:1}#lightColor{width:64px;flex:0 0 64px;margin:0;padding:4px}#speed,#flickHip,#balance,#knee{min-height:30px;padding:0}#speedValue,#flickHipValue,#balanceValue,#kneeValue{float:right;font-weight:650}
@media(max-width:760px){.topbar{padding:8px 12px}h1{font-size:19px}#readiness{width:108px;font-size:12px}.top-actions{gap:8px}#menuButton{display:block;min-width:46px;padding:8px}.workspace{grid-template-columns:minmax(0,1fr)}#control{padding:16px}.drive-deck{max-width:440px;gap:18px}.grid{gap:10px}#tools{position:fixed;z-index:30;top:64px;bottom:0;right:0;width:min(100%,430px);visibility:hidden;transform:translateX(105%);pointer-events:none;padding:16px 16px calc(16px + env(safe-area-inset-bottom,0px));box-shadow:-5px 0 25px #17233322}body[data-panel="open"] #tools{visibility:visible;transform:translateX(0);pointer-events:auto}body[data-panel="open"] #backdrop{display:block;position:fixed;z-index:20;inset:64px 0 0;border:0;border-radius:0;background:#17233366}#control{padding-bottom:max(16px,env(safe-area-inset-bottom,0px))}}
@media(max-height:480px){.drive-deck{gap:8px}.grid{grid-template-rows:repeat(3,56px);gap:8px}.drive-heading p{display:none}}
</style></head>
<body data-page="control" data-panel="closed">
<header class="topbar"><h1>🦀 Cua Robot</h1><div class="top-actions"><a href="/emo" style="color:#124c92;font-weight:600;text-decoration:none">🎭 Cảm xúc</a><span id="readiness">Đang kết nối…</span><button id="menuButton" aria-label="Mở trạng thái và cài đặt" aria-controls="tools" aria-expanded="false">☰</button></div></header>
<main class="workspace">
<section id="control" aria-label="Lái cua"><div id="driveDeck" class="drive-deck"><div class="drive-heading"><h2>Điều khiển</h2><p>Giữ nút để đi · Thả tay để dừng</p></div><div class="grid">
<button class="forward" disabled data-dir="1">↑ Tiến</button><button class="left" disabled data-dir="3">← Trái</button><button id="stop">DỪNG</button><button class="right" disabled data-dir="4">Phải →</button><button class="backward" disabled data-dir="2">↓ Lùi</button>
</div><p class="drive-hint" id="gaitHint">Hai cặp chân chéo thay phiên đẩy, có lúc cả bốn chân cùng chạm đất.</p></div></section>
<button id="backdrop" aria-label="Đóng menu" tabindex="-1"></button>
<aside id="tools" aria-label="Trạng thái, servo và cài đặt">
<div id="status" role="status">Đang kết nối...</div>
<button id="arm" class="wide">Bật servo 180°</button><button id="disarm" class="wide">Ngắt servo — tắt tất cả xung</button>
<nav aria-label="Cài đặt"><button id="showControl">Trạng thái</button><button id="showSetup">Wi-Fi</button><button id="showAssembly">Ráp</button></nav>
<section id="controlTools"><dl id="statusDetail" aria-label="Trạng thái chi tiết"></dl><label>Dáng đi<select id="gait"><option value="trot" selected>Chéo — vững, không tự xoay</option><option value="pairs">Cặp trước/sau</option><option value="flick">Búng gối — tới/lui (thử)</option></select></label><label id="flickHipBox" class="hidden">Góc hông búng <span id="flickHipValue">90°</span><input id="flickHip" type="range" min="30" max="90" step="5" value="90" aria-describedby="flickHipValue"><small>Kéo xuống nếu hai chân trước/sau đụng nhau.</small></label><label>Tốc độ <span id="speedValue">90%</span><input id="speed" type="range" min="20" max="100" step="5" value="90" aria-describedby="speedValue"></label><label>Độ nhấc gối <span id="kneeValue">45°</span><input id="knee" type="range" min="20" max="60" step="5" value="45" aria-describedby="kneeValue"><small>Chân quẹt bàn lúc hông hồi về → kéo lên. Lưu luôn trên cua.</small></label><label>Bù lệch trái ↔ phải <span id="balanceValue">0</span><input id="balance" type="range" min="-30" max="30" step="1" value="0" aria-describedby="balanceValue"><small>Đi tới bị lệch sang phải → kéo về phía + (chân bên phải đẩy mạnh hơn, bên trái nhẹ lại). Lệch trái → kéo về −. Lưu luôn trên cua.</small></label><div class="light-row"><button id="light">Bật / tắt đèn</button><input id="lightColor" type="color" value="#ffffff" aria-label="Màu đèn" title="Đổi màu đèn"></div><p class="dim">Bật máy là servo tự bật lần lượt 8 kênh trong khoảng 3 giây. Chỉ dùng servo định vị 180°.</p></section>
<section id="setup" class="hidden"><h2>Wi-Fi nhà (tùy chọn)</h2><p>Có thể lái ngay trên Wi-Fi của cua, không cần mạng nhà.</p><button id="scan" class="wide">Tìm Wi-Fi quanh đây</button><label>Chọn mạng<select id="networks"><option value="">Nhấn Tìm Wi-Fi</option></select></label><label>Tên Wi-Fi<input id="ssid" maxlength="32" autocomplete="off"></label><label>Mật khẩu<input id="password" type="password" maxlength="63" autocomplete="new-password"></label><button id="connect" class="wide">Kết nối</button><p>Nếu cần, giữ kết nối không có internet rồi mở http://192.168.4.1/.</p></section>
<section id="assembly" class="hidden"><h2>Ráp servo 180°</h2><p>Tháo horn/chân trước khi lấy tâm. Cấp nguồn, bấm Bật servo rồi Giữa thô. Chờ khoảng 3 giây. Tắt nguồn trước khi đổi giắc hoặc lắp horn.</p><p>Ráp khóa các nút lái. Không trộn servo360° cũ vào bộ mới.</p><button id="centre" class="wide">Giữa thô · 1500 µs</button><button id="stand" class="wide">Tư thế đứng</button><p class="dim">Mỗi nấc 1° rất nhỏ (gần vùng chết của SG90), servo có thể chưa nhúc nhích. Dùng ±3 để thấy rõ, ±1 để chỉnh tinh.</p><div id="trims"></div><button id="save" class="wide">Lưu tâm</button><button id="done" class="wide">Xong ráp — trở lại lái</button></section>
<section class="servo-monitor" aria-label="Góc lệnh servo"><h3>8 servo · góc lệnh</h3><p>Giá trị đã gửi tới PCA, gồm chỉnh tâm và giới hạn. Tâm danh định 90°. Đây không phải góc thực đo được; chưa có tọa độ XYZ.</p><table><thead><tr><th>Khớp</th><th>Góc</th><th>Xung µs</th><th>PWM</th></tr></thead><tbody id="servoRows"></tbody></table><p id="telemetryStamp">Chưa có bản ghi.</p></section>
<h3 class="event-heading">Nhật ký trạng thái</h3><pre id="eventLog" aria-live="off"></pre>
</aside></main>
<script>
'use strict';
const $=id=>document.getElementById(id);
let token='',seq=0,held=0,busy=false,page='control',requestEpoch=0,freshPress=false,ready=false,activePointer=null,activeButton=null,menuOpen=false,telemetryBusy=false;
const logLines=[];
// Physical positions: the owner found CH0 at the REAR RIGHT (firmware cfg::FRONT_IS_CH46).
// Calibration labels as the owner names the legs (CH6 = rear-right hip); the
// drive direction is set separately by firmware cfg::FRONT_IS_CH46.
const names=['Hông trước trái','Gối trước trái','Hông trước phải','Gối trước phải','Hông sau trái','Gối sau trái','Hông sau phải','Gối sau phải'];
const GAITS={trot:'Chéo',pairs:'Cặp trước/sau',flick:'Búng gối'};let speedDragging=false,hipDragging=false,balanceDragging=false,kneeDragging=false;
function balanceText(v){v=Number(v);return v===0?'0':(v>0?'+'+v+'% phải':v+'% (trái mạnh hơn)');}
function showSpeed(pct){$('speedValue').textContent=pct+'%';}
function renderDetail(d){const rows=[['Firmware',d.firmware||'—'],['PCA9685',d.driver?'OK':'Lỗi dây'],['Servo',d.positional?(d.enabled<8?'Đang bật '+d.enabled+'/8':'Bật đủ 8/8'):'Tắt xung'],['Chế độ',d.assembly?'Ráp (khóa lái)':'Lái'],['Dáng đi',(GAITS[d.gait]||d.gait||'—')+(d.gait==='flick'&&d.flickHip!==undefined?' · hông '+d.flickHip+'°':'')],['Tốc độ',d.speed!==undefined?Math.round(d.speed*100)+'%':'—'],['Nhấc gối',d.knee!==undefined?d.knee+'°':'—'],['Bù lệch',d.balance!==undefined?balanceText(d.balance):'—'],['Đèn',d.lightOn?'Bật'+(d.lightColor?' · '+d.lightColor:''):'Tắt'],['Wi-Fi',(d.online?'Wi-Fi nhà · ':'Wi-Fi của cua · ')+(d.url||'http://192.168.4.1/')]];const box=$('statusDetail');box.replaceChildren();for(const [k,v] of rows){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=k;dd.textContent=v;box.appendChild(dt);box.appendChild(dd);}}
async function api(path,data={}){const r=await fetch('/api/'+path,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(data),cache:'no-store',...(typeof AbortSignal!=='undefined'&&AbortSignal.timeout?{signal:AbortSignal.timeout(5000)}:{})});let d={};try{d=await r.json();}catch(e){}if(!r.ok)throw Error(d.error||'Lệnh chưa được nhận. Hãy thả nút rồi thử lại.');return d;}
function recordLog(s){logLines.push(new Date().toLocaleTimeString()+' · '+s);if(logLines.length>30)logLines.shift();$('eventLog').textContent=logLines.join('\n');}
function setStatus(s){if($('status').textContent!==s){$('status').textContent=s;recordLog(s);}}
function stop(){if(held)recordLog('Thả nút · dừng bước');held=0;freshPress=false;requestEpoch++;const b=activeButton,id=activePointer;activeButton=null;activePointer=null;if(b){b.classList.toggle('holding',false);if(b.hasPointerCapture(id))b.releasePointerCapture(id);}if(!token)return;navigator.sendBeacon('/api/move',new URLSearchParams({token,seq:String(++seq),dir:'0',fresh:'0'}));}
function fail(e){stop();setStatus(e.message);}
async function sendMove(){if(!held||page==='assembly'||busy||!ready)return;const epoch=requestEpoch;busy=true;try{await api('move',{token,seq:++seq,dir:held,fresh:freshPress?'1':'0'});}catch(e){if(epoch===requestEpoch)fail(e);}finally{if(epoch===requestEpoch)freshPress=false;busy=false;}}
function releasePointer(e){if(e.pointerId===activePointer){e.preventDefault();stop();}}
for(const b of document.querySelectorAll('[data-dir]')){
 b.addEventListener('pointerdown',e=>{e.preventDefault();if(held||page==='assembly'||!ready||b.disabled||(e.pointerType==='mouse'&&e.button!==0))return;activePointer=e.pointerId;activeButton=b;try{b.setPointerCapture(e.pointerId);}catch(e){}b.classList.toggle('holding',true);held=Number(b.dataset.dir);recordLog('Giữ nút '+b.textContent);requestEpoch++;freshPress=true;sendMove();});
 for(const event of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(event,releasePointer);
}
// Capture on the button plus window release keeps a hold while the finger drifts.
for(const event of ['pointerup','pointercancel'])window.addEventListener(event,releasePointer);
$('driveDeck').addEventListener('contextmenu',e=>e.preventDefault());
$('driveDeck').addEventListener('touchmove',e=>{if(held)e.preventDefault();},{passive:false});
for(const event of ['blur','pagehide'])window.addEventListener(event,stop);document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});$('stop').onclick=stop;
async function pollStatus(){try{const r=await fetch('/api/status',{cache:'no-store'});if(!r.ok)throw Error('status');const d=await r.json();ready=!!d.driver&&!!d.positional&&d.enabled===8&&!d.assembly;if(!ready&&held)stop();for(const b of document.querySelectorAll('[data-dir]'))if(b.disabled===ready)b.disabled=!ready;$('arm').disabled=!!d.positional||!d.driver;$('arm').textContent=d.positional?(d.enabled<8?'Đang bật servo… '+d.enabled+'/8':'✅ Servo đang bật — bấm Ngắt để tắt'):'Bật servo 180°';renderDetail(d);$('readiness').textContent=d.assembly?'Đang Ráp':!d.driver?'Lỗi PCA9685':ready?'Sẵn sàng':d.positional?'Đang bật servo':'Servo tắt';if(d.speed!==undefined&&!speedDragging){const pct=Math.round(d.speed*100);$('speed').value=String(pct);showSpeed(pct);}if(d.lightColor&&!colorPicking)$('lightColor').value=d.lightColor;if(d.knee!==undefined&&!kneeDragging){$('knee').value=String(d.knee);$('kneeValue').textContent=d.knee+'°';}if(d.balance!==undefined&&!balanceDragging){$('balance').value=String(d.balance);$('balanceValue').textContent=balanceText(d.balance);}if(d.flickHip!==undefined&&!hipDragging){$('flickHip').value=String(d.flickHip);$('flickHipValue').textContent=d.flickHip+'°';}if(d.gait){$('gait').value=d.gait;$('flickHipBox').classList.toggle('hidden',d.gait!=='flick');$('gaitHint').textContent=d.gait==='pairs'?'Cặp chân trước và sau thay phiên đẩy.':d.gait==='flick'?'Tới/lui: hông xoay 90° (trước ra trước, sau ra sau) rồi bốn gối búng — chân sau đạp, chân trước rút. Trái/phải vẫn đi chéo.':'Hai cặp chân chéo thay phiên đẩy, có lúc cả bốn chân cùng chạm đất.';}let servo=d.positional?(d.enabled<8?'Đang bật servo lần lượt: '+d.enabled+'/8.':'Servo 180° sẵn sàng.'):'Servo 180° đang tắt xung — bấm Bật servo hoặc mở Ráp.';setStatus(d.message+'\n'+(d.url||'http://192.168.4.1/')+'\n'+servo+(d.driver?'':'\nKiểm tra dây PCA9685')+(d.assembly?'\nĐang Ráp: nút lái bị khóa.':''));if(d.offsets)names.forEach((n,ch)=>$('trim'+ch).textContent='CH'+ch+' · '+n+' ('+d.offsets[ch]+'°)');}catch(e){ready=false;$('readiness').textContent='Mất kết nối';for(const b of document.querySelectorAll('[data-dir]'))b.disabled=true;stop();setStatus('Mất kết nối. Cua tự dừng bước. Mở lại địa chỉ trên màn hình.');}}
async function arm(){stop();await api('actuator',{token,seq:++seq,value:'positional',confirm:'1'});await pollStatus();}
$('arm').onclick=()=>arm().catch(fail);$('disarm').onclick=async()=>{try{stop();ready=false;await api('actuator',{token,seq:++seq,value:'unknown',confirm:'0'});await pollStatus();}catch(e){fail(e);}};
async function show(p){stop();if(page==='assembly'&&p!=='assembly'){setStatus('Bấm Xong ráp trước khi rời trang Ráp.');return;}if(p==='assembly')await api('assembly',{token,active:1});page=p;document.body.dataset.page=p;for(const s of ['control','setup','assembly'])$(s==='control'?'controlTools':s).classList.toggle('hidden',s!==p);await pollStatus();}
$('showControl').onclick=()=>show('control').catch(fail);$('showSetup').onclick=()=>show('setup').catch(fail);$('showAssembly').onclick=()=>show('assembly').catch(fail);
$('centre').onclick=()=>api('centre',{token}).then(pollStatus).catch(fail);$('stand').onclick=()=>api('stand',{token}).then(pollStatus).catch(fail);$('save').onclick=()=>api('save',{token}).then(()=>setStatus('Đã lưu tâm cho bộ180°.')).catch(fail);$('done').onclick=async()=>{try{stop();await api('assembly',{token,active:0});page='control';await show('control');}catch(e){fail(e);}};
names.forEach((n,ch)=>{const row=document.createElement('div'),label=document.createElement('span');label.id='trim'+ch;label.textContent='CH'+ch+' · '+n+' (0°)';row.appendChild(label);for(const delta of [-3,-1,1,3]){const b=document.createElement('button');b.textContent=(delta>0?'+':'−')+Math.abs(delta);b.title=Math.abs(delta)===3?'Bước lớn 3°':'Bước nhỏ 1°';b.onclick=()=>api('trim',{token,ch,delta}).then(pollStatus).catch(fail);row.appendChild(b);}$('trims').appendChild(row);});
$('light').onclick=()=>api('light',{token}).catch(fail);let colorPicking=false;$('lightColor').oninput=()=>{colorPicking=true;};$('lightColor').onchange=()=>{colorPicking=false;api('lightcolor',{token,value:$('lightColor').value.slice(1)}).catch(fail);};$('knee').oninput=()=>{kneeDragging=true;$('kneeValue').textContent=$('knee').value+'°';};$('knee').onchange=()=>{kneeDragging=false;stop();api('knee',{token,value:$('knee').value}).catch(fail);};$('balance').oninput=()=>{balanceDragging=true;$('balanceValue').textContent=balanceText($('balance').value);};$('balance').onchange=()=>{balanceDragging=false;stop();api('balance',{token,value:$('balance').value}).catch(fail);};$('flickHip').oninput=()=>{hipDragging=true;$('flickHipValue').textContent=$('flickHip').value+'°';};$('flickHip').onchange=()=>{hipDragging=false;stop();api('flickhip',{token,value:$('flickHip').value}).catch(fail);};$('speed').oninput=()=>{speedDragging=true;showSpeed($('speed').value);};$('speed').onchange=()=>{speedDragging=false;stop();showSpeed($('speed').value);api('speed',{token,value:(Number($('speed').value)/100).toFixed(2)}).catch(fail);};$('gait').onchange=()=>{stop();api('gait',{token,value:$('gait').value}).catch(fail);};
$('networks').onchange=()=>$('ssid').value=$('networks').value;
$('scan').onclick=async()=>{try{$('scan').disabled=true;let d;for(let i=0;i<30;i++){d=await api('scan');if(!d.busy)break;setStatus('Đang tìm Wi-Fi...');await new Promise(r=>setTimeout(r,500));}if(d.busy)throw Error('Chưa tìm được mạng. Thử lại sau.');$('networks').replaceChildren();for(const n of d.networks){const o=document.createElement('option');o.value=n;o.textContent=n;$('networks').appendChild(o);}}catch(e){fail(e);}finally{$('scan').disabled=false;}};
$('connect').onclick=async()=>{try{stop();const password=$('password').value;$('password').value='';await api('wifi',{ssid:$('ssid').value,password});setStatus('Đang vào Wi-Fi... Chờ QR mới trên màn hình.');}catch(e){fail(e);}};
function setMenu(open){const wasOpen=menuOpen;stop();menuOpen=open;document.body.dataset.panel=open?'open':'closed';$('menuButton').setAttribute('aria-expanded',String(open));if(open)pollServos();else if(wasOpen)$('menuButton').focus({preventScroll:true});}
$('menuButton').onclick=()=>setMenu(!menuOpen);$('backdrop').onclick=()=>setMenu(false);window.addEventListener('keydown',e=>{if(e.key==='Escape')setMenu(false);});
names.forEach((name,ch)=>{const row=document.createElement('tr'),label=document.createElement('td');label.textContent='CH'+ch+' · '+name;const state=document.createElement('small');state.id='servoState'+ch;state.textContent='Chưa xác nhận';label.appendChild(state);row.appendChild(label);for(const field of ['angle','pulse','counts']){const cell=document.createElement('td');cell.id=field+ch;cell.textContent='—';row.appendChild(cell);}$('servoRows').appendChild(row);});
function clearTelemetry(message){for(let ch=0;ch<8;ch++){for(const field of ['angle','pulse','counts'])$(field+ch).textContent='—';$('servoState'+ch).textContent='Chưa xác nhận';}$('telemetryStamp').textContent=message;}
async function pollServos(){
 if(telemetryBusy||(window.matchMedia('(max-width:760px)').matches&&!menuOpen))return;
 telemetryBusy=true;
 try{
  const response=await fetch('/api/servos',{cache:'no-store',...(typeof AbortSignal!=='undefined'&&AbortSignal.timeout?{signal:AbortSignal.timeout(1500)}:{})});if(!response.ok)throw Error('telemetry');
  const d=await response.json();if(d.kind!=='commanded'||d.feedback!==false||!Array.isArray(d.servos)||d.servos.length!==8)throw Error('telemetry');
  for(let ch=0;ch<8;ch++){const x=d.servos[ch];if(x.ch!==ch)throw Error('telemetry');const on=x.known&&x.active;for(const [field,value] of [['angle',on&&Number.isFinite(x.angleDeg)?x.angleDeg.toFixed(1)+'°':'—'],['pulse',on&&Number.isFinite(x.pulseUs)?String(x.pulseUs):'—'],['counts',on&&Number.isFinite(x.counts)?String(x.counts):'—']])$(field+ch).textContent=value;$('servoState'+ch).textContent=!x.known?'Chưa xác nhận':x.active?'Có xung':'Tắt xung';}
  $('telemetryStamp').textContent='Mẫu '+d.sampledAtMs+'ms · góc lệnh, không phải đo thực.';
 }catch(e){clearTelemetry('Chưa đọc được bản ghi servo.');}finally{telemetryBusy=false;}
}
api('session').then(d=>{token=d.token;seq=0;pollStatus();setInterval(pollStatus,1000);setInterval(sendMove,150);pollServos();setInterval(pollServos,500);}).catch(fail);
</script></body></html>
)CRABHTML";
static const char EMOTE_UI[] PROGMEM=R"CRABHTML(<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>Cua Robot · Cảm xúc</title>
<style>
*{box-sizing:border-box}body{margin:0;font:16px/1.4 system-ui,sans-serif;background:#eff5fa;color:#172333}
button,input,select{font:inherit;min-height:44px;border-radius:10px;padding:8px 10px;border:1px solid #879bad;background:#fff;color:inherit}
button{cursor:pointer;touch-action:manipulation}button:disabled{opacity:.45;cursor:default}button:active{background:#addaff}
.topbar{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 16px;background:#fff;border-bottom:1px solid #d1dee8;position:sticky;top:0;z-index:5}
.topbar h1{font-size:20px;margin:0}.topbar a{color:#124c92;text-decoration:none;font-weight:600}
main{max-width:1100px;margin:auto;padding:14px;display:grid;gap:14px;grid-template-columns:minmax(0,1fr) minmax(0,1fr)}
.card{background:#fff;border:1px solid #d1dee8;border-radius:14px;padding:14px}.card h2{font-size:18px;margin:0 0 10px}
#status{background:#dfeffc;border:1px solid #c7dff1;border-radius:10px;padding:10px;white-space:pre-line;min-height:48px}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:8px 0}.row>*{flex:1 1 auto}
#stopAll{background:#ffe1e1;border-color:#d68e8e;font-weight:700}
.presets{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px}.presets button{font-size:17px;min-height:56px}
.legs{display:grid;grid-template-columns:1fr 1fr;gap:10px}.leg{border:1px solid #d1dee8;border-radius:10px;padding:8px}.leg h3{font-size:15px;margin:0 0 4px}
.leg label{display:block;font-size:14px;margin:6px 0 0}.leg input[type=range]{width:100%;min-height:32px;padding:0;border:0}
.val{float:right;font-variant-numeric:tabular-nums;color:#38536a}
#frames{list-style:none;margin:8px 0;padding:0;display:flex;flex-wrap:wrap;gap:6px}#frames li button{min-width:52px}#frames li button.sel{background:#addaff;border-color:#2671ae}
#saved{list-style:none;margin:8px 0;padding:0}#saved li{display:flex;gap:6px;align-items:center;margin:6px 0}#saved li span{flex:1;overflow-wrap:anywhere}
.dim{color:#526778;font-size:14px}.span2{grid-column:1/-1}
@media(max-width:760px){main{grid-template-columns:minmax(0,1fr);padding:10px}.legs{grid-template-columns:1fr}}
</style></head>
<body>
<header class="topbar"><h1>🎭 Cảm xúc của cua</h1><a href="/">← Lái cua</a></header>
<main>
<section class="card"><h2>Trạng thái</h2><div id="status" role="status">Đang kết nối…</div>
<div class="row"><button id="arm">Bật servo 180°</button><button id="stopAll">DỪNG</button></div>
<p class="dim">Mở trang này sẽ nhận quyền điều khiển (trang lái sẽ phải mở lại). Thả trang, đổi tab hoặc mất kết nối thì cua tự về đứng.</p></section>
<section class="card"><h2>Cảm xúc có sẵn</h2><div class="presets" id="presets"></div>
<div class="row"><label style="flex:0 0 auto"><input type="checkbox" id="loopPreset" style="width:auto;min-height:0"> Lặp lại</label></div></section>
<section class="card span2"><h2>Tạo cảm xúc</h2>
<p class="dim">Hông: + là đưa bàn chân ra trước. Gối: + là nhấc chân lên, − là đạp xuống (thân cao lên). Mỗi khung có thời gian chuyển và thời gian giữ. Kéo thanh là cua cử động theo ngay.</p>
<div class="legs" id="legs"></div>
<div class="row"><label>Màu đèn <input type="color" id="color" value="#ffc400"></label><label>Chuyển (ms) <input type="number" id="ms" min="0" max="3000" step="10" value="300"></label><label>Giữ (ms) <input type="number" id="hold" min="0" max="5000" step="10" value="0"></label></div>
<div class="row"><label style="flex:0 0 auto"><input type="checkbox" id="mirror" style="width:auto;min-height:0" checked> Đối xứng trái/phải</label><button id="live">Xem trực tiếp: tắt</button><button id="zero">Về đứng</button></div>
<div class="row"><button id="addFrame">+ Thêm khung</button><button id="updateFrame">Cập nhật khung</button><button id="deleteFrame">Xóa khung</button></div>
<ul id="frames"></ul>
<div class="row"><button id="playOnce">▶ Chạy</button><button id="playLoop">🔁 Lặp</button></div>
<div class="row"><input id="name" maxlength="24" placeholder="Tên cảm xúc"><button id="save">💾 Lưu vào cua</button></div>
<p class="dim" id="capacity"></p><ul id="saved"></ul></section>
</main>
<script>
'use strict';
const $=id=>document.getElementById(id);
// Leg order FL, FR, RL, RR. Page units: hip + = foot forwards, knee + = lift.
// Firmware command frame: knee negative lifts; left hips move forwards when negative.
const LEGS=['Trước trái','Trước phải','Sau trái','Sau phải'],HIP_FORWARD=[-1,1,-1,1],LIMIT=30,TICK=150,MAX_LIST=3800;
const clampDeg=v=>Math.max(-LIMIT,Math.min(LIMIT,Math.round(Number(v)||0)));
// Sliders/presets are in physical leg order. The owner found CH0 at the rear right
// (firmware cfg::FRONT_IS_CH46), so physical leg L drives channels of CAD leg 3-L.
const CAD_LEG=[3,2,1,0];
function toCommand(p){const a=Array(8).fill(0);for(let leg=0;leg<4;leg++){const c=CAD_LEG[leg];a[2*c]=clampDeg(p[2*leg])*HIP_FORWARD[leg];a[2*c+1]=-clampDeg(p[2*leg+1]);}return a.map(v=>v===0?0:v).join(',');}
function hexRgb(c){const m=/^#([0-9a-f]{6})$/i.exec(c||'');const n=m?parseInt(m[1],16):0;return {r:n>>16&255,g:n>>8&255,b:n&255};}
// Frame: [h0,k0,h1,k1,h2,k2,h3,k3,'#rrggbb',moveMs,holdMs]
const F=(p,c,ms,hold=0)=>[...p,c,ms,hold];
const P=(h,k)=>[h[0],k[0],h[1],k[1],h[2],k[2],h[3],k[3]];
const STAND=P([0,0,0,0],[0,0,0,0]);
const PRESETS=[
 {n:'😄 Vui',f:[F(P([10,10,-10,-10],[-20,-20,-20,-20]),'#ffc400',150),F(P([-10,-10,10,10],[10,10,10,10]),'#ffe066',150),F(P([10,10,-10,-10],[-20,-20,-20,-20]),'#ffc400',150),F(P([-10,-10,10,10],[10,10,10,10]),'#ffe066',150),F(STAND,'#ffc400',200)]},
 {n:'😢 Buồn',f:[F(P([-10,-10,0,0],[28,28,15,15]),'#2050ff',1200,1500),F(P([-10,-10,0,0],[22,22,12,12]),'#102890',900,600),F(STAND,'#2050ff',900)]},
 {n:'😡 Giận',f:[F(P([15,15,0,0],[30,0,0,0]),'#ff0000',120),F(P([15,15,0,0],[-25,0,0,0]),'#600000',100),F(P([15,15,0,0],[0,30,0,0]),'#ff0000',120),F(P([15,15,0,0],[0,-25,0,0]),'#600000',100),F(P([15,15,0,0],[30,0,0,0]),'#ff0000',120),F(P([15,15,0,0],[-25,0,0,0]),'#600000',100),F(STAND,'#ff0000',250)]},
 {n:'👋 Chào',f:[F(P([0,25,0,0],[-10,30,-10,-10]),'#00d0ff',300),F(P([0,5,0,0],[-10,30,-10,-10]),'#00d0ff',200),F(P([0,25,0,0],[-10,30,-10,-10]),'#80f0ff',200),F(P([0,5,0,0],[-10,30,-10,-10]),'#00d0ff',200),F(P([0,25,0,0],[-10,30,-10,-10]),'#80f0ff',200),F(STAND,'#00d0ff',300)]},
 {n:'💃 Nhảy',f:[F(P([15,-15,15,-15],[-20,15,-20,15]),'#c040ff',250),F(P([-15,15,-15,15],[15,-20,15,-20]),'#ff40c0',250),F(P([15,-15,15,-15],[-20,15,-20,15]),'#c040ff',250),F(P([-15,15,-15,15],[15,-20,15,-20]),'#ff40c0',250),F(STAND,'#c040ff',250)]},
 {n:'😴 Ngủ',f:[F(P([0,0,0,0],[30,30,30,30]),'#301060',2000,2500),F(STAND,'#301060',1500)]},
 {n:'😲 Ngạc nhiên',f:[F(P([0,0,0,0],[-30,-30,-30,-30]),'#ffffff',100,700),F(STAND,'#ffffff',400)]}
];
let token='',seq=0,ready=false,run=0,frames=[],selected=-1,saved=[],liveOn=false,liveBusy=false,lastColor='';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function api(path,data={}){const r=await fetch('/api/'+path,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(data),cache:'no-store'});let d={};try{d=await r.json();}catch(e){}if(!r.ok)throw Error(d.error||'Lệnh chưa được nhận.');return d;}
function setStatus(s){$('status').textContent=s;}
async function led(c){if(c===lastColor)return;lastColor=c;const {r,g,b}=hexRgb(c);await api('led',{token,r,g,b});}
async function pose(p,ms,fresh){await api('pose',{token,seq:++seq,fresh:fresh?'1':'0',ms:String(Math.max(0,Math.min(5000,Math.round(ms)))),a:toCommand(p)});}
// The page drives the timeline: each frame is re-sent every TICK ms with the
// remaining transition time, which also renews the firmware's 500 ms lease.
async function playFrames(list,loop){
 const id=++run;liveOff();let fresh=true;
 try{
  do{for(const f of list){
   if(id!==run)return;const p=f.slice(0,8),move=Number(f[9])||0,hold=Number(f[10])||0;
   await led(f[8]);const start=Date.now();
   for(;;){if(id!==run)return;const left=start+move-Date.now();await pose(p,Math.max(0,left),fresh);fresh=false;if(Date.now()-start>=move+hold)break;await sleep(TICK);}
  }}while(loop&&id===run);
 }catch(e){setStatus(e.message);}
 if(id===run)halt();
}
function halt(){run++;liveOff();if(token&&navigator.sendBeacon)navigator.sendBeacon('/api/move',new URLSearchParams({token,seq:String(++seq),dir:'0',fresh:'0'}));}
function readEditor(){const p=[];for(let i=0;i<8;i++)p.push(clampDeg($('j'+i).value));return F(p,$('color').value,Math.max(0,Math.min(3000,Number($('ms').value)||0)),Math.max(0,Math.min(5000,Number($('hold').value)||0)));}
function writeEditor(f){for(let i=0;i<8;i++){$('j'+i).value=f[i];$('v'+i).textContent=f[i]+'°';}$('color').value=f[8];$('ms').value=f[9];$('hold').value=f[10];}
function mirrorFrom(i){if(!$('mirror').checked)return;const leg=i>>1,joint=i&1,other=leg^1,j=2*other+joint;$('j'+j).value=$('j'+i).value;$('v'+j).textContent=$('j'+j).value+'°';}
function renderFrames(){const ul=$('frames');ul.replaceChildren();frames.forEach((f,i)=>{const li=document.createElement('li'),b=document.createElement('button');b.textContent=String(i+1);b.style.borderBottom='6px solid '+f[8];if(i===selected)b.className='sel';b.onclick=()=>{selected=i;writeEditor(f);renderFrames();};li.appendChild(b);ul.appendChild(li);});}
function listJson(list){return JSON.stringify(list);}
function renderSaved(){const ul=$('saved');ul.replaceChildren();saved.forEach((e,i)=>{const li=document.createElement('li'),name=document.createElement('span'),play=document.createElement('button'),edit=document.createElement('button'),del=document.createElement('button');name.textContent=e.n;play.textContent='▶';edit.textContent='Sửa';del.textContent='Xóa';play.onclick=()=>ready&&playFrames(e.f,$('loopPreset').checked);edit.onclick=()=>{frames=e.f.map(f=>f.slice());selected=0;$('name').value=e.n;if(frames[0])writeEditor(frames[0]);renderFrames();};del.onclick=()=>store(saved.filter((_,k)=>k!==i));li.append(name,play,edit,del);ul.appendChild(li);});$('capacity').textContent='Bộ nhớ cua: '+listJson(saved).length+'/'+MAX_LIST+' ký tự.';}
async function store(list){const data=listJson(list);if(data.length>MAX_LIST){setStatus('Hết chỗ lưu trên cua. Xóa bớt cảm xúc cũ.');return false;}try{await api('emotions/save',{token,data});saved=list;renderSaved();return true;}catch(e){setStatus(e.message);return false;}}
async function loadSaved(){try{const r=await fetch('/api/emotions',{cache:'no-store'});const d=await r.json();saved=Array.isArray(d)?d.filter(e=>e&&typeof e.n==='string'&&Array.isArray(e.f)):[];}catch(e){saved=[];}renderSaved();}
async function liveLoop(){if(liveBusy)return;liveBusy=true;let fresh=true;try{while(liveOn&&ready){const f=readEditor();await led(f[8]);await pose(f.slice(0,8),200,fresh);fresh=false;await sleep(TICK);}}catch(e){setStatus(e.message);liveOff();}liveBusy=false;}
function liveOff(){if(!liveOn)return;liveOn=false;$('live').textContent='Xem trực tiếp: tắt';}
async function poll(){try{const r=await fetch('/api/status',{cache:'no-store'});const d=await r.json();ready=!!d.driver&&!!d.positional&&d.enabled===8&&!d.assembly;$('arm').disabled=!!d.positional||!d.driver;setStatus((ready?'Sẵn sàng diễn cảm xúc.':!d.driver?'Kiểm tra dây PCA9685.':d.assembly?'Đang ở trang Ráp: thoát Ráp trước.':d.positional?'Đang bật servo '+d.enabled+'/8…':'Servo đang tắt — bấm Bật servo.')+(run?'':''));}catch(e){ready=false;setStatus('Mất kết nối. Cua tự về đứng.');}}
function build(){
 const legs=$('legs');LEGS.forEach((n,leg)=>{const box=document.createElement('div');box.className='leg';const h=document.createElement('h3');h.textContent=n;box.appendChild(h);
  ['Hông','Gối'].forEach((jn,joint)=>{const i=2*leg+joint,l=document.createElement('label'),v=document.createElement('span'),r=document.createElement('input');v.className='val';v.id='v'+i;v.textContent='0°';r.type='range';r.min=-LIMIT;r.max=LIMIT;r.step=1;r.value=0;r.id='j'+i;r.oninput=()=>{v.textContent=r.value+'°';mirrorFrom(i);autoLive();};l.append(jn,v,r);box.appendChild(l);});legs.appendChild(box);});
 PRESETS.forEach(e=>{const b=document.createElement('button');b.textContent=e.n;b.onclick=()=>{if(!ready){setStatus('Bật servo trước đã.');return;}playFrames(e.f,$('loopPreset').checked);};$('presets').appendChild(b);});
}
build();
$('arm').onclick=async()=>{try{halt();await api('actuator',{token,seq:++seq,value:'positional',confirm:'1'});await poll();}catch(e){setStatus(e.message);}};
$('stopAll').onclick=halt;
$('zero').onclick=()=>writeEditor(F(STAND,$('color').value,Number($('ms').value)||0,Number($('hold').value)||0));
function startLive(){if(!ready){setStatus('Servo chưa sẵn sàng — bấm Bật servo rồi chờ 3 giây.');return false;}run++;liveOn=true;$('live').textContent='Xem trực tiếp: bật';liveLoop();return true;}
// Owner: sliders looked dead because preview was opt-in. Touching one now drives the crab.
function autoLive(){if(!liveOn)startLive();}
$('live').onclick=()=>{if(liveOn){liveOff();halt();return;}startLive();};
$('addFrame').onclick=()=>{if(frames.length>=40)return;frames.splice(selected+1,0,readEditor());selected++;renderFrames();};
$('updateFrame').onclick=()=>{if(selected<0)return;frames[selected]=readEditor();renderFrames();};
$('deleteFrame').onclick=()=>{if(selected<0)return;frames.splice(selected,1);selected=Math.min(selected,frames.length-1);if(selected>=0)writeEditor(frames[selected]);renderFrames();};
$('playOnce').onclick=()=>{if(ready&&frames.length)playFrames(frames,false);};
$('playLoop').onclick=()=>{if(ready&&frames.length)playFrames(frames,true);};
$('save').onclick=async()=>{const n=$('name').value.trim().slice(0,24);if(!n||!frames.length){setStatus('Đặt tên và thêm ít nhất một khung.');return;}const list=saved.filter(e=>e.n!==n).concat([{n,f:frames.map(f=>f.slice())}]);if(await store(list))setStatus('Đã lưu “'+n+'” vào cua.');};
for(const ev of ['blur','pagehide'])window.addEventListener(ev,halt);document.addEventListener('visibilitychange',()=>{if(document.hidden)halt();});
window.CuaEmote={toCommand,hexRgb,PRESETS,playFrames,halt,autoLive,state:()=>({run,seq,ready,liveOn,frames,saved}),setReady:v=>{ready=v;}};
api('session').then(d=>{token=d.token;seq=0;poll();loadSaved();setInterval(poll,1000);}).catch(e=>setStatus(e.message));
</script></body></html>
)CRABHTML";
