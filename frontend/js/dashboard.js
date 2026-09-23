requireAuth();
(async()=>{
try{
 const [me,jobs,resumes]=await Promise.all([api("/auth/me"),api("/jobs"),api("/resumes")]);
 welcome.textContent=`Welcome, ${me.name}. Your workspace is private to your account.`;
 jobsCount.textContent=jobs.length; resumeCount.textContent=resumes.length;
 recent.innerHTML=resumes.length
   ? `<table class="table">${resumes.slice(0,5).map(r=>`<tr><td><b>${esc(r.original_filename)}</b></td><td>${new Date(r.uploaded_at).toLocaleString()}</td><td><a class="btn small" href="/static/upload.html?resume=${r.id}">View</a></td></tr>`).join("")}</table>`
   : '<p class="muted">No resumes yet. Upload your first applicant resume.</p>';
 if(resumes.length){
   const all=await Promise.all(resumes.map(r=>api(`/analysis/resume/${r.id}`).catch(()=>[])));
   const scores=all.filter(a=>a[0]).map(a=>a[0].match_percentage);
   if(scores.length)topScore.textContent=Math.max(...scores).toFixed(1)+"%";
 }
}catch(e){console.error(e)}
})();
