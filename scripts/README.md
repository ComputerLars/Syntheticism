# Book production

Install the Typst CLI (0.15 or newer) and the Python packages in requirements-pdf.txt. From the repository root, run:

    python scripts/build_book_pdf.py

The script reads the current archival texts and image records, prepares the local .book-build directory, and compiles scripts/book.typ. The published PDF keeps its established path. TYPST_BIN can specify the Typst executable.

Typography and page construction live in book.typ; the Python builder supplies structured content. Fonts in assets/fonts are available for portable builds. The defence edition uses the installed Microsoft Garamond and Consolas families when available in PowerPoint’s DFonts directory, with EB Garamond and DejaVu Sans Mono as fallbacks. Font files from Microsoft Office are not redistributed in this repository.

The lecture paragraph and slide placements are recorded in documentation/lecture-layout.json. To regenerate the reading text and page after an editorial change, run edit_transcript.py, then build_defence_page.py, then build_book_pdf.py. build_slide_posters.py refreshes the eight source-video stills in the slide access images; it requires FFmpeg and Poppler. The original PowerPoint and slide PDF remain the sources for those access copies.
