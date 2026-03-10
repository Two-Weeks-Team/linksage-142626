from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from models import SessionLocal, Bookmark, Summary, Tag, User
from ai_service import call_summarization, call_tagging

router = APIRouter(prefix="/api")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------------------
# Simple user handling – in a real app you would replace this with proper auth
# ---------------------------------------------------------------------
def get_current_user(db):
    user = db.query(User).first()
    if not user:
        user = User(username="demo", email="demo@example.com", password_hash="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

class SummarizeRequest(BaseModel):
    content: str = Field(..., description="Raw text/content to summarize")

class TagRequest(BaseModel):
    content: str = Field(..., description="Raw text/content to tag")

class SearchResponse(BaseModel):
    results: List[dict] = Field(default_factory=list)

@router.post("/summarize", response_model=dict)
async def summarize(req: SummarizeRequest, db: SessionLocal = Depends(get_db)):
    user = get_current_user(db)
    ai_result = await call_summarization(req.content)
    summary_text = (
        ai_result.get("summary")
        or ai_result.get("text")
        or ai_result.get("result")
        or ""
    )
    if not summary_text:
        summary_text = "No summary generated."
    # Store a placeholder bookmark (real implementation would store the actual URL)
    bookmark = Bookmark(user_id=user.id, url="N/A", title="Generated Summary")
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    # Store the summary linked to the bookmark
    summary = Summary(
        bookmark_id=bookmark.id,
        user_id=user.id,
        summary=summary_text,
        ai_model="openai-gpt-oss-120b",
        confidence_score=ai_result.get("confidence"),
    )
    db.add(summary)
    db.commit()
    return {"summary": summary_text, "ai": ai_result}

@router.post("/tag", response_model=dict)
async def tag(req: TagRequest, db: SessionLocal = Depends(get_db)):
    user = get_current_user(db)
    ai_result = await call_tagging(req.content)
    raw = ai_result.get("tags") or ai_result.get("result")
    if isinstance(raw, str):
        tags_list = [t.strip() for t in raw.split(",") if t.strip()]
    elif isinstance(raw, list):
        tags_list = raw
    else:
        tags_list = []
    created = []
    for tag_path in tags_list:
        parts = [p.strip() for p in tag_path.split(">") if p.strip()]
        parent = None
        for part in parts:
            q = db.query(Tag).filter_by(user_id=user.id, name=part, parent_tag_id=parent.id if parent else None)
            existing = q.first()
            if not existing:
                new_tag = Tag(user_id=user.id, name=part, parent_tag_id=parent.id if parent else None)
                db.add(new_tag)
                db.commit()
                db.refresh(new_tag)
                existing = new_tag
            parent = existing
        if parent:
            created.append(parent.name)
    return {"tags": created, "ai": ai_result}

@router.get("/search", response_model=SearchResponse)
async def search(q: str, db: SessionLocal = Depends(get_db)):
    # Stub implementation – actual semantic search would use vector embeddings
    return {"results": []}
