from sqlalchemy.orm import Session
from models import Note, Tag
from functools import wraps
from sqlalchemy.exc import OperationalError

def retry_on_operational_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OperationalError as e:
            print(f"Error: {e}")
            return None
    return wrapper

@retry_on_operational_error
def create_note(db: Session, title: str, content: str, tags: list[str]):
    db_note = Note(title=title, content=content)
    for tag_name in tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
        db_note.tags.append(tag)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@retry_on_operational_error
def get_notes(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Note).offset(skip).limit(limit).all()

@retry_on_operational_error
def get_note_by_id(db: Session, note_id: int):
    return db.query(Note).filter(Note.id == note_id).first()

@retry_on_operational_error
def search_notes_by_tag(db: Session, tag_name: str):
    return db.query(Note).join(Note.tags).filter(Tag.name == tag_name).all()