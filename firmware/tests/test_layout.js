// Optional isolated Chromium layout regression. No robot/network access.
// PLAYWRIGHT_MODULE=/path/to/playwright node firmware/tests/test_layout.js OUTPUT_DIR
const fs=require('fs'),path=require('path'),assert=require('assert'),crypto=require('crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const html=fs.readFileSync('firmware/assets/ui.html','utf8');
const output=process.argv[2];assert(output,'Pass a private output directory');fs.mkdirSync(output,{recursive:true});
const sameBox=(a,b)=>{for(const key of ['x','y','width','height'])assert(Math.abs(a[key]-b[key])<.5,key+' moved');};
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CRAB_TEST_CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const record={htmlSha256:crypto.createHash('sha256').update(html).digest('hex'),passed:false,physicalPhoneTested:false,robotCommandsSent:false,checks:[]};
 try{
  for(const view of [{name:'desktop',width:1280,height:800},{name:'mobile',width:390,height:844},{name:'small-mobile',width:320,height:568},{name:'landscape',width:700,height:390}]){
   const mobile=view.width<=760,context=await browser.newContext({viewport:{width:view.width,height:view.height},isMobile:mobile,hasTouch:mobile,deviceScaleFactor:1});
   const page=await context.newPage();let message='Đã vào Wi-Fi',telemetry=0;const commands=[],errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.route('http://crab.test/**',async route=>{
    const url=new URL(route.request().url());let data={};
    if(url.pathname==='/')return route.fulfill({contentType:'text/html',body:html});
    if(url.pathname==='/api/session')data={token:'42'};
    if(url.pathname==='/api/status')data={message,url:'http://192.168.4.1/',driver:true,positional:true,enabled:8,assembly:false,speed:.65,gait:'trot',offsets:Array(8).fill(0)};
    if(url.pathname==='/api/servos'){telemetry++;data={kind:'commanded',feedback:false,sampledAtMs:12345,servos:Array.from({length:8},(_,ch)=>({ch,known:true,active:true,angleDeg:90+ch,pulseUs:1500+ch*6,counts:307+ch}))};}
    if(url.pathname==='/api/move')commands.push(Object.fromEntries(new URLSearchParams(route.request().postData())));
    await route.fulfill({contentType:'application/json',body:JSON.stringify(data)});
   });
   await page.goto('http://crab.test/');await page.locator('#joy:not(.off)').waitFor();
   const button=page.locator('#joy'),box=await button.boundingBox();
   assert(box.y>=64&&box.y+box.height<=view.height,'joystick off screen');assert(Math.abs(box.width-box.height)<1,'joystick not round');
   for(const id of ['#stop','#power','#light','#lightColor']){const b=await page.locator(id).boundingBox();assert(b&&b.y>=64&&b.y+b.height<=view.height&&b.x>=0&&b.x+b.width<=view.width,id+' off screen');}
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'horizontal scroll');
   assert((await page.locator('#tools').isVisible())===!mobile);
   const center={x:box.x+box.width/2,y:box.y+box.height/2},up={x:center.x,y:box.y+box.height*0.08};let cdp;
   if(mobile){cdp=await context.newCDPSession(page);await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{...center,id:1}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{...up,id:1}]});}
   else{await page.mouse.move(center.x,center.y);await page.mouse.down();await page.mouse.move(up.x,up.y,{steps:4});}
   await page.waitForFunction(()=>held===1);
   message='Trạng thái dài thử bố cục\nDòng thứ hai\nDòng thứ ba\nDòng thứ tư\nDòng thứ năm';
   await page.waitForFunction(()=>document.getElementById('status').textContent.includes('Dòng thứ năm'));
   sameBox(box,await button.boundingBox());assert(await page.evaluate(()=>held)===1);
   if(mobile){
    await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:box.x+box.width*0.92,y:center.y,id:1}]});await page.waitForFunction(()=>held===4);for(let i=0;i<40&&!commands.some(x=>x.dir==='4');i++)await page.waitForTimeout(50);
    assert(await page.evaluate(()=>scrollY)===0);sameBox(box,await button.boundingBox());
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
   }else await page.mouse.up();
   await page.waitForFunction(()=>held===0);assert(commands.some(x=>x.dir==='1'&&x.fresh==='1'));assert(commands.some(x=>x.dir==='1'&&x.fresh==='0'));if(mobile)assert(commands.some(x=>x.dir==='4'));
   assert(errors.length===0,errors.join('\n'));
   await page.screenshot({path:path.join(output,view.name+'.png')});
   message='Đã vào Wi-Fi';await page.waitForFunction(()=>!document.getElementById('status').textContent.includes('Dòng thứ năm'));
   await page.screenshot({path:path.join(output,view.name+'-clean.png')});
   if(mobile){
    const before=telemetry;await page.locator('#menuButton').click();await page.locator('#tools').waitFor({state:'visible'});
    await page.waitForFunction(()=>document.getElementById('angle0').textContent==='90.0°');assert(telemetry>before);
    sameBox(box,await button.boundingBox());await page.screenshot({path:path.join(output,view.name+'-menu.png')});
    await page.locator('#servoRows').scrollIntoViewIfNeeded();sameBox(box,await button.boundingBox());await page.screenshot({path:path.join(output,view.name+'-telemetry.png')});
    await page.locator('#menuButton').click();assert(!(await page.locator('#tools').isVisible()));sameBox(box,await button.boundingBox());
   }else{
    const right=await page.locator('#tools').boundingBox();assert(right.x>box.x+box.width);
    await page.locator('#tools').evaluate(el=>el.scrollTop=el.scrollHeight);sameBox(box,await button.boundingBox());
   }
   record.checks.push({view:view.name,heldThroughStatusChange:true,fixedDriveBounds:true,actualTouch:mobile,drawer:mobile?'hidden/open/close/scroll checked':'sidebar independent scroll',telemetryRequests:telemetry});
   await context.close();
  }
  record.passed=true;
 }finally{await browser.close();fs.writeFileSync(path.join(output,'RESULT.json'),JSON.stringify(record,null,2)+'\n');}
 console.log(JSON.stringify(record,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
