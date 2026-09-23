requireAuth();
resume.addEventListener("change",()=>fileName.textContent=resume.files[0]?.name||"PDF or DOCX");
uploadForm.addEventListener("submit",async e=>{
e.preventDefault();setMsg(msg,"Uploading and analyzing…");results.classList.add("hidden");
const btn=uploadForm.querySelector("button");btn.disabled=true;
try{
 if(!resume.files[0])throw Error("Please choose a PDF or DOCX file");
 const fd=new FormData();fd.append("file",resume.files[0]);
 const r=await fetch("/api/resumes/upload",{method:"POST",headers:authHeaders(),body:fd});
 if(r.status===401){logout();return}
 const uploaded=await r.json().catch(()=>({}));if(!r.ok)throw Error(errMsg(uploaded,"Upload failed"));
 const a=await api(`/analysis/resume/${uploaded.id}`,{method:"POST"});
 render(a,uploaded.original_filename);setMsg(msg,"Analysis completed.",true);
}catch(err){setMsg(msg,err.message)}
finally{btn.disabled=false}
});

// Opened from History / Dashboard via  upload.html?resume=<id>  -> show that resume's results.
const viewId=new URLSearchParams(location.search).get("resume");
if(viewId){(async()=>{
 try{
  setMsg(msg,"Loading analysis…");
  const list=await api("/resumes");
  const r=list.find(x=>String(x.id)===viewId);
  if(!r)throw Error("Resume not found");
  let rows=await api(`/analysis/resume/${r.id}`);
  if(!rows.length)rows=await api(`/analysis/resume/${r.id}`,{method:"POST"}); // never analyzed yet
  render(rows,r.original_filename);setMsg(msg,"");
 }catch(err){setMsg(msg,err.message)}
})()}

function render(rows,name){resultTitle.textContent=`Results — ${name}`;results.classList.remove("hidden");resultCards.innerHTML=rows.map((r,i)=>`
<div class="result"><div class="result-top"><div><h3>${i===0?"🥇 ":""}${esc(r.job_title)}</h3><p class="muted">${esc(r.explanation)}</p></div><div class="score">${r.match_percentage}%</div></div>
<div class="bar"><i style="width:${Math.min(100,Math.max(0,r.match_percentage))}%"></i></div>
<div class="result-grid"><div class="result-box"><strong>MATCHED SKILLS</strong>${r.matched_skills.map(x=>`<span class="tag">${esc(x)}</span>`).join(" ")||'<span class="muted">None detected</span>'}</div>
<div class="result-box"><strong>MISSING REQUIRED SKILLS</strong>${r.missing_skills.map(x=>`<span class="tag" style="background:#fff0f0;color:#ad4444">${esc(x)}</span>`).join(" ")||'<span class="muted">None 🎉</span>'}</div></div></div>`).join("")}
