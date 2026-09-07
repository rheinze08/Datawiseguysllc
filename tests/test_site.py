import importlib.util
import re
from html.parser import HTMLParser
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "datawise_home.html.j2"
INDEX = ROOT / "index.html"


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_index", ROOT / "scripts" / "render_index.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SiteRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = TEMPLATE.read_text(encoding="utf-8")
        cls.renderer = load_renderer()

    def test_template_has_current_product_and_team_data(self):
        self.assertIn("'name': 'Ledger Lite'", self.template)
        self.assertIn("https://www.ledgerlitedwg.com", self.template)
        self.assertIn("https://www.rolycode.com", self.template)
        self.assertIn("'status': 'Released'", self.template)
        self.assertIn("'name': 'Dylan Cael'", self.template)
        self.assertIn("'image_url': 'output/assets/dylan_cael_headshot_20260717.webp'", self.template)
        self.assertIn("'position': 'AI Engineer'", self.template)
        self.assertNotIn("Voice Ledger Lite", self.template)
        self.assertNotIn("github.com/rheinze08/RolyCode", self.template)

    def test_rendered_page_has_aligned_card_and_team_hooks(self):
        rendered = self.renderer._render_without_jinja(self.template)
        for hook in (
            'class="project-status"',
            'class="project-card-footer"',
            'class="team-grid"',
            'src="output/assets/dylan_cael_headshot_20260717.webp"',
            'href="#team">Meet the Team',
        ):
            self.assertIn(hook, rendered)
        self.assertNotIn("Founder Spotlight", rendered)
        self.assertNotIn("Founder-led", rendered)

    def test_generated_index_matches_template_defaults(self):
        subprocess.run([sys.executable, "scripts/render_index.py"], cwd=ROOT, check=True)
        rendered = INDEX.read_text(encoding="utf-8")
        for text in ("Ledger Lite", "www.ledgerlitedwg.com", "www.rolycode.com", "Dylan Cael"):
            self.assertIn(text, rendered)
        self.assertNotIn("Voice Ledger Lite", rendered)
        self.assertNotIn("View Repo", rendered)
        self.assertEqual(rendered.count('class="project-status">Released</span>'), 4)
        self.assertEqual(rendered.count('class="project-status project-status-developing"'), 2)
        self.assertEqual(rendered.count('class="team-card"'), 2)
        self.assertIn('src="output/assets/dylan_cael_headshot_20260717.webp"', rendered)
        self.assertIn('href="https://www.rolycode.com"', rendered)
        self.assertIn('href="https://x.com/rheinze08"', rendered)

    def test_redesign_content_and_accessibility_in_both_renderers(self):
        from jinja2 import Template
        for rendered in (Template(self.template).render(), self.renderer._render_without_jinja(self.template)):
            with self.subTest(renderer=rendered[:30]):
                self.assertIn('href="#main-content"', rendered)
                self.assertIn('id="main-content"', rendered)
                self.assertIn('Practical software for complex workflows.', rendered)
                self.assertIn('4 released', rendered)
                for text in ('Senior Data Scientist', 'Economics', 'AI Engineer', 'Computer Science'):
                    self.assertIn(text, rendered)
                self.assertIn('2 in development', rendered)
                self.assertNotIn('Bio coming soon.', rendered)
                self.assertEqual(len(re.findall(r'<h4>', rendered)), 6)
                self.assertEqual(rendered.count('https://x.com/rheinze08'), 1)
                self.assertIn('Have a question about our products?', rendered)
                for tag in re.findall(r'<img\b[^>]*>', rendered):
                    self.assertRegex(tag, r'width="\d+"')
                    self.assertRegex(tag, r'height="\d+"')
                    if 'hero-logo' not in tag:
                        self.assertIn('loading="lazy"', tag)

    def test_renderers_have_same_visible_content_and_links(self):
        from jinja2 import Template
        class Page(HTMLParser):
            def __init__(self, source):
                super().__init__()
                self.hidden = False
                self.words, self.links = [], []
                self.feed(source)
            def handle_starttag(self, tag, attrs):
                if tag in ('style', 'script'): self.hidden = True
                if tag == 'a': self.links.append(dict(attrs).get('href'))
            def handle_endtag(self, tag):
                if tag in ('style', 'script'): self.hidden = False
            def handle_data(self, data):
                if not self.hidden: self.words.extend(data.split())
        primary = Page(Template(self.template).render())
        fallback = Page(self.renderer._render_without_jinja(self.template))
        self.assertEqual(primary.words, fallback.words)
        self.assertEqual(primary.links, fallback.links)

    def test_local_images_exist_and_are_optimized(self):
        rendered = self.renderer._render_without_jinja(self.template)
        for source in re.findall(r'<img[^>]*src="([^"]+)"', rendered):
            asset = ROOT / source
            self.assertTrue(asset.is_file(), source)
            self.assertLess(asset.stat().st_size, 150_000, source)

    def test_deploy_includes_optimized_assets(self):
        for suffix in ('sh', 'bat'):
            script = (ROOT / 'scripts' / ('build_and_deploy_github_pages.' + suffix)).read_text()
            self.assertIn('add index.html output/assets', script)

    def test_template_and_fallback_share_styles(self):
        rendered = self.renderer._render_without_jinja(self.template)
        template_styles = self.template.split("<style>", 1)[1].split("</style>", 1)[0].strip()
        rendered_styles = rendered.split("<style>", 1)[1].split("</style>", 1)[0].strip()
        self.assertEqual(template_styles, rendered_styles)


if __name__ == "__main__":
    unittest.main()
