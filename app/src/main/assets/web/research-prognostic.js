'use strict';

/*
 * TROJANS AeroFleetX experimental prognostic adapter.
 * Research-only integration for the frozen NASA C-MAPSS FD001 experiment.
 * This module does not run the trained model on-device and does not replace
 * the existing deterministic Predictive Intelligence demonstration logic.
 */
(function(){
  const CONFIG=Object.freeze({
    schema:'aerofleetx.experimental_prognostic.v1',
    modelId:'cmapss-fd001-rf-phase5-v1',
    modelLabel:'Random Forest · Phase 5 frozen model',
    dataset:'NASA C-MAPSS FD001',
    datasetSha256:'74bef434a34db25c7bf72e668ea4cd52afe5f2cf8e44367c55a82bfd91a5a34f',
    appBaselineCommit:'346d8db1a7e51cdd05ae5dc206e953ec6402fac2',
    modelParameters:Object.freeze({nEstimators:100,maxDepth:10,maxFeatures:0.7,minSamplesLeaf:5,randomState:2026}),
    statusLabel:'EXPERIMENTAL RESEARCH OUTPUT',
    topHeldOutFeatures:Object.freeze(['sensor_9','sensor_11','sensor_14','sensor_4','sensor_12']),
    limitations:Object.freeze([
      'Benchmark simulated engine-degradation data; not a real-aircraft fleet validation.',
      'Phase 5 FD001 evaluation showed optimistic RUL bias; 79 of 100 test engines were overestimated.',
      'The frozen model improved RMSE and MAE but did not improve the asymmetric NASA score.',
      'This output has no airworthiness, release-to-service or operational maintenance authority.'
    ])
  });

  const BENCHMARK_EXAMPLES=Object.freeze([
    Object.freeze({unitId:34,lastObservedCycle:203,estimatedRulCycles:6.499041,label:'Short-horizon example'}),
    Object.freeze({unitId:3,lastObservedCycle:126,estimatedRulCycles:57.592958,label:'Intermediate-horizon example'}),
    Object.freeze({unitId:1,lastObservedCycle:31,estimatedRulCycles:164.058711,label:'Long-horizon example'})
  ]);

  function finiteRul(value){
    const n=Number(value);
    return Number.isFinite(n)&&n>=0?n:null;
  }

  function mapRul(value){
    const rul=finiteRul(value);
    if(rul===null)return Object.freeze({priority:'Unavailable',reviewBand:'Unavailable'});
    if(rul<=10)return Object.freeze({priority:'High',reviewBand:'0–10'});
    if(rul<=25)return Object.freeze({priority:'High',reviewBand:'11–25'});
    if(rul<=60)return Object.freeze({priority:'Medium',reviewBand:'26–60'});
    if(rul<=100)return Object.freeze({priority:'Medium',reviewBand:'61–100'});
    return Object.freeze({priority:'Low',reviewBand:'>100'});
  }

  function escapeHtml(value){
    return String(value??'').replace(/[&<>'"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[m]));
  }

  function style(){
    if(document.getElementById('experimentalPrognosticStyle'))return;
    const el=document.createElement('style');
    el.id='experimentalPrognosticStyle';
    el.textContent=`
      .experimental-prognostic-card{margin:16px 0;padding:18px;border:1px solid rgba(83,175,255,.28);border-radius:18px;background:linear-gradient(145deg,rgba(14,42,64,.96),rgba(7,27,43,.98));box-shadow:0 14px 30px rgba(0,0,0,.18)}
      .experimental-prognostic-head{display:flex;gap:12px;justify-content:space-between;align-items:flex-start;margin-bottom:12px}
      .experimental-prognostic-head h2{margin:3px 0 4px;font-size:1.15rem}.experimental-prognostic-head p{margin:0;color:var(--muted,#9fb4c4);font-size:.9rem;line-height:1.4}
      .experimental-prognostic-badge{display:inline-flex;align-items:center;padding:6px 9px;border-radius:999px;border:1px solid rgba(255,196,92,.45);background:rgba(255,196,92,.12);color:#ffd27a;font-size:.68rem;font-weight:800;letter-spacing:.04em;text-align:center}
      .experimental-prognostic-selector{display:grid;gap:6px;margin:12px 0}.experimental-prognostic-selector span{font-size:.76rem;color:var(--muted,#9fb4c4);font-weight:700}.experimental-prognostic-selector select{width:100%;padding:11px;border-radius:12px;border:1px solid rgba(255,255,255,.14);background:#0b263a;color:#fff}
      .experimental-prognostic-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:12px 0}.experimental-prognostic-grid article{padding:12px;border-radius:14px;background:rgba(255,255,255,.055)}.experimental-prognostic-grid span{display:block;font-size:.7rem;color:var(--muted,#9fb4c4)}.experimental-prognostic-grid strong{display:block;margin-top:5px;font-size:1.05rem}.experimental-prognostic-priority.high{color:#ff9d9d}.experimental-prognostic-priority.medium{color:#ffd27a}.experimental-prognostic-priority.low{color:#8be0b4}.experimental-prognostic-priority.unavailable{color:#c6d2da}
      .experimental-prognostic-warning{margin:12px 0;padding:11px 12px;border-radius:12px;background:rgba(255,105,105,.09);border:1px solid rgba(255,105,105,.22);font-size:.82rem;line-height:1.45}.experimental-prognostic-features{font-size:.82rem;line-height:1.5;color:var(--muted,#a9bdcb)}
      .experimental-prognostic-card details{margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,.1)}.experimental-prognostic-card summary{cursor:pointer;font-weight:800;font-size:.82rem}.experimental-prognostic-card dl{display:grid;grid-template-columns:auto 1fr;gap:6px 10px;font-size:.74rem}.experimental-prognostic-card dt{color:var(--muted,#9fb4c4)}.experimental-prognostic-card dd{margin:0;word-break:break-word}.experimental-prognostic-limits{margin:8px 0 0;padding-left:18px;font-size:.75rem;line-height:1.45;color:var(--muted,#a9bdcb)}
      @media(max-width:560px){.experimental-prognostic-head{display:block}.experimental-prognostic-badge{margin-top:9px}.experimental-prognostic-grid{grid-template-columns:1fr}.experimental-prognostic-card dl{grid-template-columns:1fr}}
    `;
    document.head.appendChild(el);
  }

  function exampleOption(example){
    return `<option value="${example.unitId}">FD001 engine ${example.unitId} · ${escapeHtml(example.label)}</option>`;
  }

  function renderRecord(panel,example){
    const mapped=mapRul(example.estimatedRulCycles);
    const priorityClass=mapped.priority.toLowerCase();
    panel.querySelector('[data-exp-rul]').textContent=`${example.estimatedRulCycles.toFixed(1)} cycles`;
    panel.querySelector('[data-exp-priority]').textContent=mapped.priority.toUpperCase();
    panel.querySelector('[data-exp-priority]').className=`experimental-prognostic-priority ${priorityClass}`;
    panel.querySelector('[data-exp-band]').textContent=`${mapped.reviewBand} cycles`;
    panel.querySelector('[data-exp-sample]').textContent=`FD001 engine ${example.unitId} · last observed cycle ${example.lastObservedCycle}`;
  }

  function buildPanel(){
    const panel=document.createElement('section');
    panel.id='experimentalPrognosticPanel';
    panel.className='experimental-prognostic-card';
    panel.setAttribute('aria-label','Experimental research prognostic output');
    panel.innerHTML=`
      <div class="experimental-prognostic-head">
        <div><span class="eyebrow">RESEARCH PROGNOSTIC ADAPTER</span><h2>FD001 Remaining Useful Life experiment</h2><p>Separate from the simulated component-risk demo below. These are frozen benchmark examples, not live aircraft predictions.</p></div>
        <span class="experimental-prognostic-badge">${CONFIG.statusLabel}</span>
      </div>
      <label class="experimental-prognostic-selector"><span>Frozen Phase 5 benchmark example</span><select id="experimentalPrognosticExample">${BENCHMARK_EXAMPLES.map(exampleOption).join('')}</select></label>
      <div class="experimental-prognostic-grid">
        <article><span>Estimated RUL</span><strong data-exp-rul>--</strong></article>
        <article><span>Research priority</span><strong data-exp-priority>--</strong></article>
        <article><span>Review band</span><strong data-exp-band>--</strong></article>
      </div>
      <p class="experimental-prognostic-features"><b>Held-out explanation evidence:</b> strongest permutation-importance signals were ${CONFIG.topHeldOutFeatures.map(escapeHtml).join(', ')}. Generic C-MAPSS sensor labels are retained; no unsupported physical interpretation is assigned.</p>
      <div class="experimental-prognostic-warning"><b>Known limitation:</b> the frozen model showed optimistic RUL bias and did not improve the asymmetric NASA score. This panel cannot create a work order, schedule maintenance, calculate airworthiness, or authorize release to service.</div>
      <details><summary>Research provenance</summary><dl>
        <dt>Example</dt><dd data-exp-sample>--</dd>
        <dt>Model</dt><dd>${escapeHtml(CONFIG.modelId)}</dd>
        <dt>Dataset</dt><dd>${escapeHtml(CONFIG.dataset)}</dd>
        <dt>Dataset SHA-256</dt><dd>${escapeHtml(CONFIG.datasetSha256)}</dd>
        <dt>Baseline app commit</dt><dd>${escapeHtml(CONFIG.appBaselineCommit)}</dd>
      </dl><ul class="experimental-prognostic-limits">${CONFIG.limitations.map(x=>`<li>${escapeHtml(x)}</li>`).join('')}</ul></details>
    `;
    const select=panel.querySelector('#experimentalPrognosticExample');
    select.addEventListener('change',()=>{
      const example=BENCHMARK_EXAMPLES.find(x=>String(x.unitId)===select.value)||BENCHMARK_EXAMPLES[0];
      renderRecord(panel,example);
    });
    renderRecord(panel,BENCHMARK_EXAMPLES[0]);
    return panel;
  }

  function mount(){
    const screen=document.getElementById('predictive');
    if(!screen||document.getElementById('experimentalPrognosticPanel'))return;
    style();
    const notice=screen.querySelector('.predictive-notice');
    const panel=buildPanel();
    if(notice)notice.insertAdjacentElement('afterend',panel);else screen.prepend(panel);
  }

  window.AeroFleetXResearchPrognostic=Object.freeze({CONFIG,BENCHMARK_EXAMPLES,mapRul,mount});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});else mount();
})();
