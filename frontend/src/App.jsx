import React, { useEffect, useMemo, useState } from 'react'

const API = 'http://127.0.0.1:5000'

function Badge({ text, kind="neutral" }) {
  const bg = {
    neutral: '#22304a',
    warn: '#664400',
    danger: '#5a1a1a',
    ok: '#1e4d2b',
  }[kind] || '#22304a'
  return (
    <span style={{
      padding:'4px 8px', borderRadius: 999, fontSize: 12, background: bg, color:'#fff'
    }}>{text}</span>
  )
}

function Toolbar({ onRefresh, onCreate }) {
  return (
    <div style={{display:'flex', gap:12, alignItems:'center', marginBottom:16}}>
      <button onClick={onRefresh} className="btn">Refresh</button>
      <button onClick={onCreate} className="btn btn-secondary">New RFI</button>
      <a className="btn btn-ghost" href={`${API}/files/notifications.csv`} target="_blank" rel="noreferrer">Open Notifications CSV</a>
      <style>{`
        .btn { background:#2d6ef7; border:0; color:white; padding:10px 14px; border-radius:12px; cursor:pointer; }
        .btn:hover{ filter:brightness(1.1); }
        .btn-secondary{ background:#7a5af8; }
        .btn-ghost{ background:#22304a; text-decoration:none; display:inline-flex; align-items:center; gap:8px; }
      `}</style>
    </div>
  )
}

function NewModal({ open, onClose, onSubmit }) {
  const [form, setForm] = useState({
    externalKey: '', projectId: 1, title: '', createdAt: new Date().toISOString().slice(0,10),
    status: 'Open', priority:'Normal'
  })
  useEffect(()=>{ if(!open){ setForm(f=>({...f, externalKey:'', title:''}))}},[open])
  if(!open) return null
  return (
    <div style={{position:'fixed', inset:0, background:'rgba(0,0,0,.5)', display:'grid', placeItems:'center', zIndex:50}}>
      <div style={{background:'#131b31', color:'#e9eef8', padding:20, borderRadius:16, width:500, boxShadow:'0 10px 40px rgba(0,0,0,.5)'}}>
        <h3 style={{marginTop:0}}>Create RFI</h3>
        <div className="grid">
          <label>External Key <input value={form.externalKey} onChange={e=>setForm({...form, externalKey:e.target.value})}/></label>
          <label>Project ID <input type="number" value={form.projectId} onChange={e=>setForm({...form, projectId:Number(e.target.value)})}/></label>
          <label>Title <input value={form.title} onChange={e=>setForm({...form, title:e.target.value})}/></label>
          <label>Created At <input type="date" value={form.createdAt} onChange={e=>setForm({...form, createdAt:e.target.value})}/></label>
          <label>Status
            <select value={form.status} onChange={e=>setForm({...form, status:e.target.value})}>
              <option>Open</option><option>Pending</option><option>Closed</option>
            </select>
          </label>
          <label>Priority
            <select value={form.priority} onChange={e=>setForm({...form, priority:e.target.value})}>
              <option>Low</option><option>Normal</option><option>High</option><option>Critical</option>
            </select>
          </label>
        </div>
        <div style={{display:'flex', gap:10, justifyContent:'flex-end', marginTop:12}}>
          <button className="btn" onClick={()=>onSubmit(form)}>Create</button>
          <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
        </div>
        <style>{`
          .grid{ display:grid; grid-template-columns:1fr 1fr; gap:12px }
          label{ display:flex; flex-direction:column; gap:6px; font-size:14px }
          input, select{ padding:10px; border-radius:10px; border:1px solid #2b3756; background:#0b1020; color:#e9eef8 }
          .btn { background:#2d6ef7; border:0; color:white; padding:10px 14px; border-radius:12px; cursor:pointer; }
          .btn-ghost{ background:#22304a; color:#fff; }
        `}</style>
      </div>
    </div>
  )
}

export default function App(){
  const [rfis, setRfis] = useState([])
  const [loading, setLoading] = useState(false)
  const [filter, setFilter] = useState('')
  const [showNew, setShowNew] = useState(false)

  async function load(){
    setLoading(true)
    const res = await fetch(`${API}/api/rfis`)
    const data = await res.json()
    setRfis(data)
    setLoading(false)
  }
  useEffect(()=>{ load() },[])

  async function createRfi(form){
    const res = await fetch(`${API}/api/rfis`, {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(form)
    })
    if(res.ok){ setShowNew(false); load() }
    else alert('Create failed')
  }

  async function updateStatus(id, status){
    const res = await fetch(`${API}/api/rfis/${id}`, {
      method:'PUT',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ status })
    })
    if(res.ok){ load() } else alert('Update failed')
  }

  const filtered = useMemo(()=>{
    const q = filter.trim().toLowerCase()
    if(!q) return rfis
    return rfis.filter(r =>
      (r.externalKey||'').toLowerCase().includes(q) ||
      (r.title||'').toLowerCase().includes(q) ||
      (r.projectCode||'').toLowerCase().includes(q) ||
      (r.status||'').toLowerCase().includes(q)
    )
  },[rfis, filter])

  return (
    <div style={{maxWidth:1100, margin:'40px auto', padding:'0 16px'}}>
      <h1 style={{margin:'0 0 10px', letterSpacing:.3}}>RFI Console</h1>
      <p style={{marginTop:0, opacity:.8}}>Quick dashboard to list, create, and update RFIs.</p>

      <Toolbar onRefresh={load} onCreate={()=>setShowNew(true)} />

      <div style={{display:'flex', gap:12, marginBottom:12}}>
        <input
          placeholder="Search external key / title / project / status"
          value={filter}
          onChange={e=>setFilter(e.target.value)}
          style={{flex:1, padding:10, borderRadius:12, border:'1px solid #22304a', background:'#0b1020', color:'#e9eef8'}}
        />
        <Badge text={`${filtered.length} RFIs`} />
      </div>

      <div style={{overflow:auto, border:'1px solid #22304a', borderRadius:12}}>
        <table style={{width:'100%', borderCollapse:'collapse', minWidth:900}}>
          <thead>
            <tr style={{background:'#131b31', textAlign:'left'}}>
              {['ID','External Key','Title','Project','Status','Priority','Created','Due','Assignee','Actions'].map(h=>(
                <th key={h} style={{padding:12, fontWeight:600, borderBottom:'1px solid #22304a'}}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="10" style={{padding:18}}>Loading…</td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan="10" style={{padding:18, opacity:.7}}>No RFIs.</td></tr>
            ) : filtered.map(r=>(
              <tr key={r.id} style={{borderTop:'1px solid #22304a'}}>
                <td style={{padding:10}}>{r.id}</td>
                <td style={{padding:10}}>{r.externalKey}</td>
                <td style={{padding:10}}>{r.title}</td>
                <td style={{padding:10}}>{r.projectCode}</td>
                <td style={{padding:10}}>
                  <select
                    value={r.status}
                    onChange={(e)=>updateStatus(r.id, e.target.value)}
                    style={{padding:6, borderRadius:8, border:'1px solid #2b3756', background:'#0b1020', color:'#e9eef8'}}
                  >
                    <option>Open</option>
                    <option>Pending</option>
                    <option>Closed</option>
                  </select>
                </td>
                <td style={{padding:10}}>
                  <Badge text={r.priority||'Normal'} kind={{
                    'Low':'ok','Normal':'neutral','High':'warn','Critical':'danger'
                  }[r.priority||'Normal']}/>
                </td>
                <td style={{padding:10}}>{r.createdAt}</td>
                <td style={{padding:10}}>{r.dueDate || '—'}</td>
                <td style={{padding:10}}>{r.assignee || '—'}</td>
                <td style={{padding:10}}>
                  <a href="#" onClick={(e)=>{e.preventDefault(); alert(JSON.stringify(r, null, 2))}} style={{color:'#9ecbff'}}>View JSON</a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <NewModal open={showNew} onClose={()=>setShowNew(false)} onSubmit={createRfi} />
    </div>
  )
}
