from pydantic import BaseModel
from typing import List, Optional, Literal

class Chapter(BaseModel):
    """
    Represents a single HTS chapter.

    Attributes:
        ch_number (str): The numeric identifier for the chapter.
        title (str): The title or heading of the chapter.
        notes (Optional[str]): Any special notes attached to the chapter.
    """
    ch_number: str
    title: str
    notes: Optional[str] = None


class Section(BaseModel):
    """
    Represents a single HTS section which can contain multiple chapters.

    Attributes:
        sec_number (str): The numeric identifier for the section.
        title (str): The title or heading of the section.
        chapters (List[Chapter]): A list of chapters belonging to this section.
    """
    sec_number: str
    title: str
    chapters: List[Chapter]

class GeneralNote(BaseModel):
    note_number: Optional[str]
    title: str
    text: str

class SectionNote(BaseModel):
    section_number: str
    text: str

class ChapterNote(BaseModel):
    chapter_number: str
    text: str
