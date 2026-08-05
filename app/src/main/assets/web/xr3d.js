/* TRJS AeroXR 3D renderer — procedural WebGL, no external runtime dependencies. */
(() => {
  'use strict';
  const DEG = Math.PI / 180;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const M4 = {
    identity(){return new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1])},
    multiply(a,b){const o=new Float32Array(16);for(let c=0;c<4;c++)for(let r=0;r<4;r++)o[c*4+r]=a[r]*b[c*4]+a[4+r]*b[c*4+1]+a[8+r]*b[c*4+2]+a[12+r]*b[c*4+3];return o},
    perspective(fov,aspect,near,far){const f=1/Math.tan(fov/2),nf=1/(near-far);return new Float32Array([f/aspect,0,0,0,0,f,0,0,0,0,(far+near)*nf,-1,0,0,2*far*near*nf,0])},
    translate(x,y,z){const m=this.identity();m[12]=x;m[13]=y;m[14]=z;return m},
    scale(x,y,z){const m=this.identity();m[0]=x;m[5]=y;m[10]=z;return m},
    rotX(a){const c=Math.cos(a),s=Math.sin(a);return new Float32Array([1,0,0,0,0,c,s,0,0,-s,c,0,0,0,0,1])},
    rotY(a){const c=Math.cos(a),s=Math.sin(a);return new Float32Array([c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1])},
    rotZ(a){const c=Math.cos(a),s=Math.sin(a);return new Float32Array([c,s,0,0,-s,c,0,0,0,0,1,0,0,0,0,1])},
    transform(m,v){const x=v[0],y=v[1],z=v[2],w=v[3]??1;return [m[0]*x+m[4]*y+m[8]*z+m[12]*w,m[1]*x+m[5]*y+m[9]*z+m[13]*w,m[2]*x+m[6]*y+m[10]*z+m[14]*w,m[3]*x+m[7]*y+m[11]*z+m[15]*w]}
  };
  function compose(...mats){return mats.reduce((a,b)=>M4.multiply(a,b),M4.identity())}
  function normalize(v){const l=Math.hypot(...v)||1;return v.map(x=>x/l)}
  function color(hex,a=1){hex=hex.replace('#','');if(hex.length===3)hex=hex.split('').map(x=>x+x).join('');return [parseInt(hex.slice(0,2),16)/255,parseInt(hex.slice(2,4),16)/255,parseInt(hex.slice(4,6),16)/255,a]}

  function makeMesh(pos,norm,idx){return {pos:new Float32Array(pos),norm:new Float32Array(norm),idx:new Uint16Array(idx)}}
  function cube(){
    const p=[],n=[],i=[];const faces=[[[1,0,0],[[1,-1,-1],[1,1,-1],[1,1,1],[1,-1,1]]],[[-1,0,0],[[-1,-1,1],[-1,1,1],[-1,1,-1],[-1,-1,-1]]],[[0,1,0],[[-1,1,-1],[-1,1,1],[1,1,1],[1,1,-1]]],[[0,-1,0],[[-1,-1,1],[-1,-1,-1],[1,-1,-1],[1,-1,1]]],[[0,0,1],[[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]]],[[0,0,-1],[[1,-1,-1],[-1,-1,-1],[-1,1,-1],[1,1,-1]]]];
    faces.forEach((f,fi)=>{const b=p.length/3;f[1].forEach(v=>{p.push(...v);n.push(...f[0])});i.push(b,b+1,b+2,b,b+2,b+3)});return makeMesh(p,n,i)
  }
  function cylinder(seg=28){const p=[],n=[],i=[];for(let y of [-1,1])for(let s=0;s<=seg;s++){const a=s/seg*Math.PI*2,x=Math.cos(a),z=Math.sin(a);p.push(x,y,z);n.push(x,0,z)}for(let s=0;s<seg;s++){const a=s,b=s+1,c=(seg+1)+s,d=c+1;i.push(a,c,b,b,c,d)}for(let cap=0;cap<2;cap++){const y=cap?1:-1,base=p.length/3;p.push(0,y,0);n.push(0,cap?1:-1,0);for(let s=0;s<=seg;s++){const a=(cap?1:-1)*s/seg*Math.PI*2;p.push(Math.cos(a),y,Math.sin(a));n.push(0,cap?1:-1,0)}for(let s=0;s<seg;s++)cap?i.push(base,base+1+s,base+2+s):i.push(base,base+2+s,base+1+s)}return makeMesh(p,n,i)}
  function torus(majorSeg=32,minorSeg=12,minor=.28){const p=[],n=[],i=[];for(let a=0;a<=majorSeg;a++){const u=a/majorSeg*Math.PI*2,cu=Math.cos(u),su=Math.sin(u);for(let b=0;b<=minorSeg;b++){const v=b/minorSeg*Math.PI*2,cv=Math.cos(v),sv=Math.sin(v);p.push((1+minor*cv)*cu,minor*sv,(1+minor*cv)*su);n.push(cv*cu,sv,cv*su)}}const row=minorSeg+1;for(let a=0;a<majorSeg;a++)for(let b=0;b<minorSeg;b++){const x=a*row+b;i.push(x,x+row,x+1,x+1,x+row,x+row+1)}return makeMesh(p,n,i)}
  function blade(){const p=[-.12,-1,0,.12,-1,0,.30,.85,0,.05,1.1,0,-.18,.82,0];const n=[];for(let k=0;k<5;k++)n.push(0,0,1);return makeMesh(p,n,[0,1,2,0,2,4,4,2,3])}
  const meshes={cube:cube(),cyl:cylinder(),torus:torus(),blade:blade()};

  class Renderer{
    constructor(canvas,hotspotLayer){this.canvas=canvas;this.layer=hotspotLayer;this.gl=null;this.program=null;this.buffers=new Map();this.scene='landing';this.screenHotspots=[];this.lastState=null;this.sensor={alpha:0,beta:0,gamma:0,enabled:false};this.quality='high';this.init()}
    init(){const gl=this.canvas.getContext('webgl2',{alpha:true,antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'})||this.canvas.getContext('webgl',{alpha:true,antialias:true,preserveDrawingBuffer:true});if(!gl)throw new Error('WebGL is not available');this.gl=gl;const vs=`attribute vec3 aPos;attribute vec3 aNormal;uniform mat4 uMVP;uniform mat4 uModel;varying vec3 vN;void main(){gl_Position=uMVP*vec4(aPos,1.0);vN=mat3(uModel)*aNormal;}`;const fs=`precision mediump float;uniform vec4 uColor;uniform float uGlow;varying vec3 vN;void main(){vec3 n=normalize(vN);float l=.28+.72*max(dot(n,normalize(vec3(.35,.75,.55))),0.0);vec3 c=uColor.rgb*l+uGlow*uColor.rgb*.35;gl_FragColor=vec4(c,uColor.a);}`;this.program=this.link(vs,fs);gl.enable(gl.DEPTH_TEST);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);Object.entries(meshes).forEach(([k,m])=>this.buffers.set(k,this.upload(m)));}
    shader(type,src){const s=this.gl.createShader(type);this.gl.shaderSource(s,src);this.gl.compileShader(s);if(!this.gl.getShaderParameter(s,this.gl.COMPILE_STATUS))throw new Error(this.gl.getShaderInfoLog(s));return s}
    link(vs,fs){const p=this.gl.createProgram();this.gl.attachShader(p,this.shader(this.gl.VERTEX_SHADER,vs));this.gl.attachShader(p,this.shader(this.gl.FRAGMENT_SHADER,fs));this.gl.linkProgram(p);if(!this.gl.getProgramParameter(p,this.gl.LINK_STATUS))throw new Error(this.gl.getProgramInfoLog(p));return p}
    upload(m){const gl=this.gl,b={count:m.idx.length};b.p=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b.p);gl.bufferData(gl.ARRAY_BUFFER,m.pos,gl.STATIC_DRAW);b.n=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b.n);gl.bufferData(gl.ARRAY_BUFFER,m.norm,gl.STATIC_DRAW);b.i=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,b.i);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,m.idx,gl.STATIC_DRAW);return b}
    resize(){const dpr=Math.min(this.quality==='high'?2:1.25,window.devicePixelRatio||1),w=Math.max(1,this.canvas.clientWidth),h=Math.max(1,this.canvas.clientHeight);const W=Math.round(w*dpr),H=Math.round(h*dpr);if(this.canvas.width!==W||this.canvas.height!==H){this.canvas.width=W;this.canvas.height=H}this.gl.viewport(0,0,W,H)}
    setScene(shape){this.scene=shape||'landing'}
    setSensor(s){this.sensor={...this.sensor,...s}}
    objects(shape){const blue=color('#159bdd',.72),cyan=color('#5ce1ff',.72),metal=color('#d9edf5',.82),dark=color('#193847',.86),rubber=color('#101820',.92),amber=color('#ffb12c',.82);const o=[];const add=(mesh,matrix,c,glow=0)=>o.push({mesh,matrix,c,glow});
      if(shape==='landing'){
        add('cyl',compose(M4.translate(0,.35,0),M4.scale(.18,1.18,.18)),metal);add('cyl',compose(M4.translate(0,-.45,0),M4.scale(.28,.45,.28)),blue);add('cube',compose(M4.translate(0,.95,0),M4.scale(.7,.12,.35)),cyan);for(const x of [-.58,.58]){add('torus',compose(M4.translate(x,-1.05,0),M4.rotZ(Math.PI/2),M4.scale(.48,.48,.48)),rubber);add('cyl',compose(M4.translate(x,-1.05,0),M4.rotZ(Math.PI/2),M4.scale(.22,.15,.22)),metal)}add('cyl',compose(M4.translate(-.32,-.35,.05),M4.rotZ(-.28),M4.scale(.08,.7,.08)),amber);add('cyl',compose(M4.translate(.32,-.35,.05),M4.rotZ(.28),M4.scale(.08,.7,.08)),amber)
      }else if(shape==='intake'){
        add('torus',compose(M4.rotX(Math.PI/2),M4.scale(1.2,1.2,1.2)),metal);add('cyl',compose(M4.rotX(Math.PI/2),M4.scale(1.08,.42,1.08)),dark);add('cyl',compose(M4.translate(0,0,.18),M4.rotX(Math.PI/2),M4.scale(.28,.15,.28)),metal);for(let i=0;i<18;i++)add('blade',compose(M4.translate(0,0,.24),M4.rotZ(i*Math.PI/9),M4.scale(.23,.72,.23)),blue,.25)
      }else if(shape==='propeller'){
        add('cyl',compose(M4.rotX(Math.PI/2),M4.scale(.36,.28,.36)),metal);for(let i=0;i<6;i++)add('blade',compose(M4.rotZ(i*Math.PI/3),M4.scale(.34,1.35,.34)),blue,.22);add('torus',compose(M4.rotX(Math.PI/2),M4.scale(.45,.45,.45)),cyan)
      }else if(shape==='wing'){
        add('cube',compose(M4.rotZ(-.08),M4.scale(1.75,.14,.58)),metal);add('cube',compose(M4.translate(.4,-.18,.08),M4.rotZ(-.08),M4.scale(1.1,.07,.48)),blue);add('cube',compose(M4.translate(-1.25,.08,0),M4.rotZ(-.08),M4.scale(.5,.08,.42)),cyan);for(let x=-1.1;x<=1.2;x+=.58)add('cyl',compose(M4.translate(x,.02,.48),M4.rotZ(Math.PI/2),M4.scale(.045,.18,.045)),amber)
      }else if(shape==='battery'){
        add('cube',compose(M4.scale(1.0,.62,.72)),dark);add('cube',compose(M4.translate(0,.72,0),M4.scale(.82,.12,.62)),metal);add('cyl',compose(M4.translate(-.55,.9,0),M4.scale(.12,.12,.12)),color('#e6435c'));add('cyl',compose(M4.translate(.55,.9,0),M4.scale(.12,.12,.12)),color('#202c34'));add('cube',compose(M4.translate(0,-.72,0),M4.scale(1.12,.08,.82)),blue);add('cube',compose(M4.translate(1.1,.05,0),M4.scale(.18,.24,.24)),amber);add('cube',compose(M4.translate(0,.05,.78),M4.scale(.72,.32,.05)),cyan,.2)
      }else{
        add('cube',compose(M4.rotX(-.35),M4.scale(1.1,.08,1.25)),metal);add('cube',compose(M4.translate(0,.45,-.3),M4.scale(1.18,.14,.12)),blue);for(const x of [-.75,0,.75])add('cyl',compose(M4.translate(x,-.08,.5),M4.rotZ(Math.PI/2),M4.scale(.06,.22,.06)),amber)
      }return o}
    hotspots(shape){const m={landing:[[-.55,-.95,.35],[.55,-.95,.35],[0,.62,.25],[.32,-.25,.35],[-.32,-.25,.35]],intake:[[0,1.12,.25],[0,.45,.6],[.75,.15,.35],[-.72,-.25,.3],[0,-.82,.35]],propeller:[[0,1.15,.2],[.95,.52,.15],[.55,-.8,.15],[-.78,-.62,.15],[-.98,.42,.15]],wing:[[-1.25,.12,.5],[-.55,.04,.55],[.15,-.04,.55],[.9,-.1,.52],[.45,-.3,.55]],battery:[[-.55,.9,.45],[0,.2,.78],[0,-.72,.45],[1.1,.05,.45],[0,.05,.84]],ramp:[[0,.9,.45],[-.75,.25,.55],[.75,.25,.55],[0,-.4,.55],[0,-.95,.45]]};return m[shape]||m.landing}
    frame(state,results,current){this.lastState=state;this.resize();const gl=this.gl,w=this.canvas.clientWidth,h=this.canvas.clientHeight;gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.useProgram(this.program);const aspect=w/h,proj=M4.perspective(42*DEG,aspect,.1,100),view=M4.translate(0,0,-6.2);const sensorYaw=state.sensorAssist?this.sensor.gamma*.12*DEG:0,sensorPitch=state.sensorAssist?this.sensor.beta*.06*DEG:0;const model=compose(M4.translate(state.x/(w*.36),-state.y/(h*.36),0),M4.rotZ((state.rz||0)*DEG),M4.rotY((state.ry||0)*DEG+sensorYaw),M4.rotX((state.rx||0)*DEG+sensorPitch),M4.scale(state.scale,state.scale,state.scale));const vp=M4.multiply(proj,view);this.objects(this.scene).forEach(o=>this.drawObject(o,M4.multiply(model,o.matrix),vp));const points=this.hotspots(this.scene);this.screenHotspots=points.map((p,i)=>this.projectPoint(p,model,vp,w,h,i,results?.[i]?.status,i===current));this.renderHotspotDOM(this.screenHotspots);}
    drawObject(o,model,vp){const gl=this.gl,p=this.program,b=this.buffers.get(o.mesh),mvp=M4.multiply(vp,model);const ap=gl.getAttribLocation(p,'aPos'),an=gl.getAttribLocation(p,'aNormal');gl.bindBuffer(gl.ARRAY_BUFFER,b.p);gl.enableVertexAttribArray(ap);gl.vertexAttribPointer(ap,3,gl.FLOAT,false,0,0);gl.bindBuffer(gl.ARRAY_BUFFER,b.n);gl.enableVertexAttribArray(an);gl.vertexAttribPointer(an,3,gl.FLOAT,false,0,0);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,b.i);gl.uniformMatrix4fv(gl.getUniformLocation(p,'uMVP'),false,mvp);gl.uniformMatrix4fv(gl.getUniformLocation(p,'uModel'),false,model);gl.uniform4fv(gl.getUniformLocation(p,'uColor'),o.c);gl.uniform1f(gl.getUniformLocation(p,'uGlow'),o.glow||0);gl.drawElements(gl.TRIANGLES,b.count,gl.UNSIGNED_SHORT,0)}
    projectPoint(p,model,vp,w,h,index,status,active){const clip=M4.transform(M4.multiply(vp,model),[...p,1]),inv=clip[3]?1/clip[3]:0,x=(clip[0]*inv*.5+.5)*w,y=(-clip[1]*inv*.5+.5)*h;return {x,y,z:clip[2]*inv,index,status,active,visible:clip[3]>0&&x>-30&&x<w+30&&y>-30&&y<h+30}}
    renderHotspotDOM(points){if(!this.layer)return;while(this.layer.children.length<points.length){const b=document.createElement('button');b.type='button';b.className='xr-3d-hotspot';b.addEventListener('click',()=>this.onHotspot?.(+b.dataset.index));this.layer.appendChild(b)}[...this.layer.children].forEach((b,i)=>{const p=points[i];b.dataset.index=i;b.textContent=i+1;b.className=`xr-3d-hotspot ${p.active?'active':''} ${p.status==='Pass'?'pass':p.status==='Fail'?'fail':p.status==='N/A'?'na':''}`;b.style.transform=`translate3d(${p.x}px,${p.y}px,0) translate(-50%,-50%)`;b.style.display=p.visible?'grid':'none'})}
    pick(x,y){let best=-1,d=1e9;this.screenHotspots.forEach(p=>{const q=Math.hypot(x-p.x,y-p.y);if(q<d){d=q;best=p.index}});return d<55?best:-1}
    capture(){try{return this.canvas.toDataURL('image/png')}catch{return ''}}
  }
  window.XR3D={create(canvas,layer){return new Renderer(canvas,layer)}};
})();
