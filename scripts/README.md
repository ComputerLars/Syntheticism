# Book production

Install the Typst CLI (0.15 or newer) and the Python packages in requirements-pdf.txt. From the repository root, run:

    python scripts/build_book_pdf.py

The script reads the current archival texts and image records, prepares the local .book-build directory, and compiles scripts/book.typ. The published PDF keeps its established path. TYPST_BIN can specify the Typst executable.

Typography and page construction live in book.typ; the Python builder supplies structured content. Fonts in assets/fonts are available for portable builds. The defence edition uses the installed Microsoft Garamond and Consolas families when available in PowerPoint’s DFonts directory, with EB Garamond and DejaVu Sans Mono as fallbacks. Font files from Microsoft Office are not redistributed in this repository.

The lecture’s spoken source paragraphs, cue map and slide placements are recorded in documentation/lecture-layout.json. edit_transcript.py reads the authorial script directly from the defence PowerPoint and retains the corrected recorded discussions. Run it before build_defence_page.py and build_book_pdf.py.

build_slide_posters.py renders all 54 whole-frame slide access images from the native PowerPoint PDF; it requires Poppler. Export that PDF in Microsoft PowerPoint using “Best for printing”, with Garamond and Consolas installed. Page 27 must show the completed anagram motion, not its initial MARCEL PROUST position. Run build_slide_posters.py --prepare-access to make a temporary access copy with only that slide’s positions advanced to their motion-path endpoints. Export this copy, without changing the source PowerPoint. The native PDF includes the original video posters. No text or captions are repainted over the slide images.
