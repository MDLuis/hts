from pydantic import BaseModel
from typing import List, Optional, Any

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
    """
    Represents a single General Note in the Harmonized Tariff Schedule (HTS).
    Attributes:
        note_number (Optional[str]): The General Note number, e.g. "1" or "2".
        title (str): Title or heading of the General Note.
        text (str): Full text of the General Note body.
    """
    note_number: Optional[str]
    title: str
    text: str

class Note(BaseModel):
    """
    Represents an individual numbered note within a section or chapter.
    Attributes:
        note_number (str): The note number, e.g. "1", "2".
        text (str): Text content of the note.
    """
    note_number: str
    text: str

class ChapterNote(BaseModel):
    """
    Represents all notes belonging to a single HTS chapter.
    Attributes:
        chapter_number (str): The chapter number, e.g. "3" or "98".
        notes (List[Note]): List of Note objects for this chapter.
    """
    chapter_number: str
    notes: List[Note]

class SectionNote(BaseModel):
    """
    Represents all notes belonging to a single HTS section.
    Attributes:
        section_number (str): The section number in Roman numerals, e.g. "I" or "XVI".
        notes (List[Note]): List of Note objects for this section.
    """
    section_number: str
    notes: List[Note]

class AdditionalUSNotes(BaseModel):
    chapter_number: str
    notes: list[Note]

class Footnote(BaseModel):
    columns: List[str]
    marker: Optional[str] = None
    value: str
    type: Optional[str]

class TariffRow(BaseModel):
    htsno: Optional[str]
    indent: Optional[str]
    description: str
    superior: Optional[str]
    units: Optional[List[str]]
    general: Optional[str]
    special: Optional[str]
    other: Optional[str]
    footnotes: Optional[List[Footnote]]
    quotaQuantity: Optional[str]
    additionalDuties: Optional[str]
    addiitionalDuties: Optional[Any]

class TariffTable(BaseModel):
    chapter_number: str
    rows: List[TariffRow]