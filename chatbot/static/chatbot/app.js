(() => {
  const overlay = document.getElementById('chat-overlay');
  const messages = document.getElementById('chat-messages');
  const input = document.getElementById('chat-input');
  const form = document.getElementById('chat-form');
  const rows = document.getElementById('lead-rows');
  const empty = document.getElementById('empty-state');
  let sessionId = localStorage.getItem('amk_session') || crypto.randomUUID();
  localStorage.setItem('amk_session', sessionId);
  let context = {};
  let filter = 'all';
  let greeted = false;

  const esc = (s) => String(s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const initials = name => (name || 'G').split(/\s+/).slice(0,2).map(x=>x[0]||'').join('').toUpperCase();
  const openChat = async () => {
    overlay.classList.add('open'); overlay.setAttribute('aria-hidden','false');
    if (!greeted) {
      greeted=true;
      try {
        const response=await fetch(`/api/chat/history/${encodeURIComponent(sessionId)}/`);
        const history=await response.json(); context=history.context||{};
        if(history.messages?.length){history.messages.forEach(m=>addMessage(m.role==='user'?'user':'bot',m.body));}
        else addMessage('bot','Hello! Welcome to AMK Hospitality. I can help with weddings & events, travel plans, and our other services. What brings you here today?',['Plan an event','Plan a trip','Other services','Ask a question']);
      } catch(_){ addMessage('bot','Hello! Welcome to AMK Hospitality. I can help with weddings & events, travel plans, and our other services. What brings you here today?',['Plan an event','Plan a trip','Other services','Ask a question']); }
    }
    setTimeout(()=>input.focus(),120);
  };
  const closeChat = () => { overlay.classList.remove('open'); overlay.setAttribute('aria-hidden','true'); };
  document.getElementById('new-enquiry').addEventListener('click',openChat);
  document.getElementById('launch-chat').addEventListener('click',openChat);
  document.getElementById('empty-preview').addEventListener('click',openChat);
  document.getElementById('close-chat').addEventListener('click',closeChat);
  overlay.addEventListener('click',e=>{if(e.target===overlay)closeChat()});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeChat()});

  function addMessage(who,text,quick=[]) {
    const wrap=document.createElement('div');
    const bubble=document.createElement('div'); bubble.className=`message ${who}`; bubble.textContent=text;
    wrap.appendChild(bubble);
    if(who==='bot') { const time=document.createElement('div'); time.className='message-time'; time.textContent='AMK Assistant · just now'; wrap.appendChild(time); }
    messages.appendChild(wrap);
    if(quick && quick.length){ const chips=document.createElement('div'); chips.className='quick-replies'; quick.forEach(label=>{const b=document.createElement('button');b.type='button';b.textContent=label;b.addEventListener('click',()=>{if(label==='Open WhatsApp chat'){const link=document.querySelector('[data-channel="whatsapp"]');if(link)window.open(link.href,'_blank','noopener,noreferrer');}else send(label)});chips.appendChild(b)});messages.appendChild(chips); }
    messages.parentElement.scrollTop=messages.parentElement.scrollHeight;
  }
  function typing(){const el=document.createElement('div');el.className='message bot typing';el.innerHTML='<i></i><i></i><i></i>';messages.appendChild(el);messages.parentElement.scrollTop=messages.parentElement.scrollHeight;return el;}
  async function send(text) {
    if(!text.trim())return;
    addMessage('user',text);
    document.querySelectorAll('.quick-replies').forEach(x=>x.remove());
    input.value=''; const wait=typing();
    try {
      const res=await fetch('/api/chat/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text,context,session_id:sessionId})});
      const data=await res.json(); wait.remove();
      if(!res.ok) throw new Error(data.error||'Could not send your message');
      context=data.context||context;
      addMessage('bot',data.reply,data.quick_replies||[]);
      const preview=document.getElementById('latest-reply');if(preview)preview.textContent=data.reply;
      if(data.qualified || data.handoff_request) { refreshLeads(); }
      if(data.reset_conversation){
        setTimeout(()=>{
          sessionId=crypto.randomUUID();localStorage.setItem('amk_session',sessionId);context={};messages.innerHTML='';
          addMessage('bot','Hello! Welcome to AMK Hospitality. I can help with weddings & events, travel plans, and our other services. What brings you here today?',['Plan an event','Plan a trip','Other services','Ask a question']);
          greeted=true;
        },1800);
      }
      if(data.end_conversation){
        setTimeout(()=>{
          closeChat();sessionId=crypto.randomUUID();localStorage.setItem('amk_session',sessionId);context={};messages.innerHTML='';greeted=false;
        },1800);
      }
    } catch(err) { wait.remove(); addMessage('bot','I’m sorry — I couldn’t reach the assistant just now. Please try again in a moment.'); }
  }
  form.addEventListener('submit',e=>{e.preventDefault();send(input.value)});
  document.querySelectorAll('[data-message]').forEach(b=>b.addEventListener('click',()=>send(b.dataset.message)));

  const relativeDate = value => {
    const d=new Date(value); if(Number.isNaN(d.getTime()))return 'Just now';
    const mins=Math.floor((Date.now()-d.getTime())/60000); if(mins<1)return 'Just now'; if(mins<60)return `${mins}m ago`; if(mins<1440)return `${Math.floor(mins/60)}h ago`; return d.toLocaleDateString('en-IN',{day:'numeric',month:'short'});
  };
  function renderLeads(leads){
    rows.innerHTML='';
    const counts={all:leads.length,new:leads.filter(x=>x.status==='New').length,events:leads.filter(x=>x.department_key==='events').length,travel:leads.filter(x=>x.department_key==='travel').length};
    document.querySelectorAll('.stat-value').forEach((el,i)=>{const nums=[counts.all,counts.new,counts.events,counts.travel];if(nums[i]!==undefined)el.firstChild.textContent=nums[i]});
    const navCount=document.querySelector('.nav-count'); if(navCount)navCount.textContent=counts.all;
    const tabCounts=document.querySelectorAll('.tab span'); if(tabCounts[0])tabCounts[0].textContent=counts.all;if(tabCounts[1])tabCounts[1].textContent=counts.new;
    const visible=filter==='all'?leads:filter==='new'?leads.filter(x=>x.status==='New'):leads.filter(x=>x.department_key===filter);
    empty.classList.toggle('visible',visible.length===0);
    document.querySelector('.lead-table').style.display=visible.length?'table':'none';
    document.getElementById('table-caption').textContent=`Showing ${visible.length} ${visible.length===1?'enquiry':'enquiries'}`;
    visible.slice(0,8).forEach(lead=>{
      const tr=document.createElement('tr');
      const dept=lead.department_key||'other';
      const short=lead.requirement.length>48?lead.requirement.slice(0,47)+'…':lead.requirement;
      tr.innerHTML=`<td><div class="guest-cell"><span class="guest-avatar">${esc(initials(lead.name))}</span><span><span class="guest-name">${esc(lead.name)}</span><span class="guest-email">${esc(lead.email)}</span></span></div></td><td><span class="dept-pill ${esc(dept)}"><i></i>${esc(lead.department)}</span></td><td><span class="requirement-cell" title="${esc(lead.requirement)}">${esc(short)}</span></td><td>${relativeDate(lead.created_at)}</td><td><span class="status-pill ${esc((lead.status||'').toLowerCase())}">${esc(lead.status)}</span></td><td><button class="row-more" title="Open enquiry summary">···</button></td>`;
      tr.querySelector('.row-more').addEventListener('click',()=>openLead(lead));
      rows.appendChild(tr);
    });
  }
  async function refreshLeads(){try{const r=await fetch('/api/leads/');const d=await r.json();renderLeads(d.leads||[])}catch(_){}}
  async function refreshChannels(){
    const health=document.getElementById('channel-health');
    try{
      const response=await fetch('/api/channels/');const data=await response.json();let active=0;
      (data.channels||[]).forEach(channel=>{
        const row=document.querySelector(`[data-channel="${channel.id}"]`);if(!row)return;
        const state=row.querySelector('.channel-state');const label=row.querySelector('.channel-state-label');
        row.querySelector('.channel-detail').textContent=channel.detail;
        label.textContent=({active:'Active',connected:'Connected',waiting:'Waiting',setup:'Needs setup'})[channel.state]||channel.state;
        state.classList.toggle('pending',!['active','connected'].includes(channel.state));
        if(['active','connected'].includes(channel.state))active++;
      });
      health.textContent=`${active} ACTIVE`;
    }catch(_){health.textContent='UNAVAILABLE'}
  }
  const initial=JSON.parse(document.getElementById('initial-leads').textContent||'[]'); renderLeads(initial);
  refreshChannels();
  window.setInterval(()=>{refreshLeads();refreshChannels()},15000);
  document.querySelectorAll('.tab[data-filter]').forEach(tab=>tab.addEventListener('click',()=>{document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));tab.classList.add('active');filter=tab.dataset.filter;refreshLeads()}));
  document.getElementById('view-all').addEventListener('click',()=>{filter='all';document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active',t.dataset.filter==='all'));refreshLeads()});
  document.getElementById('filter-toggle').addEventListener('click',()=>{filter=filter==='all'?'new':'all';document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active',t.dataset.filter===filter));refreshLeads()});

  const leadOverlay=document.getElementById('lead-overlay');
  let activeLead=null;
  function openLead(lead){
    activeLead=lead;
    document.getElementById('lead-dialog-title').textContent=lead.name;
    document.getElementById('lead-status-select').value=({New:'new',Contacted:'contacted',Converted:'converted',Closed:'closed'})[lead.status]||'new';
    const pairs=[['Department',lead.department],['Received via',lead.channel||'website'],['Requirement',lead.requirement],['Location',lead.location],['Event / travel date',lead.date],['Budget',lead.budget],['Email',lead.email],['Phone',lead.phone||'Not provided']];
    document.getElementById('lead-detail-content').innerHTML=pairs.map(([label,value])=>`<div class="lead-detail-item"><small>${esc(label)}</small><strong>${esc(value||'Not provided')}</strong></div>`).join('');
    leadOverlay.classList.add('open');leadOverlay.setAttribute('aria-hidden','false');
  }
  function closeLead(){leadOverlay.classList.remove('open');leadOverlay.setAttribute('aria-hidden','true');activeLead=null;}
  document.getElementById('close-lead').addEventListener('click',closeLead);
  leadOverlay.addEventListener('click',e=>{if(e.target===leadOverlay)closeLead()});
  document.getElementById('save-lead-status').addEventListener('click',async()=>{
    if(!activeLead)return;
    const button=document.getElementById('save-lead-status');button.disabled=true;button.textContent='Saving…';
    try{
      const response=await fetch(`/api/leads/${activeLead.id}/`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:document.getElementById('lead-status-select').value})});
      const data=await response.json();if(!response.ok)throw new Error(data.error||'Could not update lead');
      closeLead();await refreshLeads();
    }catch(_){button.textContent='Could not save';}
    finally{button.disabled=false;setTimeout(()=>button.textContent='Save status',1200);}
  });
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeLead()});
})();
