"""Idempotent synthetic data for local development only."""

import os
from datetime import datetime, timezone

from pwdlib import PasswordHash
from sqlalchemy import select

from .db import SessionLocal
from .models import Activity, CommunityGroup, Content, Event, User


def dt(value: str):
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def seed():
    if os.getenv("APP_ENV") == "production":
        raise SystemExit("Synthetic seed data cannot be loaded in production")
    password = os.getenv("DEMO_PASSWORD")
    if not password or len(password) < 12:
        raise SystemExit("Set DEMO_PASSWORD to at least 12 characters before seeding")
    hasher = PasswordHash.recommended()
    with SessionLocal() as db:
        users = {}
        for name, role in [("SunlitKoi", "member"), ("BrightKite", "member"), ("HSSModerator", "moderator")]:
            user = db.scalar(select(User).where(User.username == name))
            if not user:
                user = User(username=name, role=role, password_hash=hasher.hash(password))
                db.add(user)
                db.flush()
            else:
                user.password_hash = hasher.hash(password)
            users[name] = user
        if not db.scalar(select(Content.id).limit(1)):
            for title, body, fmt, topic, stage, author, verified in [
                ("Travelling with haemophilia: a preparation checklist", "A synthetic example resource about organising questions and travel documents before a family trip. This demo contains no clinical instructions.", "Guide", "Travel", "Primary school", "HSSModerator", True),
                ("Talking to teachers about haemophilia", "A synthetic conversation starter for sharing only the information school staff need while respecting a child's privacy.", "Resource", "School and childcare", "Primary school", "HSSModerator", True),
                ("What helped us during our first family trip", "We kept one list of questions and one list of things to pack. This is one family's example experience.", "Story", "Travel", "Infants and toddlers", "BrightKite", False),
                ("Starting primary school: what should we prepare?", "Our family is getting ready for a new school year. What conversations helped your family prepare with the school?", "Question", "School and childcare", "Primary school", "BrightKite", False),
                ("What I wish I knew after diagnosis", "I found it helpful to write down questions and ask trusted people for everyday support. This is only my experience.", "Story", "Caregiver wellbeing", "Newly diagnosed", "BrightKite", False),
            ]:
                db.add(Content(title=title, body=body, format=fmt, topic=topic, stage=stage, author_id=users[author].id, verified=verified))
        if not db.scalar(select(Event.id).limit(1)):
            for title, description, kind, when, mode, host in [
                ("Preparing for Primary 1", "Synthetic example webinar for caregivers preparing for a school transition.", "Webinar", "2026-10-26T10:00:00", "Online", "HSS Resource Team"),
                ("Community sharing session", "Synthetic example peer conversation for caregivers.", "Community sharing", "2026-11-12T12:00:00", "Online", "Community facilitators"),
                ("Planning family travel", "Synthetic example discussion about organising questions for a trip.", "Discussion", "2026-12-06T19:30:00", "Online", "HSS Resource Team"),
            ]:
                db.add(Event(title=title, description=description, kind=kind, starts_at=dt(when), mode=mode, host=host))
        if not db.scalar(select(Activity.id).limit(1)):
            db.add(Activity(title="Weekend walk and kopi", description="A synthetic casual morning walk for caregivers to meet and chat.", kind="Open jio", starts_at=dt("2026-11-10T09:00:00"), location="Near Bedok MRT", organiser_id=users["BrightKite"].id))
        if not db.scalar(select(CommunityGroup.id).limit(1)):
            for name, description, audience in [
                ("HSS Caregivers Community", "General peer connection and community updates.", "Adult caregivers"),
                ("Primary School Families", "School routines, activities and caregiver experiences.", "Primary school caregivers"),
            ]:
                db.add(CommunityGroup(name=name, description=description, audience=audience))
        db.commit()


if __name__ == "__main__":
    seed()
