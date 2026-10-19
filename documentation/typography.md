# Typography

The reading page follows the typography of the dissertation and the 21 September defence slides. It distinguishes a text's function from its colour: metadata is not uniformly red, and red is not confined to Consolas.

| Function | Dissertation | Defence slides | Reading page |
| --- | --- | --- | --- |
| Argument and continuous prose | Garamond, normally 12 pt | Garamond, normally 25–27 pt for assertions | Garamond, 29 px initially; adjustable |
| Main title | Garamond; the synthesis and article openings commonly use bold | Garamond italic, 32.25 pt | Garamond italic |
| Work and article titles | Garamond italic; some article leaves use bold italic | Garamond italic | Garamond italic |
| Registration and metadata | Consolas, commonly 10.08 pt | Consolas | Consolas |
| Subtitle | Function varies with the part of the book | Consolas, 16.5 pt: red “Or”, black colon and continuation | The same division applies where this subtitle is reproduced |
| Formal numbers and labels | Red section, article and figure designators; often Garamond within headings | Red Consolas for RQ/article labels and defence progress; red Garamond within figure captions | Red formal labels; adjacent values and punctuation remain black |
| Figure caption | Garamond italic; the figure designator can be red | Garamond italic, normally 16.5–17.25 pt; centred under its object | Garamond italic; centred under the image |
| Source location | Black bibliographic text in the appropriate textual register | Consolas, 15 pt, dark grey `#555555` | Dark grey metadata and source locations |

The source files use both `#FF0000` and, locally, `#EE0000`. Body text is black or near-black. The formal prefix does not change the font of the whole heading: a red “Figure N.3” can remain Garamond before a black Garamond title. Likewise, black values remain Consolas after a red metadata key.

The paper background on the website is `#FFFFFF`. Slides are reproduced without reframing. Their typography and punctuation remain part of the source image.

The website requests installed Garamond and Consolas first. Locally bundled EB Garamond and DejaVu Sans Mono are fallback fonts when those faces are unavailable. The fallback is explicit; it is not a redistribution of the Microsoft fonts. Font licenses accompany the files in `assets/fonts/`.

Sources: `dissertation/Syntheticism-How-I-Learned-to-Love-Democracy.pdf`, especially the colophon, contents, synthesis openings, article leaves and figure captions; `defence/Syntheticism-Defence-21-September-2026.pptx`.
