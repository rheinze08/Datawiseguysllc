import importlib.util
import re
from html.parser import HTMLParser
import subprocess
import sys
import unittest
from pathlib import Path
from xml.etree.ElementTree import TreeBuilder


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "datawise_home.html.j2"
INDEX = ROOT / "index.html"


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_index", ROOT / "scripts" / "render_index.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Page(HTMLParser):
    """Parse the generated markup for assertions on visible text and links."""

    void_tags = set("area base br col embed hr img input link meta param source track wbr".split())

    def __init__(self, source):
        super().__init__()
        self.tree = TreeBuilder()
        self.hidden = False
        self.feed(source)
        self.close()
        self.root = self.tree.close()

    def handle_starttag(self, tag, attrs):
        self.tree.start(tag, dict(attrs))
        if tag in self.void_tags:
            self.tree.end(tag)
        if tag in ("style", "script"):
            self.hidden = True

    def handle_endtag(self, tag):
        if tag not in self.void_tags:
            self.tree.end(tag)
        if tag in ("style", "script"):
            self.hidden = False

    def handle_data(self, data):
        if not self.hidden:
            self.tree.data(data)


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
        primary = Page(Template(self.template).render()).root
        fallback = Page(self.renderer._render_without_jinja(self.template)).root
        self.assertEqual(" ".join(primary.itertext()).split(), " ".join(fallback.itertext()).split())
        self.assertEqual([a.get("href") for a in primary.iter("a")], [a.get("href") for a in fallback.iter("a")])

    def test_services_is_linked_and_reuses_published_destinations(self):
        from jinja2 import Template
        for engine, rendered in (
            ("jinja", Template(self.template).render()),
            ("fallback", self.renderer._render_without_jinja(self.template)),
        ):
            with self.subTest(engine=engine):
                page = Page(rendered).root
                self.assertIsNotNone(page.find('.//nav//a[@href="#services"]'))
                self.assertIsNotNone(page.find('.//div[@class="hero-actions"]//a[@href="#services"]'))
                sections = page.findall('.//main//section[@id="services"]')
                self.assertEqual(len(sections), 1)
                services = sections[0]
                copy = " ".join(services.itertext())
                for name in ("StashSage", "SocialSync", "Ledger Lite", "Insight Connect"):
                    self.assertIn(name, copy)

                contact = 'a[@href="mailto:datawiseguysllc@gmail.com"]'
                for area in (services, page.find(".//footer")):
                    labels = [" ".join(link.itertext()).strip() for link in area.findall(".//" + contact)]
                    self.assertEqual(labels.count("Get in Touch"), 1)

                socialsync = './/a[@href="https://www.socialsyncdwg.com"]'
                self.assertIsNotNone(services.find(socialsync))
                projects = page.find('.//section[@id="projects"]')
                self.assertIsNotNone(projects.find(socialsync))

    def test_creators_link_reaches_socialsync_card_without_a_product_url(self):
        from jinja2 import Template
        template = self.template.replace("'site_url': 'https://www.socialsyncdwg.com'", "'site_url': '#'")
        for rendered in (Template(template).render(), self.renderer._render_without_jinja(template)):
            page = Page(rendered).root
            self.assertIsNotNone(page.find('.//section[@id="services"]//a[@href="#socialsync"]'))
            card = page.find('.//section[@id="projects"]//article[@id="socialsync"]')
            self.assertIsNotNone(card)
            self.assertEqual(card.findtext(".//h4"), "SocialSync")

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
