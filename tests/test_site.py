import importlib.util
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
        self.assertIn("'image_url': 'docs/dylan_cael_headshot_20260717.jpg'", self.template)
        self.assertIn("'position': 'Key Contributor'", self.template)
        self.assertNotIn("Voice Ledger Lite", self.template)
        self.assertNotIn("github.com/rheinze08/RolyCode", self.template)

    def test_rendered_page_has_aligned_card_and_team_hooks(self):
        rendered = self.renderer._render_without_jinja(self.template)
        for hook in (
            'class="project-status"',
            'class="project-card-footer"',
            'class="team-grid"',
            'src="docs/dylan_cael_headshot_20260717.jpg"',
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
        self.assertIn('src="docs/dylan_cael_headshot_20260717.jpg"', rendered)
        self.assertIn('href="https://www.rolycode.com"', rendered)
        self.assertIn('href="https://x.com/rheinze08"', rendered)

    def test_template_and_fallback_share_styles(self):
        rendered = self.renderer._render_without_jinja(self.template)
        template_styles = self.template.split("<style>", 1)[1].split("</style>", 1)[0].strip()
        rendered_styles = rendered.split("<style>", 1)[1].split("</style>", 1)[0].strip()
        self.assertEqual(template_styles, rendered_styles)


if __name__ == "__main__":
    unittest.main()
