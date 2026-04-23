// ── Word list ────────────────────────────────────────────────────────────
const WORDS = ["apple","apply","application","ant","anchor","alphabet","astronaut","bat","batman","battle","bee","balloon","butterfly","bridge","cat","caterpillar","car","cart","castle","candy","clock","dog","door","dolphin","dragon","doctor","diamond","dance","elephant","engine","envelope","eagle","earth","eclipse","energy","fish","football","friend","frog","feather","flower","forest","giraffe","grape","grapefruit","garden","guitar","galaxy","ghost","hamster","helicopter","honey","house","heart","horizon","highway","insect","ink","island","ice","iceberg","icecream","igloo","jacket","jelly","jungle","jewel","journey","jigsaw","journal","kangaroo","keyboard","kitten","kitchen","kingdom","kite","knight","lemon","leopard","library","lion","lake","ladder","lantern","magic","mango","market","mansion","mountain","mouse","mirror","notebook","novel","night","needle","ninja","nectar","nature","octopus","orange","ocean","owl","orchard","oasis","orbit","panda","parrot","peach","pearl","pencil","penguin","piano","queen","quilt","quill","quiz","quartz","quiver","quick","rabbit","rainbow","race","river","robot","rocket","ruler","snake","snow","sand","space","star","ship","station","tiger","train","tree","tunnel","tornado","tower","temple","umbrella","unicorn","universe","umpire","uproot","uncle","upward","van","valley","vase","volcano","violin","village","victory","whale","watermelon","window","wizard","wolf","wheel","world","xylophone","x-ray","xenon","yacht","yarn","yellow","yogurt","year","yolk","yard","zebra","zoo","zucchini","zero","zipper","zone","zombie"];

// ── Trie (Autocomplete + Fuzzy) ─────────────────────────────────────────
class TrieNode { constructor(){this.ch={};this.end=false} }
class Trie {
  constructor(){this.root=new TrieNode()}
  insert(w){let n=this.root;for(const c of w){if(!n.ch[c])n.ch[c]=new TrieNode();n=n.ch[c]}n.end=true}
  _traverse(prefix){let n=this.root;for(const c of prefix){if(!n.ch[c])return null;n=n.ch[c]}return n}
  autocomplete(prefix,limit=12){
    const node=this._traverse(prefix);
    if(!node)return[];
    const res=[];
    const dfs=(n,s)=>{if(res.length>=limit)return;if(n.end)res.push(s);for(const[c,ch]of Object.entries(n.ch))dfs(ch,s+c)}
    dfs(node,prefix);return res;
  }
  fuzzy(word,maxD=1){
    const row=Array.from({length:word.length+1},(_,i)=>i),res=[];
    const rec=(n,ch,prev,cur)=>{
      const r=[prev[0]+1];
      for(let i=1;i<=word.length;i++)r.push(Math.min(r[i-1]+1,prev[i]+1,prev[i-1]+(word[i-1]===ch?0:1)));
      if(r[word.length]<=maxD&&n.end)res.push([cur,r[word.length]]);
      if(Math.min(...r)<=maxD)for(const[c,child]of Object.entries(n.ch))rec(child,c,r,cur+c);
    }
    for(const[c,child]of Object.entries(this.root.ch))rec(child,c,row,c);
    return res.sort((a,b)=>a[1]-b[1]);
  }
}
const trie=new Trie();WORDS.forEach(w=>trie.insert(w));

// ── Aho-Corasick (DNA) ──────────────────────────────────────────────────
class AhoNode{constructor(){this.ch={};this.fail=null;this.out=[];this.end=false}}
class AhoCorasick{
  constructor(){this.root=new AhoNode()}
  add(p){let n=this.root;for(const c of p){if(!n.ch[c])n.ch[c]=new AhoNode();n=n.ch[c]}n.end=true;n.out.push(p)}
  build(){
    const q=[];
    for(const ch of Object.values(this.root.ch)){ch.fail=this.root;q.push(ch)}
    let i=0;
    while(i<q.length){
      const cur=q[i++];
      for(const[c,child]of Object.entries(cur.ch)){
        let f=cur.fail;
        while(f&&!f.ch[c])f=f.fail;
        child.fail=(f?f.ch[c]:null)||this.root;
        if(child.fail===child)child.fail=this.root;
        child.out=[...child.out,...child.fail.out];
        q.push(child);
      }
    }
  }
  search(text){
    const m={};let cur=this.root;
    for(let i=0;i<text.length;i++){
      const c=text[i];
      while(cur!==this.root&&!cur.ch[c])cur=cur.fail;
      if(cur.ch[c])cur=cur.ch[c];
      for(const p of cur.out){if(!m[p])m[p]=[];m[p].push(i-p.length+1)}
    }
    return m;
  }
}

// ── IP Binary Trie ──────────────────────────────────────────────────────
class IPNode{constructor(){this.ch={0:null,1:null};this.route=null}}
class IPTrie{
  constructor(){this.root=new IPNode()}
  _bits(ip){return ip.split('.').flatMap(o=>parseInt(o).toString(2).padStart(8,'0').split('').map(Number))}
  _mlen(mask){return mask.split('.').flatMap(o=>parseInt(o).toString(2).padStart(8,'0').split('')).filter(b=>b==='1').length}
  insert(net,mask,label){
    const bits=this._bits(net),pl=this._mlen(mask);
    let n=this.root;
    for(let i=0;i<pl;i++){const b=bits[i];if(!n.ch[b])n.ch[b]=new IPNode();n=n.ch[b]}
    n.route={net,mask,label,pl};
  }
  lpm(ip){
    const bits=this._bits(ip);let n=this.root,best=null;
    for(const b of bits){if(n.route)best=n.route;if(!n.ch[b])break;n=n.ch[b]}
    if(n.route)best=n.route;return best;
  }
}

// ── URL Trie ─────────────────────────────────────────────────────────────
const WC=':*';
class URLNode{constructor(seg=''){this.seg=seg;this.ch={};this.end=false;this.handler=''}}
class URLTrie{
  constructor(){this.root=new URLNode()}
  _split(url){return url.split('/').filter(s=>s)}
  _isP(s){return s.startsWith(':')}
  add(url,handler=''){
    const parts=this._split(url);let n=this.root;
    for(const p of parts){const k=this._isP(p)?WC:p;if(!n.ch[k])n.ch[k]=new URLNode(p);n=n.ch[k]}
    n.end=true;n.handler=handler||url;
  }
  route(url){return this._match(this.root,this._split(url),0,{})}
  _match(n,parts,d,params){
    if(d===parts.length)return n.end?{handler:n.handler,params}:null;
    const seg=parts[d];
    if(n.ch[seg]){const r=this._match(n.ch[seg],parts,d+1,params);if(r)return r}
    if(n.ch[WC]){const w=n.ch[WC],pname=w.seg.slice(1),r=this._match(w,parts,d+1,{...params,[pname]:seg});if(r)return r}
    return null;
  }
}

// ── GC Content & Reverse Complement ────────────────────────────────────
const gcContent=s=>s?Math.round(s.split('').filter(c=>'GC'.includes(c)).length/s.length*1000)/10:0;
const revComp=s=>[...s.toUpperCase()].map(c=>({A:'T',T:'A',G:'C',C:'G'}[c]||c)).reverse().join('');

// ── Color palette ────────────────────────────────────────────────────────
const COLORS=['#00d4ff','#10b981','#f97316','#a855f7','#f59e0b','#ef4444','#06b6d4','#ec4899'];

// ══════════════════════════════════════════════════════════════════════
//  TAB 1: AUTOCOMPLETE
// ══════════════════════════════════════════════════════════════════════
let fuzzyMode=false;
document.getElementById('toggleFuzzy').addEventListener('click',function(){
  fuzzyMode=!fuzzyMode;this.classList.toggle('on',fuzzyMode);
  document.getElementById('fuzzyLabel').textContent=fuzzyMode?'Fuzzy ON':'Fuzzy OFF';
  runAutoComplete();
});
document.getElementById('acInput').addEventListener('input',runAutoComplete);
document.getElementById('acInput').addEventListener('keydown',e=>{if(e.key==='Enter')runAutoComplete()});

function runAutoComplete(){
  const q=document.getElementById('acInput').value.trim().toLowerCase();
  const out=document.getElementById('acResults');
  const count=document.getElementById('acCount');
  if(!q){out.innerHTML='<div class="empty">Start typing to see suggestions…</div>';count.textContent='';return}
  let results;
  if(fuzzyMode){
    results=trie.fuzzy(q,1);
    if(!results.length){out.innerHTML='<div class="empty">No fuzzy matches found.</div>';count.textContent='';return}
    count.textContent=results.length+' match'+(results.length!==1?'es':'');
    out.innerHTML=results.map(([w,d])=>`
      <div class="suggestion">
        <span>${w.startsWith(q)?'<span class="match">'+q+'</span>'+w.slice(q.length):w}</span>
        <span class="dist">dist: ${d}</span>
      </div>`).join('');
  } else {
    results=trie.autocomplete(q,15);
    if(!results.length){out.innerHTML='<div class="empty">No matches. Try fuzzy mode!</div>';count.textContent='';return}
    count.textContent=results.length+' suggestion'+(results.length!==1?'s':'');
    out.innerHTML=results.map(w=>`
      <div class="suggestion">
        <span class="match">${w.slice(0,q.length)}</span><span>${w.slice(q.length)}</span>
      </div>`).join('');
  }
}

// ══════════════════════════════════════════════════════════════════════
//  TAB 2: DNA
// ══════════════════════════════════════════════════════════════════════
document.getElementById('dnaRun').addEventListener('click',runDNA);

function runDNA(){
  const seq=document.getElementById('dnaSeq').value.trim().toUpperCase().replace(/[^ACGT]/g,'');
  const rawPats=document.getElementById('dnaPatterns').value.trim().toUpperCase();
  const patterns=rawPats.split(/[\n,]+/).map(p=>p.trim().replace(/[^ACGT]/g,'')).filter(Boolean);
  const seqDisp=document.getElementById('seqDisplay');
  const matchInfo=document.getElementById('matchInfo');
  const statsDiv=document.getElementById('dnaStats');

  statsDiv.innerHTML=`
    <div class="stat">GC Content: <b>${gcContent(seq)}%</b></div>
    <div class="stat">Length: <b>${seq.length} bp</b></div>
    <div class="stat" style="word-break:break-all;max-width:300px">Rev-Comp: <b style="font-size:.75rem">${revComp(seq).slice(0,30)}${seq.length>30?'…':''}</b></div>`;

  if(!seq||!patterns.length){seqDisp.textContent='No sequence to display.';matchInfo.innerHTML='';return}

  const aho=new AhoCorasick();
  patterns.forEach(p=>aho.add(p));aho.build();
  const matches=aho.search(seq);

  // Build highlighted sequence
  const colors={};patterns.forEach((p,i)=>colors[p]=COLORS[i%COLORS.length]);
  const highlighted=Array.from({length:seq.length},(_,i)=>({char:seq[i],color:null}));
  for(const[pat,positions]of Object.entries(matches)){
    for(const pos of positions){
      for(let i=pos;i<pos+pat.length;i++)if(i<seq.length)highlighted[i].color=colors[pat];
    }
  }
  seqDisp.innerHTML=highlighted.map(({char,color})=>
    color?`<span style="background:${color}22;color:${color};font-weight:600;border-radius:3px">${char}</span>`:char
  ).join('');

  // Table
  if(!Object.keys(matches).length){matchInfo.innerHTML='<div class="empty">No patterns matched in this sequence.</div>';return}
  matchInfo.innerHTML=`<table class="match-table">
    <thead><tr><th>Pattern</th><th>Positions (0-indexed)</th><th>Count</th></tr></thead>
    <tbody>${Object.entries(matches).map(([p,pos])=>`
      <tr>
        <td><span class="pattern-chip" style="background:${colors[p]}22;color:${colors[p]}">${p}</span></td>
        <td class="mono">${pos.join(', ')}</td>
        <td class="mono">${pos.length}</td>
      </tr>`).join('')}
    </tbody></table>`;
}

// ══════════════════════════════════════════════════════════════════════
//  TAB 3: IP ROUTING
// ══════════════════════════════════════════════════════════════════════
const ipTrie=new IPTrie();
const defaultRoutes=[
  {net:'192.168.1.0',mask:'255.255.255.0',label:'LAN-A'},
  {net:'192.168.2.0',mask:'255.255.255.0',label:'LAN-B'},
  {net:'10.0.0.0',mask:'255.0.0.0',label:'WAN-Class-A'},
  {net:'172.16.0.0',mask:'255.240.0.0',label:'Private-B'},
];
defaultRoutes.forEach(r=>ipTrie.insert(r.net,r.mask,r.label));
let ipRoutes=[...defaultRoutes];
let lastLPMNet=null;

function renderIPTable(){
  document.getElementById('ipTable').innerHTML=`<table class="route-table"><thead><tr><th>Network</th><th>Mask</th><th>Label</th><th>/CIDR</th></tr></thead>
    <tbody>${ipRoutes.map(r=>`<tr class="${lastLPMNet===r.net?'highlighted':''}">
      <td>${r.net}</td><td>${r.mask}</td><td>${r.label}</td>
      <td>${ipTrie.root&&r.net?r.net:''}</td>
    </tr>`).join('')}</tbody></table>`;
}
renderIPTable();

document.getElementById('ipLookup').addEventListener('click',()=>{
  const ip=document.getElementById('ipInput').value.trim();
  const out=document.getElementById('ipResult');
  try{
    const bits=ipTrie._bits(ip);
    if(bits.length!==32)throw new Error('Invalid');
    const route=ipTrie.lpm(ip);
    lastLPMNet=route?route.net:null;
    renderIPTable();
    if(route){
      out.innerHTML=`<div class="result-box result-ok">
        <div class="result-label" style="color:#10b981">✓ Route Found — Longest Prefix Match</div>
        <div class="mono" style="font-size:.95rem;margin-bottom:8px">${ip}</div>
        <div style="font-size:.85rem;color:var(--muted)">Best route → <span style="color:#f97316;font-family:var(--mono)">${route.net} / ${route.mask}</span></div>
        <div style="font-size:.85rem;margin-top:4px">Label: <b>${route.label}</b> &nbsp;·&nbsp; Prefix length: <b>/${route.pl} bits</b></div>
      </div>`;
    } else {
      out.innerHTML=`<div class="result-box result-err">❌ No route found — packet would be dropped.</div>`;
    }
  } catch(e){out.innerHTML=`<div class="result-box result-err">Invalid IP address format.</div>`}
});

document.getElementById('ipAddRoute').addEventListener('click',()=>{
  const net=document.getElementById('ipNewNet').value.trim();
  const mask=document.getElementById('ipNewMask').value.trim();
  const label=document.getElementById('ipNewLabel').value.trim()||'custom';
  if(!net||!mask)return;
  try{ipTrie._bits(net);ipTrie.insert(net,mask,label);ipRoutes.push({net,mask,label});renderIPTable()}
  catch(e){alert('Invalid network/mask format')}
});

// ══════════════════════════════════════════════════════════════════════
//  TAB 4: URL ROUTING
// ══════════════════════════════════════════════════════════════════════
const urlTrie=new URLTrie();
const defaultRoutes_url=[
  {url:'/home','handler':'home_page'},
  {url:'/about','handler':'about_page'},
  {url:'/user/:id','handler':'user_profile'},
  {url:'/user/:id/posts','handler':'user_posts'},
  {url:'/user/:id/posts/:postId','handler':'post_detail'},
  {url:'/shop/:category','handler':'shop_category'},
  {url:'/shop/:category/:item','handler':'item_detail'},
];
defaultRoutes_url.forEach(r=>urlTrie.add(r.url,r.handler));
let urlRoutes=[...defaultRoutes_url];
let lastMatchedHandler=null;

function renderURLList(){
  document.getElementById('urlList').innerHTML=urlRoutes.map(r=>`
    <li class="${lastMatchedHandler===r.handler?'matched':''}">
      <span class="method">GET</span>
      <span class="mono">${r.url}</span>
      <span class="handler">${r.handler}</span>
    </li>`).join('');
}
renderURLList();

document.getElementById('urlMatch').addEventListener('click',()=>{
  const url=document.getElementById('urlInput').value.trim();
  const out=document.getElementById('urlResult');
  const result=urlTrie.route(url);
  lastMatchedHandler=result?result.handler:null;
  renderURLList();
  if(result){
    const hasParams=Object.keys(result.params).length>0;
    out.innerHTML=`<div class="result-box result-ok">
      <div class="result-label" style="color:#a855f7">✓ Route Matched</div>
      <div style="font-size:.85rem">Handler: <b>${result.handler}</b></div>
      ${hasParams?`<div class="params-box" style="margin-top:10px">
        <div style="font-size:.72rem;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:8px">Extracted Params</div>
        ${Object.entries(result.params).map(([k,v])=>`<div><span class="pk">:${k}</span> → <span class="pv">"${v}"</span></div>`).join('')}
      </div>`:'<div style="font-size:.82rem;color:var(--muted);margin-top:6px">No path parameters.</div>'}
    </div>`;
  } else {
    out.innerHTML=`<div class="result-box result-err">❌ 404 — No matching route found.</div>`;
  }
});

document.getElementById('urlAdd').addEventListener('click',()=>{
  const url=document.getElementById('urlNew').value.trim();
  const handler=document.getElementById('urlHandler').value.trim()||'custom_handler';
  if(!url)return;
  urlTrie.add(url,handler);urlRoutes.push({url,handler});
  document.getElementById('urlNew').value='';document.getElementById('urlHandler').value='';
  renderURLList();
});

// ── Tab switching ────────────────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(tab=>{
  tab.addEventListener('click',()=>{
    document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('panel'+tab.dataset.tab).classList.add('active');
  });
});
