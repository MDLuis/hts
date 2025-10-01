## Global Issues (Fixed except the quotes)
- **Line breaks & escape characters**  
  - Text often includes `\n` when the PDF has a newline.  
  - Text includes `\\` when the PDF has quotes (`"`) in between.  
  - **Impact:** Breaks clean text flow; may cause false mismatches during validation.  

- **Page heading bleed-through**  
  - Headings from the next page sometimes appear at the end or middle of a note.  
  - **Impact:** Corrupts note content; may cause incorrect splits.  

---

## Section Notes (Fixed)
- Only the **first note** is saved if multiple notes exist.  
- **Impact:** Missing content, lowers completeness score significantly.  

---

## General Notes (Fixed)
- Sometimes the number and “General Notes” are concatenated into the title.  

---

## Additional Notes (Still needs work)
- Footnote text sometimes gets parsed as part of the note.  
- **Impact:** Creates validation errors.  
