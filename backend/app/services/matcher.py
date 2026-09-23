import re
import threading
from functools import lru_cache
from typing import Iterable

# Common skills plus aliases. This is intentionally editable for your domain.
SKILL_ALIASES = {
    "python": ["python"],
    "java": ["java"],
    "c++": ["c++", "cpp"],
    "c": ["c"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "html": ["html"],
    "css": ["css"],
    "react": ["react", "reactjs", "react.js"],
    "angular": ["angular"],
    "node.js": ["node.js", "nodejs", "node"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "sql": ["sql"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo db"],
    "git": ["git", "github"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud"],
    "machine learning": ["machine learning", "machine-learning","ml"],
    "deep learning": ["deep learning","dl"],
    "nlp": ["nlp", "natural language processing"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "power bi": ["power bi"],
    "tableau": ["tableau"],
    "excel": ["excel", "microsoft excel"],
    "spring boot": ["spring boot"],
    "rest api": ["rest api", "restful api"],
}

# Reverse lookup so "js", "reactjs", "k8s"... are all normalised to one canonical name.
ALIAS_TO_CANON = {}
for _canon, _aliases in SKILL_ALIASES.items():
    ALIAS_TO_CANON[_canon] = _canon
    for _a in _aliases:
        ALIAS_TO_CANON[_a] = _canon

def split_skills(raw: str) -> list[str]:
    items = [x.strip().lower() for x in re.split(r"[,;\n|]+", raw or "") if x.strip()]
    return [ALIAS_TO_CANON.get(x, x) for x in items]

@lru_cache(maxsize=512)
def _skill_pattern(skill: str) -> re.Pattern:
    """Compile a safe regex for one skill. Every alias is escaped, so skills such as
    'c++', 'c#', '.net' or 'asp.net (mvc' can never break the regex or match wrongly."""
    aliases = SKILL_ALIASES.get(skill, [skill])
    alts = "|".join(re.escape(a).replace(r"\ ", r"\s+") for a in aliases)
    # Not glued to other word chars, and not part of node.js / c++ / c# style tokens.
    return re.compile(r"(?<![\w.+#])(?:" + alts + r")(?![\w+#])", re.I)

def detect_skills(text: str, extra_skills: Iterable[str] = ()) -> set[str]:
    candidates = set(SKILL_ALIASES.keys()) | {x.lower() for x in extra_skills}
    return {skill for skill in candidates if _skill_pattern(skill).search(text or "")}

def experience_years(text: str) -> float:
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|year|yrs|yr)\b", (text or "").lower())
    # Ignore absurd values such as "100 years of history".
    return max((float(x) for x in matches if float(x) <= 50), default=0.0)

# The embedding model is expensive to load. Load it once and remember a failure,
# instead of retrying (and waiting on the network) for every job role.
_model = None
_model_failed = False
_model_lock = threading.Lock()

def _get_model():
    global _model, _model_failed
    if _model is not None or _model_failed:
        return _model
    with _model_lock:
        if _model is None and not _model_failed:
            try:
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception:
                _model_failed = True
    return _model

@lru_cache(maxsize=128)
def _embed(text: str):
    return _get_model().encode(text, convert_to_tensor=True)

def semantic_similarity(resume_text: str, job_text: str) -> float:
    if _get_model() is not None:
        try:
            from sentence_transformers import util
            score = float(util.cos_sim(_embed(resume_text[:12000]), _embed(job_text[:12000])).item())
            return max(0.0, min(1.0, score))
        except Exception:
            pass
    # Deterministic fallback based on token overlap.
    a = set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}", resume_text.lower()))
    b = set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}", job_text.lower()))
    return len(a & b) / max(1, len(b))

def analyze(resume_text: str, job) -> dict:
    req = set(split_skills(job.required_skills))
    pref = set(split_skills(job.preferred_skills))
    all_job_skills = req | pref
    resume_skills = detect_skills(resume_text, all_job_skills)

    matched_req = req & resume_skills
    missing = req - resume_skills
    skill_score = (len(matched_req) / len(req)) if req else 0.0
    pref_score = (len(pref & resume_skills) / len(pref)) if pref else 0.0

    exp = experience_years(resume_text)
    exp_score = 1.0 if job.minimum_experience <= 0 else min(exp / job.minimum_experience, 1.0)

    job_text = f"{job.title}\n{job.description}\n{job.required_skills}\n{job.preferred_skills}\n{job.education}"
    sem = semantic_similarity(resume_text, job_text)

    # Explainable score: required skills dominate; semantic similarity adds context.
    # A role with no required skills must not lose the 60% skill weight; fall back to
    # preferred skills, then to semantic similarity.
    core = skill_score if req else (pref_score if pref else sem)
    final = 0.60 * core + 0.15 * pref_score + 0.10 * exp_score + 0.15 * sem
    final = round(final * 100, 2)

    reasons = []
    if matched_req:
        reasons.append(f"Matched {len(matched_req)} of {len(req)} required skills")
    if missing:
        reasons.append(f"{len(missing)} required skills are missing")
    if job.minimum_experience:
        reasons.append(f"Detected experience: {exp:g} years vs {job.minimum_experience:g} required")
    reasons.append(f"Semantic similarity: {sem * 100:.1f}%")

    return {
        "match_percentage": final,
        "semantic_score": round(sem * 100, 2),
        "skill_score": round(skill_score * 100, 2),
        "matched_skills": sorted(matched_req | (pref & resume_skills)),
        "missing_skills": sorted(missing),
        "explanation": ". ".join(reasons) + ".",
    }
