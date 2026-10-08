// Optional UI verification. Requires Playwright, not the ordinary live press.
const {chromium}=require(process.env.CARBON_PLAYWRIGHT || 'playwright');
const fs=require('fs'),path=require('path'),os=require('os'),crypto=require('crypto');
const {spawn}=require('child_process');
const assert=require('assert/strict');
const root=__dirname;
const hash=text=>crypto.createHash('sha256').update(text,'ascii').digest('hex');
const launch={headless:true,args:['--no-sandbox']};
if(process.env.CARBON_CHROMIUM)launch.executablePath=process.env.CARBON_CHROMIUM;
(async()=>{
 const html=process.argv[2];
 if(!html)throw Error('Usage: node test_browser.cjs /absolute/path/afterimage.html');
 const temporary=fs.mkdtempSync(path.join(os.tmpdir(),'carbon-browser-'));
 const port=21977;
 let browser,server;
 const evidence={timestamp:new Date().toISOString(),replays:[],live:{},page_errors:[]};
 try{
  browser=await chromium.launch(launch);
  const page=await browser.newPage({viewport:{width:1280,height:1130},deviceScaleFactor:1});
  page.on('pageerror',e=>evidence.page_errors.push(String(e)));
  await page.goto('file://'+path.resolve(html));
  await page.waitForFunction(()=>window.afterimage);
  for(let i=0;i<3;i++){
   await page.locator('#specimens button').nth(i).click();
   const r=await page.evaluate(()=>{const a=window.afterimage;let s=a.inspect();a.seek(s.world.trace.length);s=a.inspect();const ins=s.world.instructions;
    const cells=s.states.map((c,i)=>ins.colors[c].padEnd(32)+c+' '.repeat(7)+s.links.slice(i*4,i*4+4).map(v=>String(v).padStart(8)).join('')+String(s.imprints[i]).padStart(8)).join('');
    const heads=s.heads.map(h=>String(h.pos).padStart(8)+ins.headings[h.heading].padEnd(32)+`(T${String(1+h.genome*1152).padStart(4,'0')}:A1152)`.padEnd(32)+String(h.home).padStart(8)).join('');
    return {title:s.world.spec.title,position:s.position,errors:s.errors,cells,heads,expected:s.world.final_sha256};});
   const hashes={'world.spool':hash(r.cells),'heads.spool':hash(r.heads)};
   assert.deepEqual(hashes,r.expected,'Viewer reconstruction vs native spools');assert.deepEqual(r.errors,[]);
   evidence.replays.push({title:r.title,events:r.position,hashes,passed:true});
   await page.locator('#timeline').fill('13');await page.locator('#timeline').dispatchEvent('input');
   await page.locator('#step').click();assert.equal(await page.evaluate(()=>window.afterimage.inspect().position),14);
  }
  await page.locator('#specimens button').nth(0).click();await page.locator('#fracture').click();
  await page.locator('#edges').click();await page.locator('#edges').click();await page.locator('#follow').click();
  await page.locator('#play').click();await page.waitForTimeout(150);await page.locator('#play').click();
  await page.setViewportSize({width:390,height:900});await page.waitForTimeout(50);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth),false);
  evidence.mobile={width:390,horizontal_overflow:false};evidence.replay_controls=true;

  server=spawn(process.env.CARBON_PYTHON||'python3',[path.join(root,'afterimage.py'),'--serve','--port',String(port),'--world',path.join(temporary,'world')],{env:{...process.env,PYTHONUNBUFFERED:'1'},stdio:['ignore','pipe','pipe']});
  await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('Live press startup timed out')),15000);let out='',err='';server.stdout.on('data',d=>{out+=d.toString();if(out.includes('Native FORMAT press active')){clearTimeout(timeout);resolve();}});server.stderr.on('data',d=>err+=d.toString());server.once('exit',code=>{clearTimeout(timeout);reject(Error('Live press exited '+code+' '+err));});});
  const url=`http://127.0.0.1:${port}`;
  await page.setViewportSize({width:1280,height:1130});await page.goto(url);await page.waitForFunction(()=>window.afterimage);
  await page.locator('#step').click();await page.waitForFunction(()=>window.afterimage.inspect().position===1);
  await page.locator('#play').click();await page.waitForTimeout(300);await page.locator('#play').click();
  assert.ok(await page.evaluate(()=>window.afterimage.inspect().position>1));
  async function clickRecord(record){const point=await page.evaluate(pos=>{const c=document.getElementById('field').getBoundingClientRect(),s=window.afterimage.inspect().world.spec,cell=Math.min((c.width-32)/s.width,(c.height-32)/s.height);return {x:c.left+(c.width-cell*s.width)/2+(((pos-1)%s.width)+.5)*cell,y:c.top+(c.height-cell*s.height)/2+(Math.floor((pos-1)/s.width)+.5)*cell};},record);await page.mouse.click(point.x,point.y);}
  await page.locator('[data-tool="paint"]').click();await page.locator('#brushes button').nth(3).click();await clickRecord(1);
  await page.waitForFunction(()=>window.afterimage.inspect().states[0]===3);
  await page.locator('[data-tool="fold"]').click();await clickRecord(1);await clickRecord(6912);
  await page.waitForFunction(()=>window.afterimage.inspect().links[1]===6912&&window.afterimage.inspect().links[(6912-1)*4+3]===1);
  await page.locator('#turns').fill('LLLL');await page.locator('#stamps').fill('....');await page.locator('#apply').click();
  await page.waitForFunction(()=>window.afterimage.inspect().world.spec.genomes[0].turns==='LLLL');
  await page.locator('#step').click();await page.waitForFunction(()=>window.afterimage.inspect().position===1);
  const checkpoint=await page.request.get(url+'/checkpoint');assert.equal(checkpoint.status(),200);assert.ok((await checkpoint.body()).length>100);
  const denied=await page.request.post(url+'/step',{data:{rounds:1},headers:{Origin:'https://outside.invalid'}});assert.equal(denied.status(),403);
  const invalid=await page.request.post(url+'/genome',{data:{index:0,turns:'XXXX',stamps:'....'}});assert.equal(invalid.status(),400);
  const snapshot=await (await page.request.get(url+'/state')).json();assert.equal(snapshot.spec.genomes[0].turns,'LLLL');
  await page.locator('#specimens button').nth(2).click();await page.waitForFunction(()=>window.afterimage.inspect().world.spec.preset==='highway');
  evidence.live={native_play_step:true,paint:true,splice:true,genome_edit:true,checkpoint_download:true,invalid_edit_rejected:true,origin_guard:true,reseed:true};
  assert.deepEqual(evidence.page_errors,[]);evidence.passed=true;
  fs.writeFileSync(path.join(root,'evidence','browser.json'),JSON.stringify(evidence,null,2)+'\n');
  console.log(JSON.stringify(evidence));
 }finally{if(server)server.kill('SIGTERM');if(browser)await browser.close();fs.rmSync(temporary,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exit(1);});
