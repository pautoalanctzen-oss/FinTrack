(function(){
  function pad(n){return n<10?"0"+n:""+n}
  function build(container,input){
    // Ensure wrapper keeps its class and we add container class
    container.classList.add("mdp-container");
    const panel = document.createElement('div');
    panel.className = 'mdp-panel';

    const header = document.createElement('div');
    header.className = 'mdp-header';

    const prev = document.createElement('button');
    prev.type = 'button'; prev.className = 'mdp-arrow'; prev.setAttribute('aria-label','Anterior');
    prev.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>';
    const next = document.createElement('button');
    next.type = 'button'; next.className = 'mdp-arrow'; next.setAttribute('aria-label','Siguiente');
    next.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>';

    const yearLabel = document.createElement('span'); yearLabel.className='mdp-year';

    const monthSelect = document.createElement('select');
    monthSelect.className = 'mdp-month';
    const months = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
    months.forEach((m,i)=>{const o=document.createElement('option'); o.value=i+1; o.textContent=m; monthSelect.appendChild(o);});

    header.appendChild(prev); header.appendChild(yearLabel); header.appendChild(next); header.appendChild(monthSelect);

    const daysGrid = document.createElement('div');
    daysGrid.className='mdp-days';

    panel.appendChild(header);
    panel.appendChild(daysGrid);
    container.appendChild(panel);

    // state
    let date = new Date();
    function syncFromInput(){
      const v = input.value;
      if(v){
        const parts = v.split('-');
        const y = parseInt(parts[0]);
        const m = parseInt(parts[1]);
        const d = parts[2]?parseInt(parts[2]):1;
        if(!isNaN(y)&&!isNaN(m)&&!isNaN(d)) date = new Date(y,m-1,d);
      }
    }
    function render(){
      yearLabel.textContent = date.getFullYear();
      monthSelect.value = (date.getMonth()+1);
      daysGrid.innerHTML = '';
      const y = date.getFullYear();
      const m = date.getMonth();
      const first = new Date(y,m,1);
      const last = new Date(y,m+1,0);
      const startWeekday = first.getDay(); // 0-6
      // weekday labels
      const wl = ['D','L','M','X','J','V','S'];
      const head = document.createElement('div'); head.className='mdp-weekdays';
      wl.forEach(w=>{const el=document.createElement('div'); el.textContent=w; head.appendChild(el);});
      daysGrid.appendChild(head);
      // empty slots
      for(let i=0;i<startWeekday;i++){const s=document.createElement('div'); s.className='mdp-empty'; daysGrid.appendChild(s);}    
      for(let d=1; d<= last.getDate(); d++){
        const btn = document.createElement('button'); btn.type='button'; btn.className='mdp-day'; btn.textContent = d;
        if(d === date.getDate()) btn.classList.add('active');
        btn.addEventListener('click',()=>{
          date = new Date(y,m,d);
          input.value = y+'-'+pad(m+1)+'-'+pad(d);
          input.dispatchEvent(new Event('change'));
          hide();
        });
        daysGrid.appendChild(btn);
      }
    }
    function show(){ container.classList.add('open'); }
    function hide(){ container.classList.remove('open'); }

    prev.addEventListener('click',()=>{ date = new Date(date.getFullYear()-1, date.getMonth(), date.getDate()); render(); });
    next.addEventListener('click',()=>{ date = new Date(date.getFullYear()+1, date.getMonth(), date.getDate()); render(); });
    monthSelect.addEventListener('change',()=>{ const m = parseInt(monthSelect.value)-1; date = new Date(date.getFullYear(), m, 1); render(); });

    document.addEventListener('click', (e)=>{ if(!container.contains(e.target) && e.target!==input) hide(); });
    // Prevent native picker / keyboard and route to custom UI
    try { input.readOnly = true; } catch {}
    input.addEventListener('mousedown', (e)=>{ e.preventDefault(); syncFromInput(); render(); position(); show(); });
    input.addEventListener('focus', (e)=>{ e.preventDefault && e.preventDefault(); syncFromInput(); render(); position(); show(); });
    input.addEventListener('click', (e)=>{ e.preventDefault && e.preventDefault(); syncFromInput(); render(); position(); show(); });

    function position(){
      const rect = input.getBoundingClientRect();
      panel.style.top = (input.offsetTop + input.offsetHeight + 4) + 'px';
      panel.style.left = (input.offsetLeft) + 'px';
      panel.style.minWidth = Math.max(280, input.offsetWidth) + 'px';
    }
  }

  function init(){
    const inputs = document.querySelectorAll('input[data-datepicker="modern"]');
    console.log('Modern datepicker init - found', inputs.length, 'inputs');
    // Inject CSS to hide native picker indicator (Chrome/Edge)
    const style = document.createElement('style');
    style.textContent = 'input[data-datepicker="modern"]::-webkit-calendar-picker-indicator{opacity:0; display:none;}';
    document.head.appendChild(style);
    inputs.forEach(input=>{
      const wrap = document.createElement('div');
      wrap.className='mdp-wrap';
      input.parentNode.insertBefore(wrap, input);
      wrap.appendChild(input);
      // Force text type to fully disable native pickers across browsers
      try { input.type = 'text'; } catch {}
      // Add a small calendar icon to hint interactivity
      const ico = document.createElement('span');
      ico.setAttribute('aria-hidden','true');
      ico.style.position='absolute';
      ico.style.right='10px';
      ico.style.top='50%';
      ico.style.transform='translateY(-50%)';
      ico.style.color='#6c757d';
      ico.style.pointerEvents='none';
      ico.innerHTML='📅'; // calendar emoji
      wrap.style.position='relative';
      wrap.appendChild(ico);
      build(wrap,input);
    });
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
