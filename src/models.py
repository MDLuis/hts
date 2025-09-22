from pydantic import BaseModel
from typing import List, Optional

class Chapter(BaseModel):
    """
    Represents a single HTS chapter.

    Attributes:
        ch_number (int): The numeric identifier for the chapter.
        title (str): The title or heading of the chapter.
        notes (Optional[str]): Any special notes attached to the chapter.
    """
    ch_number: int
    title: str
    notes: Optional[str] = None


class Section(BaseModel):
    """
    Represents a single HTS section which can contain multiple chapters.

    Attributes:
        sec_number (int): The numeric identifier for the section.
        title (str): The title or heading of the section.
        chapters (List[Chapter]): A list of chapters belonging to this section.
    """
    sec_number: int
    title: str
    chapters: List[Chapter]
