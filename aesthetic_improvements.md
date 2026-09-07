# Website design implementation

Implemented a restrained off-white, navy, and teal visual system with consistent system typography, simpler navigation, a benefit-focused hero, concise product descriptions, smaller team portraits, and a dedicated contact section.

Roland: Founder, CEO | Senior Data Scientist; Economics background.
Dylan: AI Engineer; Computer Science background.

The Jinja template is the source of truth for styles and default content. The dependency-free Python renderer mirrors the markup; regression tests compare visible content and links between both paths. Missing template styles now fail explicitly instead of using stale CSS.

Optimized WebP assets are in output/assets; original files remain in docs. Both deployment scripts stage the generated homepage and these assets together. The standalone output/website-preview.html embeds its images and omits analytics for local review.

Validation: run python -m unittest discover -s tests -v. Browser checks cover 320, 390, 760, 900, and 1440px, loaded images, keyboard skip navigation, and team navigation. Preserve focus visibility and reduced-motion behavior when changing styles.

Future content improvements: add real product screenshots when available and expand team biographies with verified details.
