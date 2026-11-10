/* Progressive enhancements; all articles and navigation work without JavaScript. */
'use strict';
document.body.classList.add('js');
const root = document.body.dataset.root || '';
const menu = document.querySelector('.menu-toggle');
const sidebar = document.querySelector('.sidebar');
const mobile = window.matchMedia('(max-width: 700px)');
function syncSidebar() { sidebar.inert = mobile.matches && menu.getAttribute('aria-expanded') !== 'true'; }
function closeMenu() {
  if (mobile.matches && sidebar.contains(document.activeElement)) menu.focus();
  menu.setAttribute('aria-expanded', 'false'); sidebar.classList.remove('is-open'); syncSidebar();
}
mobile.addEventListener('change', () => { closeMenu(); syncSidebar(); });
syncSidebar();
menu.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  sidebar.classList.toggle('is-open', open);
  syncSidebar();
});
document.addEventListener('click', event => {
  if (!sidebar.contains(event.target) && !menu.contains(event.target)) closeMenu();
});
document.addEventListener('keydown', event => { if (event.key === 'Escape') closeMenu(); });

const dialog = document.querySelector('.search-dialog');
const input = document.querySelector('#search-input');
const results = document.querySelector('.search-results');
const status = document.querySelector('.search-status');
let index = JSON.parse(document.querySelector('#search-fallback').textContent);
const normalize = value => value.toLocaleLowerCase('ru').replaceAll('ё', 'е');
function search() {
  const words = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
  const matches = index.map(item => {
    const title = normalize(item.title);
    const text = normalize(`${item.title} ${item.group} ${item.text}`);
    return { item, score: words.reduce((n, word) => n + (title.includes(word) ? 3 : 0), 0), match: words.every(word => text.includes(word)) };
  }).filter(entry => entry.match).sort((a, b) => b.score - a.score).slice(0, 15);
  results.replaceChildren();
  for (const { item } of matches) {
    const a = document.createElement('a');
    a.href = root + item.path;
    const title = document.createElement('strong'); title.textContent = item.title;
    const group = document.createElement('small'); group.textContent = item.group;
    a.append(title, group); results.append(a);
  }
  status.textContent = words.length ? (matches.length ? `Найдено страниц: ${matches.length}` : 'Ничего не найдено. Попробуйте «сцена», «C++» или «свет».') : 'Все разделы руководства';
}
function openSearch() { closeMenu(); if (!dialog.open) dialog.showModal(); search(); input.focus(); }
document.querySelector('.search-open').addEventListener('click', openSearch);
document.querySelector('.search-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
input.addEventListener('input', search);
document.addEventListener('keydown', event => {
  if (event.key === '/' && !dialog.open && !/INPUT|TEXTAREA|SELECT/.test(event.target.tagName) && !event.target.isContentEditable) { event.preventDefault(); openSearch(); }
});
// Local-file viewing uses the embedded index. HTTP uses the separate JSON resource.
if (location.protocol !== 'file:') fetch(root + 'search-index.json').then(response => { if (!response.ok) throw new Error('Search index unavailable'); return response.json(); }).then(data => { index = data; if (dialog.open) search(); }).catch(() => {});

document.querySelectorAll('pre').forEach(pre => {
  const code = pre.querySelector('code');
  if (!code) return;
  const button = document.createElement('button');
  button.type = 'button'; button.className = 'copy-code'; button.textContent = 'Копировать'; button.setAttribute('aria-live', 'polite');
  button.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(code.textContent); button.textContent = 'Скопировано'; }
    catch (_) {
      const selection = window.getSelection(); const range = document.createRange(); range.selectNodeContents(code); selection.removeAllRanges(); selection.addRange(range); button.textContent = 'Выделено: Ctrl/Cmd + C';
    }
    setTimeout(() => { button.textContent = 'Копировать'; }, 2500);
  });
  pre.prepend(button);
});

document.querySelectorAll('[data-scene]').forEach(container => {
  const canvas = container.querySelector('canvas');
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const pause = container.querySelector('[data-pause]');
  const wire = container.querySelector('[data-wire]');
  const speed = container.querySelector('[data-speed]');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let paused = reduced.matches, wireframe = false, angle = 0.5, previous = 0, visible = false, frame = 0;
  const vertices = [[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]];
  const faces = [[0,1,2,3],[4,7,6,5],[0,4,5,1],[3,2,6,7],[0,3,7,4],[1,5,6,2]];
  function project(v) { const [x,y,z] = v; return [480 + (x-z)*88, 265 + (x+z)*34-y*90]; }
  function path(points) { ctx.beginPath(); points.forEach((p,i) => { if(i) ctx.lineTo(...p); else ctx.moveTo(...p); }); ctx.closePath(); }
  function draw() {
    ctx.fillStyle = '#182e28'; ctx.fillRect(0,0,960,520);
    ctx.strokeStyle = '#2c4738'; ctx.lineWidth = 1;
    for(let i=-6;i<=6;i++) {
      ctx.beginPath(); ctx.moveTo(...project([i,-1.6,-6])); ctx.lineTo(...project([i,-1.6,6])); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(...project([-6,-1.6,i])); ctx.lineTo(...project([6,-1.6,i])); ctx.stroke();
    }
    ctx.fillStyle = '#0e211b66'; ctx.beginPath(); ctx.ellipse(480,365,165,48,0,0,Math.PI*2); ctx.fill();
    const points = vertices.map(([x,y,z]) => [x*Math.cos(angle)-z*Math.sin(angle),y+0.1,x*Math.sin(angle)+z*Math.cos(angle)]);
    faces.map((face,i)=>({face,i,depth:face.reduce((n,v)=>n+points[v][0]+points[v][2],0)})).sort((a,b)=>a.depth-b.depth).forEach(({face,i})=>{
      path(face.map(v=>project(points[v])));
      if(!wireframe){ctx.fillStyle=['#4a997e','#72b99a','#4c9279','#c1d7a2','#34816d','#67a98b'][i];ctx.fill();}
      ctx.strokeStyle=wireframe?'#badc9d':'#c8e3ae88';ctx.lineWidth=2;ctx.stroke();
    });
    ctx.fillStyle='#93b483';ctx.font='11px monospace';ctx.fillText('X',820,458);ctx.fillText('Y',136,458);ctx.fillText('Z',486,56);
  }
  function updatePause(){pause.textContent=paused?'Продолжить':'Пауза';pause.setAttribute('aria-pressed',String(paused));}
  function tick(time){frame=0;if(!visible||paused)return;if(previous) angle+=(time-previous)/1000*Number(speed.value)*Math.PI/180;previous=time;draw();frame=requestAnimationFrame(tick);}
  function start(){previous=0;if(visible&&!paused&&!frame)frame=requestAnimationFrame(tick);}
  pause.addEventListener('click',()=>{paused=!paused;updatePause();if(paused){cancelAnimationFrame(frame);frame=0;}else start();});
  wire.addEventListener('click',()=>{wireframe=!wireframe;wire.setAttribute('aria-pressed',String(wireframe));draw();});
  speed.addEventListener('input',()=>{container.querySelector('output').value=`${speed.value}°/с`;});
  reduced.addEventListener('change',event=>{if(event.matches){paused=true;cancelAnimationFrame(frame);frame=0;updatePause();draw();}});
  document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(frame);frame=0;}else start();});
  new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible)start();else{cancelAnimationFrame(frame);frame=0;}}).observe(canvas);
  updatePause();draw();
});
