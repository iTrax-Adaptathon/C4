const API_URL= "http://127.0.0.1:8000";
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const read=()=>JSON.parse(localStorage.getItem('forgeos-data')||'{"materials":[],"runs":[],"trips":[],"activity":[]}'); 
const save=d=>localStorage.setItem('forgeos-data',JSON.stringify(d)); let state=read(),kind='',selectedTrip=null,tripFilter='ALL';
const esc=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const status=s=>`<span class="status ${s.toLowerCase().replaceAll('_','-')}">${esc(s.replaceAll('_',' '))}</span>`;
function activity(text){state.activity.unshift({id:crypto.randomUUID(),text,time:new Date().toLocaleString()});state.activity=state.activity.slice(0,40);save(state)} 
function toast(t){$('#toast').textContent=t;$('#toast').classList.add('show');setTimeout(()=>$('#toast').classList.remove('show'),2800)}
async function loadBackendDashboard() {
    try {
        const response = await fetch(`${API_URL}/dashboard/`);

        if (!response.ok) {
            throw new Error("Dashboard API failed");
        }

        const data = await response.json();

        console.log("Backend Dashboard:", data);

        $('#stat-runs').textContent = data.running_runs;
        $('#stat-trips').textContent = data.machines;
        $('#stat-holds').textContent = data.active_alerts;
        $('#stat-today').textContent = data.materials;

    } catch (error) {
        console.error("Backend connection error:", error);
    }
}
async function loadBackendMaterials() {
    try {
        const response = await fetch(`${API_URL}/materials/`);

        if (!response.ok) {
            throw new Error("Materials API failed");
        }

        const materials = await response.json();

        console.log("Backend Materials:", materials);

        state.materials = materials.map(material => ({
            id: material.material_id,
            batch: material.batch_id,
            name: material.name,
            quantity: material.quantity,
            unit: "units",
            location: material.location,
            status: material.status
        }));

        $('#materials-table').innerHTML = state.materials.map(x => `
            <tr>
                <td><b>${esc(x.batch)}</b></td>
                <td>${esc(x.name)}</td>
                <td>${esc(x.quantity)} ${esc(x.unit)}</td>
                <td>${esc(x.location)}</td>
                <td>${status(x.status)}</td>
                <td>
                    <button class="row-action" data-material="${x.id}">
                        ${x.status === 'ON_HOLD'
                            ? 'Release hold'
                            : 'Place on hold'}
                    </button>
                </td>
            </tr>
        `).join('');

        $('#materials-empty').style.display =
            state.materials.length ? 'none' : 'flex';

        bindRows();

    } catch (error) {
        console.error("Materials connection error:", error);
    }
}
async function loadBackendMachines() {
    try {
        const response = await fetch(`${API_URL}/machines/`);

        if (!response.ok) {
            throw new Error("Machines API failed");
        }

        const machines = await response.json();

        console.log("Backend Machines:", machines);

        $('#machines-table').innerHTML = machines.map(machine => `
            <tr>
                <td><b>${esc(machine.machine_id)}</b></td>
                <td>${esc(machine.name)}</td>
                <td>${status(machine.status)}</td>
                <td>${esc(machine.current_run || '—')}</td>
            </tr>
        `).join('');

        $('#machines-empty').style.display =
            machines.length ? 'none' : 'flex';

    } catch (error) {
        console.error("Machines connection error:", error);
    }
}
async function loadBackendOperators() {
    try {
        const response = await fetch(`${API_URL}/operators/`);

        if (!response.ok) {
            throw new Error("Operators API failed");
        }

        const operators = await response.json();

        console.log("Backend Operators:", operators);

        $('#operators-table').innerHTML = operators.map(operator => `
            <tr>
                <td><b>${esc(operator.operator_id)}</b></td>
                <td>${esc(operator.name)}</td>
                <td>${status(operator.status)}</td>
                <td>${esc(operator.shift)}</td>
            </tr>
        `).join('');

        $('#operators-empty').style.display =
            operators.length ? 'none' : 'flex';

    } catch (error) {
        console.error("Operators connection error:", error);
    }
}
async function loadBackendProductionRuns() {
    try {
        const response = await fetch(`${API_URL}/production-runs/`);

        if (!response.ok) {
            throw new Error("Production Runs API failed");
        }

        const runs = await response.json();

        console.log("Backend Production Runs:", runs);

        state.runs = runs.map(run => ({
            id: run.run_id,
            order: run.work_order,
            product: run.product,
            quantity: run.quantity,
            due: run.due_date,
            status: run.status
        }));

        $('#runs-table').innerHTML = state.runs.map(x => `
            <tr>
                <td><b>${esc(x.order)}</b></td>
                <td>${esc(x.product)}</td>
                <td>${esc(x.quantity)} units</td>
                <td>${status(x.status)}</td>
                <td>${x.due || '—'}</td>
            <td>
    ${x.status === 'PLANNED'
        ? `<button class="row-action" data-run="${x.id}" data-next="ACTIVE">Start run</button>`
        : x.status === 'RUNNING'
        ? `<button class="row-action" data-run="${x.id}" data-next="COMPLETED">Complete</button>`
        : '—'
    }

    <button class="row-action" data-trace="${x.id}">
        View Trace
    </button>
</td>  
            </tr>
        `).join('');

        $('#runs-empty').style.display =
            state.runs.length ? 'none' : 'flex';

        bindRows();

    } catch (error) {
        console.error("Production Runs connection error:", error);
    }
}
async function loadBackendTraceability(runId) {
    try {
        const response = await fetch(
            `${API_URL}/traceability/${runId}`
        );

        if (!response.ok) {
            throw new Error("Traceability API failed");
        }

        const events = await response.json();

        console.log("Backend Traceability:", events);

        $('#traceability-table').innerHTML = events.map(event => `
            <tr>
                <td><b>${esc(event.run_id)}</b></td>
                <td>${esc(event.material_id)}</td>
                <td>${esc(event.batch_id)}</td>
                <td>${esc(event.machine_id)}</td>
                <td>${esc(event.operator_id)}</td>
                <td>${esc(event.event_type)}</td>
                <td>${esc(event.description)}</td>
                <td>${esc(event.timestamp)}</td>
            </tr>
        `).join('');

        $('#traceability-empty').style.display =
            events.length ? 'none' : 'flex';

    } catch (error) {
        console.error("Traceability connection error:", error);
    }
}
function empty(id,icon,title,text,label,k){return `<div class="empty" id="${id}"><span>${icon}</span><b>${title}</b><p>${text}</p><button class="small-primary" data-create="${k}">${label}</button></div>`}
function render(){loadBackendMaterials();loadBackendMachines();loadBackendOperators();loadBackendProductionRuns();let active=state.runs.filter(x=>x.status==='ACTIVE').length,transit=state.trips.filter(x=>x.status==='IN_TRANSIT').length,today=new Date().toISOString().slice(0,10);$('#stat-runs').textContent=active;$('#stat-trips').textContent=transit;$('#stat-holds').textContent=state.materials.filter(x=>x.status==='ON_HOLD').length;$('#stat-today').textContent=state.trips.filter(x=>x.eta===today).length;$('#trip-count').textContent=transit;$('#welcome').style.display=(state.materials.length||state.runs.length||state.trips.length)?'none':'flex';
$('#runs-table').innerHTML=state.runs.map(x=>`<tr><td><b>${esc(x.order)}</b></td><td>${esc(x.product)}</td><td>${esc(x.quantity)} units</td><td>${status(x.status)}</td><td>${x.due||'—'}</td><td>${x.status==='PLANNED'?`<button class="row-action" data-run="${x.id}" data-next="ACTIVE">Start run</button>`:x.status==='ACTIVE'?`<button class="row-action" data-run="${x.id}" data-next="COMPLETED">Complete</button>`:'—'}</td></tr>`).join('');$('#runs-empty').style.display=state.runs.length?'none':'flex';
$('#materials-table').innerHTML=state.materials.map(x=>`<tr><td><b>${esc(x.batch)}</b></td><td>${esc(x.name)}</td><td>${esc(x.quantity)} ${esc(x.unit)}</td><td>${esc(x.location)}</td><td>${status(x.status)}</td><td><button class="row-action" data-material="${x.id}">${x.status==='ON_HOLD'?'Release hold':'Place on hold'}</button></td></tr>`).join('');$('#materials-empty').style.display=state.materials.length?'none':'flex';
let r=state.runs.slice(0,3),t=state.trips.slice(0,3);$('#recent-runs').outerHTML=r.length?`<div class="mini-list" id="recent-runs">${r.map(x=>`<div><span class="mini-icon">◉</span><b>${esc(x.order)}<small>${esc(x.product)} · ${esc(x.quantity)} units</small></b>${status(x.status)}</div>`).join('')}</div>`:empty('recent-runs','◉','No production runs yet','Create a run and link it to your materials.','Create run','run');$('#recent-trips').outerHTML=t.length?`<div class="mini-list" id="recent-trips">${t.map(x=>`<div><span class="mini-icon">⌁</span><b>${esc(x.reference)}<small>${esc(x.origin)} → ${esc(x.destination)}</small></b>${status(x.status)}</div>`).join('')}</div>`:empty('recent-trips','⌁','No goods are being tracked','Create a trip to follow its status and location.','Add trip','trip');renderTrips();$('#activity-list').innerHTML=state.activity.map(x=>`<div class="activity"><i></i><div>${esc(x.text)}<small>${esc(x.time)}</small></div></div>`).join('');$('#activity-empty').style.display=state.activity.length?'none':'flex';bindRows()}
function renderTrips(){let items=state.trips.filter(x=>tripFilter==='ALL'||x.status===tripFilter);$('#trip-list').innerHTML=items.map(x=>`<button class="trip-item ${selectedTrip===x.id?'chosen':''}" data-trip="${x.id}"><span class="trip-symbol">⌁</span><span><b>${esc(x.reference)}</b><small>${esc(x.origin)} → ${esc(x.destination)}</small></span>${status(x.status)}</button>`).join('');$('#trips-empty').style.display=items.length?'none':'flex';let t=state.trips.find(x=>x.id===selectedTrip);$('#tracker').innerHTML=t?tracker(t):`<div class="tracker-empty"><span>⌁</span><h3>Select a trip</h3><p>Choose a trip to see its route, latest location, and controls.</p></div>`;$$('[data-trip]').forEach(b=>b.onclick=()=>{selectedTrip=b.dataset.trip;renderTrips()});$$('[data-update-trip]').forEach(b=>b.onclick=()=>openForm('trip',state.trips.find(x=>x.id===b.dataset.updateTrip)))}
function tracker(t){let stages=['CREATED','PICKED_UP','IN_TRANSIT','DELIVERED'],step=Math.max(0,stages.indexOf(t.status));return `<div class="tracker-top"><p class="eyebrow">CURRENTLY TRACKING</p><h2>${esc(t.reference)}</h2>${status(t.status)}</div><div class="route"><div><small>FROM</small><b>${esc(t.origin)}</b></div><div class="route-line"><i style="width:${step/3*100}%"></i><span>●</span></div><div><small>TO</small><b>${esc(t.destination)}</b></div></div><div class="location"><span>⌖</span><div><small>LATEST LOCATION</small><b>${esc(t.location||'Location not updated')}</b><p>Last update: ${esc(t.updatedAt||'Not yet updated')}</p></div></div><div class="trip-meta"><div><small>CARRIER / DRIVER</small><b>${esc(t.carrier||'Not specified')}</b></div><div><small>EXPECTED ARRIVAL</small><b>${t.eta||'Not specified'}</b></div></div><div class="timeline">${stages.map((s,i)=>`<div class="${i<=step?'done':''}"><i></i><span>${s.replaceAll('_',' ')}</span></div>`).join('')}</div>${t.status!=='DELIVERED'?`<button class="primary wide" data-update-trip="${t.id}">Update trip location or status</button>`:''}`}
function bindRows(){$$('[data-trace]').forEach(b => b.onclick = async () => {

    const runId = b.dataset.trace;

    document.querySelector('[data-page="traceability"]').click();

    await loadBackendTraceability(runId);
});$$('[data-run]').forEach(b=>b.onclick=()=>{let x=state.runs.find(x=>x.id===b.dataset.run);x.status=b.dataset.next;activity(`${x.order} changed to ${x.status}`);render();toast('Production run updated')});$$('[data-material]').forEach(b=>b.onclick=()=>{let x=state.materials.find(x=>x.id===b.dataset.material);x.status=x.status==='ON_HOLD'?'AVAILABLE':'ON_HOLD';activity(`${x.batch} ${x.status==='ON_HOLD'?'placed on quality hold':'released from hold'}`);render();toast('Material status updated')});$$('[data-create]').forEach(b=>b.onclick=()=>openForm(b.dataset.create));}
const fields={material:[['batch','Batch / lot number','text'],['name','Material name','text'],['quantity','Available quantity','number'],['unit','Unit (kg, units, rolls)','text'],['location','Storage location','text']],run:[['order','Work order number','text'],['product','Product name','text'],['quantity','Planned quantity','number'],['due','Due date','date'],['material','Material ID','text'],['machine','Machine ID','text'],['operator','Operator ID','text']],trip:[['reference','Trip reference','text'],['origin','Origin','text'],['destination','Destination','text'],['carrier','Carrier or driver','text'],['eta','Expected arrival','date'],['location','Current location','text']]};
function openForm(k,trip){kind=k;$('#form-kicker').textContent=trip?'LIVE UPDATE':`NEW ${k.toUpperCase()}`;$('#form-title').textContent=trip?`Update ${trip.reference}`:`Add ${k==='run'?'production run':k==='trip'?'goods trip':'material batch'}`;let list=trip?[['location','Current location','text'],['status','Status','select']]:fields[k];$('#form-fields').innerHTML=list.map(([n,l,t])=>`<label>${l}${t==='select'?`<select name="${n}"><option>CREATED</option><option>PICKED_UP</option><option>IN_TRANSIT</option><option>DELIVERED</option></select>`:`<input name="${n}" type="${t}" required value="${esc(trip?.[n]||'')}">`}</label>`).join('');if(trip){$('select[name=status]').value=trip.status}$('#modal').classList.add('visible');$('#data-form').dataset.trip=trip?.id||'';}
$('#data-form').onsubmit = async e => {
    e.preventDefault();

    let f = Object.fromEntries(new FormData(e.target));
    let id = e.target.dataset.trip;

    try {

        // UPDATE EXISTING TRIP
        if (id) {

            let x = state.trips.find(x => x.id === id);

            Object.assign(x, f, {
                updatedAt: new Date().toLocaleString()
            });

            activity(
                `${x.reference} updated: ${x.status.replaceAll('_', ' ')} at ${x.location}`
            );

            selectedTrip = x.id;

            toast('Trip tracking updated');
        }

        // CREATE MATERIAL
        else if (kind === 'material') {

            const response = await fetch(`${API_URL}/materials/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    material_id: f.batch,
                    name: f.name,
                    batch_id: f.batch,
                    quantity: Number(f.quantity),
                    location: f.location,
                    status: 'AVAILABLE'
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Material creation failed');
            }

            console.log('Backend Material Created:', data);

            toast('Material added successfully');
        }

        // CREATE LOCAL RUN OR TRIP FOR NOW
        else if (kind === 'run') {

    const response = await fetch(`${API_URL}/production-runs/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            run_id: f.order,
            work_order: f.order,
            product: f.product,
            quantity: Number(f.quantity),
            due_date: f.due,
            material_id: f.material,
            machine_id: f.machine,
            operator_id: f.operator
        })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'Production run creation failed');
    }

    console.log("Backend Production Run Created:", data);

    toast('Production run created successfully');

    await loadBackendProductionRuns();
}

else {

    let x = {
        ...f,
        id: crypto.randomUUID(),
        status: 'CREATED'
    };

    state.trips.unshift(x);

    activity(`${x.reference} created`);

    toast('Goods trip created');
}
        save(state);

        $('#modal').classList.remove('visible');

        e.target.reset();

        render();

    } catch (error) {

        console.error('Backend error:', error);

        toast(error.message);
    }
};
$$('.nav').forEach(b=>b.onclick=()=>{let p=b.dataset.page;$$('.nav').forEach(x=>x.classList.toggle('active',x===b));$$('.page').forEach(x=>x.classList.toggle('active',x.id===p));$('#page-title').textContent=b.querySelector('span').textContent;$('#page-kicker').textContent=p==='trips'?'LIVE GOODS TRACKING':'YOUR OPERATIONS'});$$('[data-go]').forEach(b=>b.onclick=()=>document.querySelector(`[data-page="${b.dataset.go}"]`).click());$('#open-trip').onclick=()=>openForm('trip');$('#open-run').onclick=()=>openForm('run');$('#close-modal').onclick=()=>$('#modal').classList.remove('visible');$('#modal').onclick=e=>{if(e.target===$('#modal'))$('#modal').classList.remove('visible')};$$('.filter').forEach(b=>b.onclick=()=>{tripFilter=b.dataset.filter;$$('.filter').forEach(x=>x.classList.toggle('selected',x===b));renderTrips()});$('#reset-data').onclick=()=>{if(confirm('Remove all your locally stored ForgeOS data?')){localStorage.removeItem('forgeos-data');state=read();selectedTrip=null;render();toast('Your data was reset')}};render();
loadBackendDashboard();
