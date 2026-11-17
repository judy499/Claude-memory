#!/usr/bin/env python3
"""Quick checks on Walmart copy. Usage: python3 copy_check.py "<title>" FILE_WITH_DESCRIPTION"""
import re
import sys

title = sys.argv[1]
desc = open(sys.argv[2], encoding="utf-8").read().strip()

words = re.findall(r"[A-Za-z0-9'%.-]+", desc)
sentences = [s for s in re.split(r"(?<=[.!?])\s+", desc) if s.strip()]
avg_sentence = len(words) / max(len(sentences), 1)
avg_word = sum(len(w) for w in words) / max(len(words), 1)

print(f"Title: {len(title)} chars {'OK' if 50 <= len(title) <= 90 else 'CHECK (aim 50-90)'}")
print(f"Description: {len(words)} words {'OK' if len(words) >= 60 else 'TOO SHORT (<60)'}")
print(f"Sentences: {len(sentences)}, avg {avg_sentence:.1f} words, avg word length {avg_word:.1f}")
for label, text in (("title", title), ("description", desc)):
    if "—" in text or "–" in text:
        print(f"Em/en dash found in {label}: remove it")
