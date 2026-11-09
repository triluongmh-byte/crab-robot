#pragma once
#include <pgmspace.h>
static const char WEB_UI[] PROGMEM=R"CRABHTML(<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Cua Robot</title>
<style>body{font:18px system-ui,sans-serif;max-width:520px;margin:auto;padding:16px;background:#f3f8fc;color:#172333}h1{font-size:26px}button,input,select{font:inherit;min-height:48px;border-radius:10px;padding:10px;border:1px solid #8094a6}button{background:#fff;cursor:pointer}button:active{background:#b4deff}button:disabled{opacity:.5}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.grid button{touch-action:none;user-select:none;-webkit-user-select:none}.wide{width:100%;margin:6px 0}label{display:block;margin:12px 0}input,select{box-sizing:border-box;width:100%}section{padding:12px 0}.hidden{display:none}#status{background:#dfeffc;padding:12px;white-space:pre-line}a{color:#124c92}small{display:block}#trims>div{display:flex;align-items:center;justify-content:space-between;margin:8px 0;gap:4px}#trims span{font-size:15px;flex:1}#trims button{min-width:48px}</style>
<h1>🦀 Cua Robot</h1><div id="status" role="status">Đang kết nối...</div>
<nav><button id="showControl">Lái cua</button> <button id="showSetup">Wi-Fi</button> <button id="showAssembly">Ráp</button></nav>
<section id="setup" class="hidden"><h2>Cài Wi-Fi</h2><button id="scan" class="wide">Tìm Wi-Fi quanh đây</button><label>Chọn mạng<select id="networks"><option value="">Nhấn Tìm Wi-Fi</option></select></label><label>Tên Wi-Fi (có thể nhập tay)<input id="ssid" maxlength="32" autocomplete="off"></label><label>Mật khẩu<input id="password" type="password" maxlength="63" autocomplete="new-password"></label><button id="connect" class="wide">Kết nối</button><p>Nếu điện thoại hỏi, chọn giữ kết nối với Wi-Fi không có internet. Nếu trang không tự mở, vào http://192.168.4.1/.</p></section>
<section id="control"><p>Giữ nút để đi, thả để dừng. Hãy kê thân để chân không chạm bàn ở lần thử đầu.</p><div class="grid"><button data-dir="5">↖ Tới trái</button><button data-dir="1">↑ Tới</button><button data-dir="6">↗ Tới phải</button><button data-dir="3">← Trái</button><button id="stop">DỪNG</button><button data-dir="4">Phải →</button><button data-dir="7">↙ Lui trái</button><button data-dir="2">↓ Lui</button><button data-dir="8">↘ Lui phải</button></div><label>Tốc độ<select id="speed"><option value="0.4">Chậm</option><option value="0.65" selected>Vừa</option><option value="1">Nhanh</option></select></label><button id="light" class="wide">Bật / tắt đèn</button><small>Đèn bị giới hạn độ sáng để giảm dòng.</small></section>
<section id="assembly" class="hidden"><h2>Ráp horn và chỉnh tâm</h2><p>Kê thân chắc chắn, chân để tự do. Mở trang này sẽ khóa đi bộ cho đến khi bấm Xong ráp. Không chỉnh tâm để che chân in sai hình.</p><button id="centre" class="wide">Giữa thô 1500 µs — gắn horn</button><button id="stand" class="wide">Tư thế đứng — xem tâm đã chỉnh</button><div id="trims"></div><button id="save" class="wide">Lưu tâm</button><button id="done" class="wide">Xong ráp — trở lại lái</button></section>
<script>
'use strict';
let token='',seq=0,held=0,busy=false,page='control',requestEpoch=0,freshPress=false;
const $=id=>document.getElementById(id);
async function api(path,data={}){const r=await fetch('/api/'+path,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(data),cache:'no-store'});if(!r.ok)throw Error('Lệnh chưa được nhận. Hãy thả nút rồi thử lại.');return r.json();}
function setStatus(t){$('status').textContent=t;}
async function getSession(){const d=await api('session');token=d.token;seq=0;}
function stop(){held=0;requestEpoch++;if(!token)return;const data=new URLSearchParams({token,seq:String(++seq),dir:'0',fresh:'0'});navigator.sendBeacon('/api/move',data);}
async function sendMove(){if(!held||busy||page!=='control')return;const epoch=requestEpoch;busy=true;try{await api('move',{token,seq:++seq,dir:held,fresh:freshPress?'1':'0'});}catch(e){if(epoch===requestEpoch){stop();setStatus(e.message);}}finally{if(epoch===requestEpoch)freshPress=false;busy=false;}}
function press(e){if(held||page!=='control')return;e.preventDefault();held=Number(e.currentTarget.dataset.dir);e.currentTarget.setPointerCapture(e.pointerId);requestEpoch++;freshPress=true;sendMove();}
for(const b of document.querySelectorAll('[data-dir]')){b.addEventListener('pointerdown',press);for(const event of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(event,stop);}
for(const event of ['pagehide','blur'])window.addEventListener(event,stop);
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
$('stop').onclick=stop;
async function show(p){stop();if(page==='assembly'&&p!=='assembly'){setStatus('Bấm Xong ráp để mở lại đi bộ.');return;}if(p==='assembly'){await api('assembly',{token,active:1});}page=p;for(const s of ['setup','control','assembly'])$(s).classList.toggle('hidden',s!==p);}
$('showControl').onclick=()=>show('control').catch(fail);$('showSetup').onclick=()=>show('setup').catch(fail);$('showAssembly').onclick=()=>show('assembly').catch(fail);
function fail(e){stop();setStatus(e.message);}
$('scan').onclick=async()=>{try{$('scan').disabled=true;let d;for(let i=0;i<30;i++){d=await api('scan');if(!d.busy)break;setStatus('Đang tìm mạng...');await new Promise(r=>setTimeout(r,500));}if(d.busy)throw Error('Chưa tìm được mạng. Hãy thử lại.');$('networks').replaceChildren();for(const n of d.networks){const o=document.createElement('option');o.value=n;o.textContent=n;$('networks').appendChild(o);}setStatus('Chọn Wi-Fi nhà rồi nhập mật khẩu.');}catch(e){fail(e);}finally{$('scan').disabled=false;}};
$('networks').onchange=()=>$('ssid').value=$('networks').value;
$('connect').onclick=async()=>{try{stop();const password=$('password').value;$('password').value='';await api('wifi',{ssid:$('ssid').value,password});setStatus('Đang vào Wi-Fi... Chờ QR mới trên màn hình.');}catch(e){fail(e);}};
$('light').onclick=()=>api('light',{token}).catch(fail);$('speed').onchange=()=>api('speed',{token,value:$('speed').value}).catch(fail);
$('centre').onclick=()=>api('centre',{token}).catch(fail);$('stand').onclick=()=>api('stand',{token}).catch(fail);
$('save').onclick=()=>api('save',{token}).then(()=>setStatus('Đã lưu tâm.')).catch(fail);
$('done').onclick=async()=>{try{await api('assembly',{token,active:0});page='control';show('control');}catch(e){fail(e);}};
const names=['Hông trước trái','Gối trước trái','Hông trước phải','Gối trước phải','Hông sau trái','Gối sau trái','Hông sau phải','Gối sau phải'];
names.forEach((name,ch)=>{const row=document.createElement('div');const label=document.createElement('span');label.textContent=name;row.appendChild(label);for(const delta of [-1,1]){const b=document.createElement('button');b.textContent=delta===1?'+':'−';b.onclick=()=>api('trim',{token,ch,delta}).then(d=>label.textContent=name+' ('+d.offset+'°)').catch(fail);row.appendChild(b);}$('trims').appendChild(row);});
async function status(){try{const r=await fetch('/api/status',{cache:'no-store'});const d=await r.json();setStatus(d.message+'\n'+(d.url||'http://192.168.4.1/')+(d.driver?'':'\nKiểm tra dây PCA9685')+(d.assembly?'\nChế độ ráp: đi bộ đang khóa.':''));if(!d.online&&page==='control')await show('setup');}catch(e){stop();setStatus('Mất kết nối. Cua tự dừng. Mở lại địa chỉ trên màn hình.');}}
getSession().then(()=>{status();setInterval(status,2000);setInterval(sendMove,150);}).catch(fail);
</script></html>
)CRABHTML";
