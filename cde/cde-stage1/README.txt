Stage 1 - Data Fundamentals - Enabler Files
=============================================

Folder layout:

  requirements.txt        <- pinned package versions (used in Setup, Step 6)
  scripts/
    generate_dataset.py           <- creates the toy dataset (Setup, Step 8)
    exercise1_duckdb.py            <- Exercise 1
    exercise2_great_expectations.py <- Exercise 2
    fix_dirty_rows.py              <- used partway through Exercise 3
  data/
    (starts empty - generate_dataset.py fills this in)

Follow the DOCX tutorial step by step. Every command in this zip has
been tested end-to-end before being included -- if something doesn't
match what's described in the tutorial, check that you're running
commands from the exact folder the tutorial says to.
