from __future__ import annotations

import ast
import re
from html import escape
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_FILE = ROOT_DIR / "templates" / "datawise_home.html.j2"
OUTPUT_FILE = ROOT_DIR / "index.html"



def _extract_default_scalar(template_text: str, variable: str, fallback: str) -> str:
    patterns = [
        re.compile(r"\{\{\s*" + re.escape(variable) + r"\s*\|\s*default\('([^']*)'\)\s*\}\}"),
        re.compile(
            r"\{%\s*set\s+" + re.escape(variable) + r"\s*=\s*" + re.escape(variable) + r"\s*\|\s*default\('([^']*)'\)\s*%\}",
            re.DOTALL,
        ),
    ]

    for pattern in patterns:
        match = pattern.search(template_text)
        if match:
            return match.group(1)
    return fallback


def _extract_default_list_or_dict(template_text: str, variable: str, fallback):
    pattern = re.compile(
        r"\{%\s*set\s+" + re.escape(variable) + r"\s*=\s*" + re.escape(variable) + r"\s*\|\s*default\((.*?)\)\s*%\}",
        re.DOTALL,
    )
    match = pattern.search(template_text)
    if not match:
        return fallback

    value_text = match.group(1).strip()
    try:
        return ast.literal_eval(value_text)
    except Exception:
        return fallback


def _is_live_link(url: str | None) -> bool:
    return bool(url and url != "#")


def _safe_text(value: str | None, fallback: str = "") -> str:
    return escape(value or fallback)


def _extract_styles(template_text: str) -> str:
    match = re.search(r"<style>\s*(.*?)\s*</style>", template_text, re.DOTALL)
    if not match:
        raise ValueError("Homepage template must contain a style block")
    return match.group(1)


def _description_copy(value: str | None) -> str:
    if not value or "placeholder description" in value.lower():
        return "More details coming soon."
    return value


def _link_html(url: str, label: str, class_name: str) -> str:
    return (
        f'<a class="{class_name}" href="{escape(url)}" target="_blank" rel="noopener noreferrer">'
        f"{escape(label)}</a>"
    )


def _mailto_html(email: str, label: str, class_name: str) -> str:
    return (
        f'<a class="{class_name}" href="mailto:{escape(email)}">'
        f"{escape(label)}</a>"
    )


def _render_social_links(handles: dict[str, str] | None) -> list[str]:
    handles = handles or {}
    items = []
    for label, key in (
        ("X", "x"),
        ("Facebook", "facebook"),
        ("Instagram", "instagram"),
        ("TikTok", "tiktok"),
        ("Discord", "discord"),
    ):
        url = handles.get(key)
        if _is_live_link(url):
            items.append(_link_html(url, label, "social-pill"))
    return items


def _render_without_jinja(template_text: str) -> str:
    company_name = _extract_default_scalar(template_text, "company_name", "Data WiseGuys, LLC")
    company_tagline = _extract_default_scalar(
        template_text,
        "company_tagline",
        "We build tools that simplify everyday work, from social publishing and personal notes to coding workflows and data analysis.",
    )
    company_email = _extract_default_scalar(
        template_text,
        "company_email",
        "datawiseguysllc@gmail.com",
    )
    company_logo_url = _extract_default_scalar(
        template_text,
        "company_logo_url",
        "output/assets/data_wiseguys_logo_20230401.webp",
    )
    social_links = _extract_default_list_or_dict(
        template_text,
        "social_links",
        {"x": "#", "facebook": "#", "instagram": "#", "tiktok": "#"},
    )
    projects = _extract_default_list_or_dict(template_text, "projects", [])
    team_members = _extract_default_list_or_dict(template_text, "team_members", [])

    company_social_items = _render_social_links(social_links)
    company_social_html = ""
    if company_social_items:
        company_social_html = (
            '          <div class="social-row">\n'
            + "\n".join(f"            {item}" for item in company_social_items)
            + "\n          </div>\n"
        )

    def _render_project_card(project: dict) -> str:
        name = _safe_text(project.get("name"), "Project")
        description = _safe_text(_description_copy(project.get("description")))
        logo_url = _safe_text(project.get("logo_url"), "#")
        logo_alt = _safe_text(project.get("logo_alt"), "Project logo")
        site_url = project.get("site_url", "#")
        site_label = _safe_text(project.get("site_label"), "Visit Site")
        contact_email = project.get("contact_email", "")
        actions = []
        if _is_live_link(site_url):
            actions.append(_link_html(site_url, site_label, "project-action project-action-primary"))
        if contact_email:
            actions.append(_mailto_html(contact_email, "Email", "project-action"))
        actions_html = ""
        if actions:
            actions_html = (
                '            <div class="project-actions">\n'
                + "\n".join(f"              {item}" for item in actions)
                + "\n            </div>\n"
            )

        social_items = _render_social_links(project.get("social_handles"))
        social_html = ""
        if social_items:
            social_html = (
                '            <div class="social-row">\n'
                + "\n".join(f"              {item}" for item in social_items)
                + "\n            </div>\n"
            )

        empty_note = ""
        if not actions and not social_items:
            empty_note = '            <p class="empty-note">Launch details coming soon.</p>\n'

        status = _safe_text(project.get("status"), "Developing")
        status_class = "" if status == "Released" else " project-status-developing"
        return (
            "          <article class=\"project-card\">\n"
            "            <div class=\"project-media\">\n"
            f"              <img class=\"project-logo\" width=\"220\" height=\"112\" loading=\"lazy\" decoding=\"async\" src=\"{logo_url}\" alt=\"{logo_alt}\">\n"
            "            </div>\n"
            "            <div class=\"project-copy\">\n"
            f"              <span class=\"project-status{status_class}\">{status}</span>\n"
            f"              <h4>{name}</h4>\n"
            f"              <p class=\"project-description\">{description}</p>\n"
            "            </div>\n"
            "            <div class=\"project-card-footer\">\n"
            f"{actions_html}"
            f"{social_html}"
            f"{empty_note}"
            "            </div>\n"
            "          </article>"
        )

    released_project_html = []
    developing_project_html = []
    for project in projects:
        status = _safe_text(project.get("status"), "Developing")
        card_html = _render_project_card(project)
        if status == "Released":
            released_project_html.append(card_html)
        else:
            developing_project_html.append(card_html)

    team_html = []
    for member in team_members:
        member_name = _safe_text(member.get("name"), "Team Member")
        image_url = _safe_text(member.get("image_url"), "")
        image_alt = _safe_text(member.get("image_alt"), "Team member")
        position = _safe_text(member.get("position"))
        description = _safe_text(member.get("description"))
        links = []
        if member.get("linkedin_url"):
            links.append(_link_html(member.get("linkedin_url"), "LinkedIn", "profile-link"))
        if member.get("minnect_url"):
            links.append(_link_html(member.get("minnect_url"), "Minnect", "profile-link"))
        links_html = ""
        if links:
            links_html = (
                '              <div class="profile-links">\n'
                + "\n".join(f"                {item}" for item in links)
                + "\n              </div>\n"
            )

        photo_html = (
            f'              <img class="team-photo" width="112" height="140" loading="lazy" decoding="async" src="{image_url}" alt="{image_alt}">'
            if image_url
            else f'              <div class="team-photo-placeholder" role="img" aria-label="{image_alt}">DC</div>'
        )
        team_html.append(
            "          <article class=\"team-card\">\n"
            "            <div class=\"team-photo-wrap\">\n"
            f"{photo_html}\n"
            "            </div>\n"
            "            <div class=\"team-copy\">\n"
            f"              <h3>{member_name}</h3>\n"
            f"              <p class=\"member-role\">{position}</p>\n"
            f"              <p class=\"member-description\">{description}</p>\n"
            f"{links_html}"
            "            </div>\n"
            "          </article>"
        )

    escaped_company_name = escape(company_name)
    escaped_company_tagline = escape(company_tagline)
    escaped_company_email = escape(company_email)
    escaped_company_logo_url = escape(company_logo_url)
    project_count = len(projects)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_company_name}</title>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-72FM3KNC3X"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag() {{ dataLayer.push(arguments); }}
    gtag('js', new Date());

    gtag('config', 'G-72FM3KNC3X');
  </script>
  <style>
{_extract_styles(template_text)}
  </style>
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to content</a>
  <div class="site-shell">
    <header class="site-hero" id="top">
      <div class="topbar">
        <div class="brand-lockup">
          <p class="brand-kicker">Operator-led software portfolio</p>
          <a class="brand-name" href="#top">{escaped_company_name}</a>
        </div>

        <nav class="topnav" aria-label="Primary">
          <a class="nav-pill" href="#projects">Projects</a>
          <a class="nav-pill" href="#team">Team</a>
          <a class="nav-pill nav-pill-accent" href="mailto:{escaped_company_email}">Contact</a>
        </nav>
      </div>

      <div class="hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">Operator-led data ventures</p>
          <h1>Practical software for complex workflows.</h1>
          <p class="hero-text">{escaped_company_tagline}</p>

          <div class="hero-actions">
            <a class="hero-action hero-action-primary" href="#projects">Explore Projects</a>
            <a class="hero-action" href="#team">Meet the Team</a>
          </div>
{company_social_html}        </div>

        <aside class="hero-panel">
          <div class="hero-logo-shell">
            <img class="hero-logo" width="300" height="240" src="{escaped_company_logo_url}" alt="Data WiseGuys, LLC logo">
          </div>
          <p class="panel-label">Independent software studio</p>
          <p class="portfolio-summary"><strong>{len(released_project_html)} released</strong> &middot; {len(developing_project_html)} in development</p>
        </aside>
      </div>
    </header>

    <main class="page-sections" id="main-content" tabindex="-1">
      <section class="section-shell" id="projects" aria-labelledby="projects-title">
        <div class="section-heading">
          <div>
            <p class="eyebrow">Current builds</p>
            <h2 id="projects-title">Projects</h2>
          </div>
          <p>Released products and active builds shaped around practical workflows, signals, and decisions.</p>
        </div>

        <div class="project-group">
          <div class="project-group-heading">
            <h3>Released</h3>
          </div>
          <div class="project-grid">
{chr(10).join(released_project_html)}
          </div>
        </div>

        <div class="project-group">
          <div class="project-group-heading">
            <h3>Developing</h3>
          </div>
          <div class="project-grid">
{chr(10).join(developing_project_html)}
          </div>
        </div>
      </section>

      <section class="section-shell section-shell-team" id="team" aria-labelledby="team-title">
        <div class="section-heading">
          <div>
          <p class="eyebrow">Our people</p>
            <h2 id="team-title">Our Team</h2>
          </div>
          <p>The company is built around hands-on product execution, with each product shaped around a clear workflow or decision problem.</p>
        </div>

        <div class="team-grid">
{chr(10).join(team_html)}
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <div class="contact-row">
        <div><h2>Have a question about our products?</h2><a class="panel-email" href="mailto:{escaped_company_email}">{escaped_company_email}</a></div>
        <a class="nav-pill nav-pill-accent" href="mailto:{escaped_company_email}">Get in Touch</a>
      </div>
      <div class="footer-bottom">
        <p class="footer-note">{escaped_company_name} &middot; Independent software studio</p>
        <div class="social-row" aria-label="Founder social profiles">
          <a class="social-pill" href="https://x.com/rheinze08" target="_blank" rel="noopener noreferrer">X</a>
          <a class="social-pill" href="https://www.facebook.com/profile.php?id=61582292837909" target="_blank" rel="noopener noreferrer">Facebook</a>
          <a class="social-pill" href="https://www.instagram.com/heinze_roland/" target="_blank" rel="noopener noreferrer">Instagram</a>
          <a class="social-pill" href="https://discord.gg/k58TnRgFPb" target="_blank" rel="noopener noreferrer">Discord</a>
        </div>
      </div>
    </footer>
  </div>
</body>
</html>
"""


def main() -> None:
    template_text = TEMPLATE_FILE.read_text(encoding="utf-8")

    try:
        from jinja2 import Environment, FileSystemLoader

        env = Environment(loader=FileSystemLoader(str(TEMPLATE_FILE.parent)))
        template = env.get_template(TEMPLATE_FILE.name)
        rendered = template.render()
    except ModuleNotFoundError:
        rendered = _render_without_jinja(template_text)

    OUTPUT_FILE.write_text(rendered, encoding="utf-8")
    print(f"Rendered {TEMPLATE_FILE} -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
