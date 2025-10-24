from pydantic import BaseModel
from typing import List, Optional, Any, Union

class Note(BaseModel):
    """
    Represents an individual numbered note within a section or chapter.
    Attributes:
        note_number (str): The note number, e.g. "1", "2".
        text (str): Text content of the note.
        sub_items (Optional[List[Union[str, dict]]]): Optional nested sub-items within the note.
    """
    note_number: str
    text: str
    sub_items:  Optional[List[Union[str, dict]]] = None

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
    """
    Represents "Additional U.S. Notes" that appear after the main notes of a chapter.

    Attributes:
        chapter_number (str): Chapter number to which these notes belong.
        notes (List[Note]): List of Note objects in this section.
    """
    chapter_number: str
    notes: list[Note]

class Footnote(BaseModel):
    """
    Represents a single footnote in tariff tables.

    Attributes:
        columns (List[str]): Columns in which the footnote applies.
        marker (Optional[str]): Symbol or identifier marking the footnote.
        value (str): The actual text of the footnote.
        type (Optional[str]): Optional categorization or type of footnote.
    """
    columns: List[str]
    marker: Optional[str] = None
    value: str
    type: Optional[str]

class TariffRow(BaseModel):
    """
    Represents a single row within a tariff table.

    Attributes:
        htsno (Optional[str]): The HTS number or subheading.
        indent (Optional[str]): Level of indentation in the tariff table.
        description (str): The description of goods or tariff line.
        superior (Optional[str]): Parent heading or category reference.
        units (Optional[List[str]]): Units of measure.
        general (Optional[str]): General rate of duty.
        special (Optional[str]): Special rate of duty (e.g., under trade agreements).
        other (Optional[str]): Other rate categories.
        footnotes (Optional[List[Footnote]]): Footnotes attached to this row.
        quotaQuantity (Optional[str]): Quota limits where applicable.
        additionalDuties (Optional[str]): Additional duties text.
        addiitionalDuties (Optional[Any]): Typo-preserving legacy field; use `additionalDuties` instead.
    """
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
    """
    Represents the entire tariff table for a specific chapter.

    Attributes:
        chapter_number (str): The chapter identifier.
        rows (List[TariffRow]): The rows making up the tariff data.
    """
    chapter_number: str
    rows: List[TariffRow]

class Chapter(BaseModel):
    """
    Represents a single HTS chapter.

    Attributes:
        ch_number (str): The numeric identifier for the chapter.
        title (str): The title or heading of the chapter.
        notes (Optional[ChapterNote]): Any special notes attached to the chapter.
        additional (Optional[AdditionalUSNotes]): Additional U.S. Notes associated with this chapter.
        table (Optional[TariffTable]): Tariff table data if available.
    """
    ch_number: str
    title: str
    notes: Optional[ChapterNote] = None
    additional: Optional[AdditionalUSNotes] = None
    table: Optional[TariffTable] = None

class Section(BaseModel):
    """
    Represents a single HTS section which can contain multiple chapters.

    Attributes:
        sec_number (str): The numeric identifier for the section.
        title (str): The title or heading of the section.
        notes (Optional[SectionNote]): Section-level notes, if any.
        chapters (List[Chapter]): A list of chapters belonging to this section.
    """
    sec_number: str
    title: str
    notes: Optional[SectionNote] = None
    chapters: List[Chapter] = None

class GeneralNote(BaseModel):
    """
    Represents a single General Note in the Harmonized Tariff Schedule (HTS).
    Attributes:
        note_number (Optional[str]): The General Note number, e.g. "1" or "2".
        title (str): Title or heading of the General Note.
        text (str): Full text of the General Note body.
        sub_items (Optional[List[Union[str, dict]]]): Nested sub-items or enumerations within the note.
    """
    note_number: Optional[str]
    title: str
    text: str
    sub_items:  Optional[List[Union[str, dict]]] = None

class HTSData(BaseModel):
    """
    Represents the overall structured HTS dataset including
    General Notes and all Sections.
    """
    general_notes: List[GeneralNote]
    sections: List[Section]

class Ruling(BaseModel):
    """
    Represents a single Customs Ruling document entry.

    Attributes:
        id (str): Unique identifier for the ruling.
        hts_code (str): The HTS code to which the ruling applies.
        prefix (str): Prefix indicating ruling type (e.g., HQ or NY).
        text (str): Extracted text of the ruling.
    """
    id: str
    hts_code: str
    prefix: str
    text: str

class GeneralRule(BaseModel):
    """
    Represents an individual General Rule of Interpretation (GRI).

    Attributes:
        rule_number (Optional[str]): Rule number, e.g., "1", "2".
        text (Optional[str]): Text of the rule or introductory text.
        sub_items (Optional[List[Union[str, dict]]]): Optional nested rule details or sub-clauses.
    """
    rule_number: Optional[str] = None
    text: Optional[str] = None
    sub_items:  Optional[List[Union[str, dict]]] = None