"""Haemily synthetic demo API. No clinical or identity-verification service is connected."""

import hashlib
import os
import secrets
import time
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from pwdlib import PasswordHash
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DBSession

from .db import get_db
from .models import Activity, ActivityJoin, Comment, CommunityGroup, Content, Event, HelpOffer, HelpRequest, Reaction, Registration, Report, Save, Session, User, now
from .schemas import ActivityIn, CommentIn, ContentIn, HelpRequestIn, LoginIn, ReportIn, ReportStatusIn

app = FastAPI(title="Haemily synthetic demo API", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")
password_hash = PasswordHash.recommended()
COOKIE_NAME = "haemily_session"
SESSION_HOURS = 12
_login_attempts: dict[str, list[float]] = {}


def fail(message: str, code: int = 404):
    raise HTTPException(status_code=code, detail=message)


def utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def current_session(request: Request, db: DBSession = Depends(get_db)) -> Session:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        fail("Sign in required", 401)
    session = db.scalar(select(Session).where(Session.token_hash == hashlib.sha256(token.encode()).hexdigest()))
    if not session:
        fail("Sign in required", 401)
    expires = utc(session.expires_at)
    if expires <= now():
        db.delete(session)
        db.commit()
        fail("Session expired", 401)
    return session


def current_user(session: Session = Depends(current_session)) -> User:
    return session.user


def write_session(request: Request, session: Session = Depends(current_session)) -> Session:
    if request.headers.get("X-CSRF-Token") != session.csrf_token:
        fail("Invalid CSRF token", 403)
    return session


def write_user(session: Session = Depends(write_session)) -> User:
    return session.user


def moderator(user: User = Depends(write_user)) -> User:
    if user.role != "moderator":
        fail("Moderator access required", 403)
    return user


def user_out(user: User):
    return {"id": user.id, "username": user.username, "role": user.role}


def content_out(db: DBSession, item: Content, user: User):
    return {
        "id": item.id, "title": item.title, "body": item.body, "format": item.format,
        "topic": item.topic, "stage": item.stage, "author": item.author.username,
        "author_id": item.author_id, "verified": item.verified, "created_at": item.created_at,
        "saved": db.get(Save, (user.id, item.id)) is not None,
        "reacted": db.get(Reaction, (user.id, item.id)) is not None,
        "reactions": db.scalar(select(func.count()).select_from(Reaction).where(Reaction.content_id == item.id)),
        "comments": db.scalar(select(func.count()).select_from(Comment).where(Comment.content_id == item.id, Comment.deleted_at.is_(None))),
    }


def event_out(db: DBSession, item: Event, user: User):
    return {"id": item.id, "title": item.title, "description": item.description, "kind": item.kind,
            "starts_at": item.starts_at, "mode": item.mode, "host": item.host,
            "registered": db.get(Registration, (user.id, item.id)) is not None}


def activity_out(db: DBSession, item: Activity, user: User):
    return {"id": item.id, "title": item.title, "description": item.description, "kind": item.kind,
            "starts_at": item.starts_at, "location": item.location, "organiser": item.organiser.username,
            "organiser_id": item.organiser_id,
            "joined": db.get(ActivityJoin, (user.id, item.id)) is not None}


def help_out(db: DBSession, item: HelpRequest, user: User):
    offers = db.scalars(select(HelpOffer).where(HelpOffer.request_id == item.id)).all() if item.requester_id == user.id else []
    my_offer = db.scalar(select(HelpOffer).where(HelpOffer.request_id == item.id, HelpOffer.volunteer_id == user.id))
    return {"id": item.id, "title": item.title, "description": item.description, "area": item.area,
            "status": item.status, "requester": item.requester.username, "mine": item.requester_id == user.id,
            "my_offer": my_offer.status if my_offer else None,
            "offers": [{"id": o.id, "volunteer": o.volunteer.username, "status": o.status} for o in offers]}


def existing(db: DBSession, model, item_id: int):
    item = db.get(model, item_id)
    if item is None or getattr(item, "deleted_at", None) is not None:
        fail("Item not found")
    return item


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/login")
def login(data: LoginIn, request: Request, response: Response, db: DBSession = Depends(get_db)):
    # A small local throttle protects the demo login. A deployed system needs a shared rate limiter.
    key = request.client.host if request.client else "unknown"
    recent = [t for t in _login_attempts.get(key, []) if t > time.monotonic() - 60]
    if len(recent) >= 10:
        fail("Too many login attempts; try again later", 429)
    user = db.scalar(select(User).where(User.username == data.username))
    if user is None or not password_hash.verify(data.password, user.password_hash):
        recent.append(time.monotonic())
        _login_attempts[key] = recent
        fail("Invalid demo credentials", 401)
    _login_attempts.pop(key, None)
    token = secrets.token_urlsafe(48)
    csrf = secrets.token_urlsafe(32)
    session = Session(token_hash=hashlib.sha256(token.encode()).hexdigest(), csrf_token=csrf, user_id=user.id, expires_at=now() + timedelta(hours=SESSION_HOURS))
    db.add(session)
    db.commit()
    response.set_cookie(COOKIE_NAME, token, httponly=True, secure=os.getenv("APP_ENV") == "production", samesite="lax", max_age=SESSION_HOURS * 3600, path="/")
    response.headers["Cache-Control"] = "no-store"
    return {"user": user_out(user), "csrf_token": csrf}


@app.get("/api/auth/session")
def get_session(response: Response, session: Session = Depends(current_session)):
    response.headers["Cache-Control"] = "no-store"
    return {"user": user_out(session.user), "csrf_token": session.csrf_token}


@app.post("/api/auth/logout", status_code=204)
def logout(response: Response, db: DBSession = Depends(get_db), session: Session = Depends(write_session)):
    db.delete(session)
    db.commit()
    response.delete_cookie(COOKIE_NAME, path="/")


@app.get("/api/content")
def list_content(db: DBSession = Depends(get_db), user: User = Depends(current_user)):
    items = db.scalars(select(Content).where(Content.deleted_at.is_(None)).order_by(Content.created_at.desc(), Content.id.desc())).all()
    return [content_out(db, x, user) for x in items]


@app.get("/api/content/{item_id}")
def get_content(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(current_user)):
    return content_out(db, existing(db, Content, item_id), user)


@app.post("/api/content", status_code=201)
def create_content(data: ContentIn, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    item = Content(**data.model_dump(), author_id=user.id, verified=False)
    db.add(item)
    db.commit()
    db.refresh(item)
    return content_out(db, item, user)


@app.delete("/api/content/{item_id}", status_code=204)
def delete_content(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    item = existing(db, Content, item_id)
    if user.id != item.author_id and user.role != "moderator":
        fail("Only the author or a moderator can remove this post", 403)
    item.deleted_at = now()
    db.commit()


@app.put("/api/content/{item_id}/save", status_code=204)
def save_content(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    existing(db, Content, item_id)
    if db.get(Save, (user.id, item_id)) is None:
        db.add(Save(user_id=user.id, content_id=item_id))
        db.commit()


@app.delete("/api/content/{item_id}/save", status_code=204)
def unsave_content(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    row = db.get(Save, (user.id, item_id))
    if row:
        db.delete(row)
        db.commit()


@app.put("/api/content/{item_id}/reaction", status_code=204)
def react_content(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    existing(db, Content, item_id)
    if db.get(Reaction, (user.id, item_id)) is None:
        db.add(Reaction(user_id=user.id, content_id=item_id))
        db.commit()


@app.delete("/api/content/{item_id}/reaction", status_code=204)
def unreact_content(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    row = db.get(Reaction, (user.id, item_id))
    if row:
        db.delete(row)
        db.commit()


@app.get("/api/content/{item_id}/comments")
def list_comments(item_id: int, db: DBSession = Depends(get_db), _user: User = Depends(current_user)):
    existing(db, Content, item_id)
    comments = db.scalars(select(Comment).where(Comment.content_id == item_id, Comment.deleted_at.is_(None)).order_by(Comment.created_at, Comment.id)).all()
    return [{"id": c.id, "body": c.body, "author": c.author.username, "author_id": c.author_id, "parent_id": c.parent_id, "created_at": c.created_at} for c in comments]


@app.post("/api/content/{item_id}/comments", status_code=201)
def add_comment(item_id: int, data: CommentIn, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    existing(db, Content, item_id)
    if data.parent_id:
        parent = existing(db, Comment, data.parent_id)
        if parent.content_id != item_id:
            fail("Reply must belong to this post", 422)
    comment = Comment(content_id=item_id, author_id=user.id, **data.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {"id": comment.id, "body": comment.body, "author": user.username, "author_id": user.id, "parent_id": comment.parent_id, "created_at": comment.created_at}


@app.delete("/api/comments/{item_id}", status_code=204)
def delete_comment(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    item = existing(db, Comment, item_id)
    if item.author_id != user.id and user.role != "moderator":
        fail("Only the author or a moderator can remove this comment", 403)
    item.deleted_at = now()
    db.commit()


@app.get("/api/me/comments")
def my_comments(db: DBSession = Depends(get_db), user: User = Depends(current_user)):
    rows = db.execute(select(Comment, Content.title).join(Content, Content.id == Comment.content_id).where(Comment.author_id == user.id, Comment.deleted_at.is_(None), Content.deleted_at.is_(None)).order_by(Comment.created_at.desc())).all()
    return [{"id": c.id, "body": c.body, "author": user.username, "author_id": user.id, "parent_id": c.parent_id, "created_at": c.created_at, "content_id": c.content_id, "content_title": title} for c, title in rows]


@app.get("/api/events")
def list_events(db: DBSession = Depends(get_db), user: User = Depends(current_user)):
    return [event_out(db, x, user) for x in db.scalars(select(Event).order_by(Event.starts_at)).all()]


@app.put("/api/events/{item_id}/registration", status_code=204)
def register(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    item = existing(db, Event, item_id)
    if utc(item.starts_at) < now():
        fail("This event has passed", 409)
    if db.get(Registration, (user.id, item_id)) is None:
        db.add(Registration(user_id=user.id, event_id=item_id))
        db.commit()


@app.delete("/api/events/{item_id}/registration", status_code=204)
def unregister(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    row = db.get(Registration, (user.id, item_id))
    if row:
        db.delete(row)
        db.commit()


@app.get("/api/activities")
def list_activities(db: DBSession = Depends(get_db), user: User = Depends(current_user)):
    return [activity_out(db, x, user) for x in db.scalars(select(Activity).where(Activity.deleted_at.is_(None)).order_by(Activity.starts_at)).all()]


@app.post("/api/activities", status_code=201)
def create_activity(data: ActivityIn, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    if data.starts_at <= now():
        fail("Choose a future date", 422)
    item = Activity(**data.model_dump(), organiser_id=user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return activity_out(db, item, user)


@app.delete("/api/activities/{item_id}", status_code=204)
def delete_activity(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    item = existing(db, Activity, item_id)
    if item.organiser_id != user.id and user.role != "moderator":
        fail("Only the organiser or a moderator can remove this activity", 403)
    item.deleted_at = now()
    db.commit()


@app.put("/api/activities/{item_id}/join", status_code=204)
def join_activity(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    item = existing(db, Activity, item_id)
    if utc(item.starts_at) < now():
        fail("This activity has passed", 409)
    if db.get(ActivityJoin, (user.id, item_id)) is None:
        db.add(ActivityJoin(user_id=user.id, activity_id=item_id))
        db.commit()


@app.delete("/api/activities/{item_id}/join", status_code=204)
def leave_activity(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    row = db.get(ActivityJoin, (user.id, item_id))
    if row:
        db.delete(row)
        db.commit()


@app.get("/api/groups")
def list_groups(db: DBSession = Depends(get_db), _user: User = Depends(current_user)):
    return [{"id": x.id, "name": x.name, "description": x.description, "audience": x.audience} for x in db.scalars(select(CommunityGroup).order_by(CommunityGroup.name)).all()]


@app.get("/api/help-requests")
def list_help(db: DBSession = Depends(get_db), user: User = Depends(current_user)):
    offered_ids = select(HelpOffer.request_id).where(HelpOffer.volunteer_id == user.id)
    rows = db.scalars(select(HelpRequest).where(HelpRequest.deleted_at.is_(None), (HelpRequest.status == "open") | (HelpRequest.requester_id == user.id) | (HelpRequest.id.in_(offered_ids))).order_by(HelpRequest.created_at.desc())).all()
    return [help_out(db, x, user) for x in rows]


@app.post("/api/help-requests", status_code=201)
def create_help(data: HelpRequestIn, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    item = HelpRequest(title=data.title, description=data.description, area=data.area, requester_id=user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return help_out(db, item, user)


@app.get("/api/help-requests/{item_id}")
def get_help(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(current_user)):
    item = existing(db, HelpRequest, item_id)
    if item.status != "open" and item.requester_id != user.id and user.role != "moderator" and not db.scalar(select(HelpOffer.id).where(HelpOffer.request_id == item_id, HelpOffer.volunteer_id == user.id)):
        fail("Request not available", 403)
    return help_out(db, item, user)


@app.post("/api/help-requests/{item_id}/cancel", status_code=204)
def cancel_help(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    item = existing(db, HelpRequest, item_id)
    if item.requester_id != user.id:
        fail("Only the requester can cancel", 403)
    if item.status != "open":
        fail("Only open requests can be cancelled", 409)
    item.status = "cancelled"
    db.commit()


@app.delete("/api/help-requests/{item_id}", status_code=204)
def delete_help(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    item = existing(db, HelpRequest, item_id)
    if item.requester_id != user.id and user.role != "moderator":
        fail("Only the requester or a moderator can remove this request", 403)
    item.deleted_at = now()
    db.commit()


@app.post("/api/help-requests/{item_id}/offers", status_code=201)
def offer_help(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    item = existing(db, HelpRequest, item_id)
    if item.requester_id == user.id:
        fail("You cannot offer on your own request", 409)
    if item.status != "open":
        fail("This request is no longer open", 409)
    offer = db.scalar(select(HelpOffer).where(HelpOffer.request_id == item_id, HelpOffer.volunteer_id == user.id))
    if offer:
        fail("You already offered help", 409)
    offer = HelpOffer(request_id=item_id, volunteer_id=user.id)
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return {"id": offer.id, "status": offer.status}


@app.delete("/api/help-requests/{item_id}/offers/mine", status_code=204)
def withdraw_offer(item_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    offer = db.scalar(select(HelpOffer).where(HelpOffer.request_id == item_id, HelpOffer.volunteer_id == user.id))
    if not offer:
        fail("Offer not found")
    if offer.status != "offered":
        fail("An accepted offer cannot be withdrawn here", 409)
    db.delete(offer)
    db.commit()


@app.post("/api/help-requests/{item_id}/offers/{offer_id}/accept", status_code=204)
def accept_offer(item_id: int, offer_id: int, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    item = existing(db, HelpRequest, item_id)
    offer = db.get(HelpOffer, offer_id)
    if item.requester_id != user.id:
        fail("Only the requester can accept", 403)
    if not offer or offer.request_id != item_id or item.status != "open" or offer.status != "offered":
        fail("Offer cannot be accepted", 409)
    offer.status = "accepted"
    for other in db.scalars(select(HelpOffer).where(HelpOffer.request_id == item_id, HelpOffer.id != offer_id, HelpOffer.status == "offered")):
        other.status = "declined"
    item.status = "connected"
    db.commit()


@app.post("/api/reports", status_code=201)
def create_report(data: ReportIn, db: DBSession = Depends(get_db), user: User = Depends(write_user)):
    target = {"content": Content, "activity": Activity, "help_request": HelpRequest}[data.target_type]
    existing(db, target, data.target_id)
    item = Report(**data.model_dump(), reporter_id=user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "status": item.status}


@app.get("/api/reports")
def list_reports(db: DBSession = Depends(get_db), user: User = Depends(current_user)):
    if user.role != "moderator":
        fail("Moderator access required", 403)
    return [{"id": x.id, "target_type": x.target_type, "target_id": x.target_id, "reason": x.reason, "details": x.details, "status": x.status, "created_at": x.created_at} for x in db.scalars(select(Report).order_by(Report.created_at.desc())).all()]


@app.patch("/api/reports/{item_id}")
def update_report(item_id: int, data: ReportStatusIn, db: DBSession = Depends(get_db), _user: User = Depends(moderator)):
    item = existing(db, Report, item_id)
    item.status = data.status
    db.commit()
    return {"id": item.id, "target_type": item.target_type, "target_id": item.target_id, "reason": item.reason, "details": item.details, "status": item.status, "created_at": item.created_at}
