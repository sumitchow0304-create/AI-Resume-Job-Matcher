requireAuth();
// NOTE: `history` is the browser's built-in window.history, so the element is looked up
// explicitly. (Before, `history.innerHTML=...` silently did nothing and the page stayed blank.)
const listEl = document.getElementById("history");
(async()=>{
try{
 const resumes=await api("/resumes");
 if(!resumes.length){listEl.innerHTML='<p class="muted">No resumes have been uploaded yet.</p>';return}
 const analyses=await Promise.all(resumes.map(r=>api(`/analysis/resume/${r.id}`).catch(()=>[])));
 listEl.innerHTML=resumes.map((r,i)=>{
   const best=analyses[i][0];
   return `<div class="history-row"><div><b>${esc(r.original_filename)}</b><div class="muted">${new Date(r.uploaded_at).toLocaleString()}</div></div>
   <div>${best?`<b>${esc(best.job_title)}</b> · <strong>${best.match_percentage}%</strong>`:"Not analyzed"}</div>
   <a class="btn small" href="/static/upload.html?resume=${r.id}">View</a></div>`;
 }).join("");
}catch(e){listEl.innerHTML=`<p class="message">${esc(e.message)}</p>`}
})();
