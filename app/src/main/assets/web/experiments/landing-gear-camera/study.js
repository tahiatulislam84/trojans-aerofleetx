(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const points = [
    ['1 · Generic left wheel', 'Frame the complete landing gear assembly first. This marker is on the generic model left wheel; verify aircraft variant and approved inspection data before work.'],
    ['2 · Generic right wheel', 'This marker is on the generic model right wheel. The real wheel arrangement and access depend on the aircraft.'],
    ['3 · Identify the upper attachment', 'Use the generic upper model point for orientation; do not infer an attachment location or inspection criterion from this rendering.'],
    ['4 · Identify the lower structure', 'Compare the generic model against the physical assembly and consult the approved aircraft instructions.'],
    ['5 · Generic lower structure', 'Use this generic lower model point for orientation. Document observations under the applicable approved task; this prototype makes no maintenance decision.']
  ];
  let renderer, stream, current = 0, mode = 'move', held = false;
  let state = {x:0,y:0,scale:.82,rx:-8,ry:18,rz:0,sensorAssist:false};
  const pointers = new Map(); let previousDistance = 0, previousCenter = null;
  function status(message){$('status').textContent=message}
  function draw(){renderer.frame(state, [], current)}
  function select(index){current=Math.max(0,Math.min(points.length-1,index));$('point-title').textContent=points[current][0];$('point-detail').textContent=points[current][1];draw()}
  try {renderer=XR3D.create($('model'),$('hotspots'));renderer.setScene('landing');renderer.onHotspot=select;select(0)}
  catch(e){status('WebGL rendering is unavailable on this device: '+e.message);$('start').disabled=true;return}
  $('start').onclick=async()=>{
    if(stream)return;
    try{
      if(!navigator.mediaDevices?.getUserMedia)throw new Error('Use HTTPS or localhost and a browser with camera access.');
      stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:'environment'}},audio:false});
      $('video').srcObject=stream;await $('video').play();$('start').disabled=true;$('stop').disabled=false;
      status('Live camera ready. Position the generic model manually; alignment and inspection points are not verified.');draw();
    }catch(e){stream?.getTracks().forEach(t=>t.stop());stream=null;status('Camera unavailable: '+e.message)}
  };
  $('stop').onclick=()=>{stream?.getTracks().forEach(t=>t.stop());stream=null;$('video').srcObject=null;$('start').disabled=false;$('stop').disabled=true;status('Camera stopped.')};
  $('reset').onclick=()=>{state={x:0,y:0,scale:.82,rx:-8,ry:18,rz:0,sensorAssist:false};held=false;$('anchor').textContent='Hold overlay';draw()};
  $('anchor').onclick=()=>{held=!held;$('anchor').textContent=held?'Release overlay':'Hold overlay';status(held?'Overlay held in screen coordinates; moving the camera will not track the gear.':'Overlay can be moved again.')};
  $('move').onclick=()=>{mode='move';status('Drag to move; pinch to resize.')};
  $('rotate').onclick=()=>{mode='rotate';status('Drag to rotate; pinch to resize.')};
  $('previous').onclick=()=>select(current-1);$('next').onclick=()=>select(current+1);
  const canvas=$('model');
  canvas.addEventListener('pointerdown',e=>{if(held)return;canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});previousCenter=null;previousDistance=0});
  canvas.addEventListener('pointermove',e=>{
    if(held||!pointers.has(e.pointerId))return;
    const prior=pointers.get(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(pointers.size===2){const [a,b]=[...pointers.values()],distance=Math.hypot(a.x-b.x,a.y-b.y);if(previousDistance)state.scale=Math.max(.42,Math.min(2.25,state.scale*distance/previousDistance));previousDistance=distance;previousCenter={x:(a.x+b.x)/2,y:(a.y+b.y)/2}}
    else if(!previousCenter){if(mode==='rotate'){state.ry+=(e.clientX-prior.x)*.45;state.rx=Math.max(-80,Math.min(80,state.rx+(e.clientY-prior.y)*.35))}else{state.x+=e.clientX-prior.x;state.y+=e.clientY-prior.y}}
    draw();
  });
  for(const event of ['pointerup','pointercancel'])canvas.addEventListener(event,e=>{pointers.delete(e.pointerId);previousDistance=0;previousCenter=null});
  window.addEventListener('resize',draw);window.addEventListener('beforeunload',()=>stream?.getTracks().forEach(t=>t.stop()));
})();
