const STORE='lumen.cinematic01.voir.v1';
const QA=new URLSearchParams(location.search).get('qa');
const reduceMotion=matchMedia('(prefers-reduced-motion: reduce)').matches;
const mobile=matchMedia('(max-width:600px)').matches;

const $=s=>document.querySelector(s);
const html=document.documentElement;
const entryScene=$('#entryScene');
const voirScene=$('#voirScene');
const thresholdSurface=$('#thresholdSurface');
const codexSurface=$('#codexSurface');
const reflectionSurface=$('#reflectionSurface');
const completeSurface=$('#completeSurface');

const defaults={
  stage:'entry',
  page:0,
  situation:'',
  reflection:'',
  completed:false
};

let state=load();
let lesson=null;
let sources=null;
let pointer={x:0,y:0,tx:0,ty:0};
let sound=null;
let atmosphereInfo={mode:'initializing',tier:mobile?'mobile':'high',avgFrameMs:null};

function load(){
  try{return Object.assign({},defaults,JSON.parse(localStorage.getItem(STORE)||'{}'))}
  catch{return {...defaults}}
}
function save(){localStorage.setItem(STORE,JSON.stringify(state))}
function status(msg){
  const el=$('#sceneStatus');
  el.textContent=msg;
  el.classList.add('on');
  clearTimeout(status.t);
  status.t=setTimeout(()=>el.classList.remove('on'),1900);
}

async function loadContent(){
  const [l,s]=await Promise.all([
    fetch('/api/real/lesson/choisir-sa-prise').then(r=>r.json()),
    fetch('/api/real/sources').then(r=>r.json())
  ]);
  lesson=l;sources=s;
}

function hideAllSurfaces(){
  thresholdSurface.hidden=true;
  codexSurface.hidden=true;
  reflectionSurface.hidden=true;
  completeSurface.hidden=true;
}

function setStage(stage,{persist=true,announce=true}={}){
  state.stage=stage;
  if(persist)save();

  document.body.classList.remove('stage-threshold','stage-reading','stage-reflection','stage-complete');
  hideAllSurfaces();

  if(stage==='entry'){
    entryScene.hidden=false;
    voirScene.hidden=true;
    voirScene.classList.remove('active');
    html.dataset.scene='entry';
    if(announce)status('Sanctuaire');
    return;
  }

  entryScene.hidden=true;
  voirScene.hidden=false;
  requestAnimationFrame(()=>voirScene.classList.add('active'));
  html.dataset.scene=stage;
  document.body.classList.add('stage-'+stage);

  if(stage==='threshold'){
    thresholdSurface.hidden=false;
    $('#situation').value=state.situation||'';
  }else if(stage==='reading'){
    codexSurface.hidden=false;
    renderPage();
  }else if(stage==='reflection'){
    reflectionSurface.hidden=false;
    $('#reflectionPrompt').textContent=lesson?.reflection_prompt||'Reformulez l’idée avec vos propres mots.';
    $('#reflection').value=state.reflection||'';
  }else if(stage==='complete'){
    completeSurface.hidden=false;
  }
  markQAReady();
}

function crossIntoVoir(){
  if(reduceMotion){
    setStage('threshold');
    return;
  }
  document.body.classList.add('crossing');
  setTimeout(()=>{
    setStage('threshold');
    document.body.classList.remove('crossing');
  },780);
}

function roman(n){return ['I','II','III','IV','V','VI'][n]||String(n+1)}

function renderPage(){
  if(!lesson)return;
  const page=Math.max(0,Math.min(lesson.sections.length-1,state.page||0));
  state.page=page;
  const section=lesson.sections[page];

  $('#pageRoman').textContent=roman(page);
  $('#sectionKicker').textContent=section.kicker||`LECTURE ${page+1}`;
  $('#sectionTitle').textContent=section.title||'';
  const body=$('#sectionBody');
  body.innerHTML='';
  for(const paragraph of (section.body||[])){
    const p=document.createElement('p');
    p.textContent=paragraph;
    body.appendChild(p);
  }
  $('#pageCount').textContent=`${page+1} / ${lesson.sections.length}`;
  $('#progressFill').style.width=`${((page+1)/lesson.sections.length)*100}%`;
  $('#previousPage').style.visibility=page===0?'hidden':'visible';
  $('#nextPage').querySelector('span').textContent=page===lesson.sections.length-1?'Reformuler':'Continuer';

  const sourceId=(lesson.sources||[])[0];
  const src=sources?.sources?.find(x=>x.id===sourceId);
  $('#sourceWhisper').textContent=src
    ? `${src.author} · ${src.title}. Limite : ${src.limits}`
    : 'Source et limite conservées dans le contenu LUMEN.';
}

function nextPage(){
  if(!lesson)return;
  if(state.page<lesson.sections.length-1){
    state.page+=1;save();renderPage();
    codexSurface.animate(
      [{opacity:.35,transform:'translate(-50%,-45%) scale(.995)'},{opacity:1,transform:'translate(-50%,-46%) scale(1)'}],
      {duration:420,easing:'cubic-bezier(.2,.7,.2,1)'}
    );
  }else{
    setStage('reflection');
  }
}
function previousPage(){
  if(state.page>0){state.page-=1;save();renderPage()}
}

function wire(){
  $('#enterVoir').addEventListener('click',crossIntoVoir);
  $('#backSanctuary').addEventListener('click',()=>setStage('entry'));

  $('#engraveSituation').addEventListener('click',()=>{
    const value=$('#situation').value.trim();
    if(value.length<8){status('Écrivez une situation réelle en quelques mots.');return}
    state.situation=value;
    state.page=0;
    save();
    setStage('reading');
  });

  $('#nextPage').addEventListener('click',nextPage);
  $('#previousPage').addEventListener('click',previousPage);

  $('#sealReflection').addEventListener('click',()=>{
    const value=$('#reflection').value.trim();
    if(value.length<18){status('Reformulez avec un peu plus de précision.');return}
    state.reflection=value;
    state.completed=true;
    save();
    setStage('complete');
  });

  $('#returnThreshold').addEventListener('click',()=>{
    state.page=0;
    save();
    setStage('threshold');
  });

  $('#soundToggle').addEventListener('click',toggleSound);

  window.addEventListener('pointermove',e=>{
    if(reduceMotion)return;
    pointer.tx=((e.clientX/window.innerWidth)-.5)*2;
    pointer.ty=((e.clientY/window.innerHeight)-.5)*2;
    if(sound?.pan)sound.pan.pan.setTargetAtTime(pointer.tx*.35,sound.ctx.currentTime,.08);
  },{passive:true});

  window.addEventListener('keydown',e=>{
    if(e.key==='Escape'&&state.stage!=='entry')setStage('entry');
    if(e.key==='Enter'&&state.stage==='entry'&&document.activeElement===document.body)crossIntoVoir();
  });
}

function animateCamera(){
  if(reduceMotion)return;
  pointer.x+=(pointer.tx-pointer.x)*.055;
  pointer.y+=(pointer.ty-pointer.y)*.055;
  html.style.setProperty('--px',pointer.x.toFixed(4));
  html.style.setProperty('--py',pointer.y.toFixed(4));
  html.style.setProperty('--breath',((Math.sin(performance.now()/1700)+1)/2).toFixed(4));
  requestAnimationFrame(animateCamera);
}

function setupSound(){
  if(sound)return sound;
  const AC=window.AudioContext||window.webkitAudioContext;
  if(!AC)return null;
  const ctx=new AC();
  const master=ctx.createGain(); master.gain.value=.0001;
  const pan=ctx.createStereoPanner?ctx.createStereoPanner():null;
  const filter=ctx.createBiquadFilter();filter.type='lowpass';filter.frequency.value=420;filter.Q.value=.45;

  const oscA=ctx.createOscillator();oscA.type='sine';oscA.frequency.value=55;
  const oscB=ctx.createOscillator();oscB.type='sine';oscB.frequency.value=82.5;
  const gainA=ctx.createGain();gainA.gain.value=.022;
  const gainB=ctx.createGain();gainB.gain.value=.009;

  oscA.connect(gainA);oscB.connect(gainB);
  gainA.connect(filter);gainB.connect(filter);
  if(pan){filter.connect(pan);pan.connect(master)}else{filter.connect(master)}
  master.connect(ctx.destination);
  oscA.start();oscB.start();

  sound={ctx,master,pan,on:false};
  return sound;
}

async function toggleSound(){
  const s=setupSound();
  if(!s){status('Audio non disponible.');return}
  await s.ctx.resume();
  s.on=!s.on;
  const now=s.ctx.currentTime;
  s.master.gain.cancelScheduledValues(now);
  s.master.gain.setTargetAtTime(s.on?.035:.0001,now,.16);
  $('#soundToggle').setAttribute('aria-pressed',String(s.on));
  status(s.on?'Ambiance activée':'Ambiance coupée');
}

function initAtmosphere(){
  const canvas=$('#atmosphere');
  const gl=canvas.getContext('webgl',{alpha:true,antialias:false,premultipliedAlpha:true})
    ||canvas.getContext('experimental-webgl',{alpha:true,antialias:false});
  if(!gl){
    atmosphereInfo.mode='css-fallback';
    html.dataset.atmosphere='fallback';
    return;
  }

  const vert=`
    attribute vec2 p;
    void main(){gl_Position=vec4(p,0.0,1.0);}
  `;
  const frag=`
    precision mediump float;
    uniform vec2 r;
    uniform float t;
    uniform vec2 m;

    float hash(vec2 p){
      return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453123);
    }
    float noise(vec2 p){
      vec2 i=floor(p),f=fract(p);
      f=f*f*(3.0-2.0*f);
      return mix(mix(hash(i),hash(i+vec2(1.,0.)),f.x),
                 mix(hash(i+vec2(0.,1.)),hash(i+vec2(1.,1.)),f.x),f.y);
    }
    float fbm(vec2 p){
      float v=0.0;
      v+=noise(p)*.55;
      p=p*2.03+17.1;
      v+=noise(p)*.28;
      p=p*2.01+9.7;
      v+=noise(p)*.17;
      return v;
    }
    void main(){
      vec2 uv=gl_FragCoord.xy/r.xy;
      vec2 q=uv-.5;
      q.x*=r.x/r.y;

      float tt=t*.035;
      float fog=fbm(vec2(q.x*1.65+tt,q.y*2.1-tt*.42)+m*.12);
      fog=smoothstep(.47,.86,fog)*(1.0-smoothstep(.68,1.0,length(q)));

      vec2 cell=floor((uv+vec2(tt*.08,-tt*.02))*vec2(86.0,52.0));
      float dust=step(.985,hash(cell));
      float twinkle=.45+.55*sin(t*1.7+hash(cell)*20.0);
      dust*=twinkle*(1.0-smoothstep(.1,.9,abs(q.y)));

      float ray=max(0.0,1.0-abs(q.x*.9+q.y*.20-m.x*.05)*7.5);
      ray*=smoothstep(.9,.05,uv.y)*.18;

      vec3 gold=vec3(.81,.68,.41);
      vec3 cold=vec3(.38,.46,.60);
      vec3 col=mix(cold,gold,.68);
      float a=fog*.075+dust*.12+ray;
      gl_FragColor=vec4(col*a,a);
    }
  `;

  function shader(type,src){
    const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);
    if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));
    return s;
  }

  try{
    const program=gl.createProgram();
    gl.attachShader(program,shader(gl.VERTEX_SHADER,vert));
    gl.attachShader(program,shader(gl.FRAGMENT_SHADER,frag));
    gl.linkProgram(program);
    if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(program));
    gl.useProgram(program);

    const buf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buf);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
    const loc=gl.getAttribLocation(program,'p');
    gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,2,gl.FLOAT,false,0,0);

    const ur=gl.getUniformLocation(program,'r');
    const ut=gl.getUniformLocation(program,'t');
    const um=gl.getUniformLocation(program,'m');

    const scale=mobile?1:Math.min(window.devicePixelRatio||1,1.25);
    const targetFps=mobile?30:60;
    let last=0,frames=[],start=performance.now();

    function resize(){
      const w=Math.max(1,Math.floor(innerWidth*scale));
      const h=Math.max(1,Math.floor(innerHeight*scale));
      if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h)}
    }
    function draw(now){
      requestAnimationFrame(draw);
      const minStep=1000/targetFps;
      if(now-last<minStep)return;
      if(last)frames.push(now-last);
      last=now;
      if(frames.length>120)frames.shift();
      resize();
      gl.useProgram(program);
      gl.uniform2f(ur,canvas.width,canvas.height);
      gl.uniform1f(ut,reduceMotion?0:now*.001);
      gl.uniform2f(um,pointer.x,pointer.y);
      gl.drawArrays(gl.TRIANGLES,0,6);

      if(now-start>1800&&frames.length>20){
        atmosphereInfo.avgFrameMs=frames.reduce((a,b)=>a+b,0)/frames.length;
        html.dataset.frameMs=atmosphereInfo.avgFrameMs.toFixed(1);
      }
    }

    atmosphereInfo.mode='webgl';
    atmosphereInfo.tier=mobile?'mobile-30':'desktop-60';
    html.dataset.atmosphere='webgl';
    html.dataset.quality=atmosphereInfo.tier;
    requestAnimationFrame(draw);
  }catch(err){
    console.warn('LUMEN atmosphere fallback',err);
    atmosphereInfo.mode='css-fallback';
    html.dataset.atmosphere='fallback';
  }
}

function markQAReady(){
  if(!QA)return;
  requestAnimationFrame(()=>requestAnimationFrame(()=>{
    html.dataset.qaReady=QA;
    html.dataset.qaStage=state.stage;
    html.dataset.qaInnerWidth=String(innerWidth);
    html.dataset.qaScrollWidth=String(document.documentElement.scrollWidth);
  }));
}

function applyQA(){
  if(!QA)return false;
  state.situation='J’attends une réponse importante et je veux distinguer ce qui dépend de mon prochain geste.';
  state.reflection='Je peux séparer le fait observé de ce que j’ajoute, puis choisir la prochaine prise réellement disponible.';
  state.page=QA==='reading-late'?3:0;

  if(QA==='entry'){state.stage='entry'}
  else if(QA==='threshold'){state.stage='threshold'}
  else if(QA==='reading'||QA==='reading-late'){state.stage='reading'}
  else if(QA==='reflection'){state.stage='reflection'}
  else if(QA==='complete'){state.stage='complete'}
  else state.stage='threshold';
  return true;
}

async function boot(){
  initAtmosphere();
  await loadContent();
  wire();

  const qa=applyQA();
  if(!qa && state.stage!=='entry' && !['threshold','reading','reflection','complete'].includes(state.stage)){
    state={...defaults};
  }

  setStage(state.stage,{persist:false,announce:false});
  if(state.stage==='reading')renderPage();
  markQAReady();

  window.__LUMEN_CINEMATIC__={
    get state(){return {...state}},
    get atmosphere(){return {...atmosphereInfo}},
    get pointer(){return {...pointer}},
    setStage
  };

  if(!reduceMotion)requestAnimationFrame(animateCamera);
}

boot().catch(err=>{
  console.error(err);
  html.dataset.bootError=String(err?.message||err);
});
