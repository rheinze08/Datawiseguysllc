from __future__ import annotations

import ast
import re
from html import escape
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_FILE = ROOT_DIR / "templates" / "datawise_home.html.j2"
OUTPUT_FILE = ROOT_DIR / "index.html"

STYLES = """
    :root {
      color-scheme: light;
      --bg: #f3ede2;
      --bg-deep: #e4d9c8;
      --surface: rgba(255, 252, 247, 0.84);
      --surface-strong: #fffdf8;
      --ink: #16243b;
      --muted: #5d6c75;
      --brand: #0f766e;
      --brand-strong: #0c5b55;
      --accent: #d97745;
      --line: rgba(22, 36, 59, 0.12);
      --line-strong: rgba(22, 36, 59, 0.24);
      --shadow: 0 28px 60px rgba(27, 38, 59, 0.14);
      --shadow-soft: 0 20px 48px rgba(27, 38, 59, 0.09);
      --radius-xl: 32px;
      --radius-lg: 26px;
      --radius-md: 18px;
    }

    * {
      box-sizing: border-box;
    }

    html {
      scroll-behavior: smooth;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: Georgia, "Palatino Linotype", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(217, 119, 69, 0.18), transparent 26%),
        radial-gradient(circle at 85% 18%, rgba(15, 118, 110, 0.16), transparent 28%),
        linear-gradient(180deg, var(--bg) 0%, #f8f4ed 45%, var(--bg-deep) 100%);
    }

    a {
      color: inherit;
    }

    img {
      display: block;
      max-width: 100%;
    }

    .site-shell {
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px 20px 48px;
    }

    .site-hero,
    .section-shell,
    .site-footer {
      position: relative;
      overflow: hidden;
      border: 1px solid var(--line);
      background: var(--surface);
      backdrop-filter: blur(16px);
      box-shadow: var(--shadow);
    }

    .site-hero {
      border-radius: var(--radius-xl);
      padding: 24px;
    }

    .site-hero::before {
      content: "";
      position: absolute;
      top: -80px;
      left: -90px;
      width: 260px;
      height: 260px;
      border-radius: 999px;
      background: rgba(217, 119, 69, 0.12);
      filter: blur(18px);
    }

    .topbar,
    .section-heading,
    .site-footer {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 18px;
      position: relative;
      z-index: 1;
    }

    .brand-lockup {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .brand-kicker,
    .eyebrow,
    .panel-label,
    .stat-label {
      margin: 0;
      font-family: "Trebuchet MS", "Avenir Next", sans-serif;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      font-size: 0.74rem;
      color: var(--muted);
    }

    .brand-name {
      text-decoration: none;
      font-family: "Trebuchet MS", "Avenir Next", sans-serif;
      font-size: 1.15rem;
      font-weight: 700;
    }

    .topnav,
    .hero-actions,
    .social-row,
    .project-actions,
    .profile-links {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }

    .nav-pill,
    .hero-action,
    .project-action,
    .social-pill,
    .profile-link {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 11px 16px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.76);
      text-decoration: none;
      font-family: "Trebuchet MS", "Avenir Next", sans-serif;
      font-size: 0.95rem;
      font-weight: 700;
      transition:
        transform 140ms ease,
        border-color 140ms ease,
        box-shadow 140ms ease,
        background 140ms ease;
    }

    .nav-pill:hover,
    .hero-action:hover,
    .project-action:hover,
    .social-pill:hover,
    .profile-link:hover {
      transform: translateY(-1px);
      border-color: var(--line-strong);
      box-shadow: var(--shadow-soft);
    }

    .nav-pill-accent,
    .hero-action-primary,
    .project-action-primary {
      background: var(--brand);
      color: #fff;
      border-color: transparent;
    }

    .hero-grid {
      position: relative;
      z-index: 1;
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(300px, 0.8fr);
      gap: 30px;
      align-items: center;
      padding-top: 38px;
    }

    .hero-copy h1 {
      margin: 0;
      max-width: 10ch;
      font-family: "Trebuchet MS", "Avenir Next", sans-serif;
      font-size: clamp(2.7rem, 7vw, 5.5rem);
      line-height: 0.95;
    }

    .hero-text {
      margin: 20px 0 0;
      max-width: 38rem;
      color: var(--muted);
      font-size: 1.14rem;
      line-height: 1.8;
    }

    .hero-actions {
      margin-top: 24px;
    }

    .social-row {
      margin-top: 18px;
    }

    .hero-panel {
      justify-self: end;
      width: 100%;
      max-width: 360px;
      padding: 24px;
      border-radius: 28px;
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(244, 240, 233, 0.88));
      border: 1px solid rgba(22, 36, 59, 0.10);
      box-shadow: var(--shadow-soft);
    }

    .hero-logo-shell,
    .project-media,
    .team-photo-wrap {
      background: linear-gradient(135deg, rgba(15, 118, 110, 0.12), rgba(217, 119, 69, 0.16));
    }

    .hero-logo-shell {
      padding: 22px;
      border-radius: 24px;
    }

    .hero-logo {
      width: 100%;
      aspect-ratio: 1 / 1;
      object-fit: cover;
      border-radius: 18px;
      border: 1px solid rgba(22, 36, 59, 0.10);
    }

    .panel-email {
      display: inline-block;
      margin-top: 8px;
      text-decoration: none;
      font-family: "Trebuchet MS", "Avenir Next", sans-serif;
      font-size: 1.05rem;
      font-weight: 700;
    }

    .panel-meta {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      margin-top: 24px;
    }

    .panel-stat {
      padding: 14px;
      border-radius: 18px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.72);
    }

    .panel-stat strong {
      display: block;
      margin-top: 4px;
      font-family: "Trebuchet MS", "Avenir Next", sans-serif;
      font-size: 1.1rem;
    }

    .page-sections {
      display: grid;
      gap: 24px;
      margin-top: 28px;
    }

    .section-shell {
      padding: 28px;
      border-radius: 30px;
    }

    .section-heading {
      margin-bottom: 24px;
    }

    .section-heading h2 {
      margin: 6px 0 0;
      font-family: "Trebuchet MS", "Avenir Next", sans-serif;
      font-size: clamp(1.9rem, 4vw, 3.1rem);
    }

    .section-heading p {
      margin: 0;
      max-width: 34rem;
      color: var(--muted);
      line-height: 1.7;
    }

    .project-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 20px;
    }

    .project-card {
      display: flex;
      flex-direction: column;
      gap: 18px;
      min-height: 100%;
      padding: 22px;
      border-radius: var(--radius-lg);
      border: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(246, 241, 233, 0.82));
      box-shadow: var(--shadow-soft);
    }

    .project-media {
      padding: 18px;
      border-radius: 22px;
    }

    .project-logo {
      width: 100%;
      aspect-ratio: 1 / 1;
      object-fit: contain;
    }

    .project-card h3 {
      margin: 0;
      font-family: "Trebuchet MS", "Avenir Next", sans-serif;
      font-size: 1.4rem;
    }

    .project-description {
      margin: 0;
      color: var(--muted);
      line-height: 1.7;
    }

    .project-actions {
      margin-top: auto;
    }

    .social-pill {
      padding: 10px 14px;
    }

    .empty-note {
      margin: 0;
      color: var(--muted);
      font-style: italic;
    }

    .section-shell-team {
      background: linear-gradient(180deg, rgba(255, 252, 247, 0.92), rgba(240, 245, 242, 0.78));
    }

    .team-grid {
      display: grid;
      gap: 20px;
    }

    .team-card {
      display: grid;
      grid-template-columns: minmax(220px, 280px) minmax(0, 1fr);
      gap: 24px;
      align-items: center;
      padding: 24px;
      border-radius: 28px;
      border: 1px solid var(--line);
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(230, 240, 236, 0.80));
      box-shadow: var(--shadow-soft);
    }

    .team-photo-wrap {
      padding: 14px;
      border-radius: 24px;
    }

    .team-photo {
      width: 100%;
      aspect-ratio: 4 / 5;
      object-fit: cover;
      border-radius: 20px;
    }

    .team-copy h3 {
      margin: 8px 0 0;
      font-family: "Trebuchet MS", "Avenir Next", sans-serif;
      font-size: clamp(2rem, 4vw, 3rem);
    }

    .member-role {
      margin: 8px 0 0;
      color: var(--brand-strong);
      font-family: "Trebuchet MS", "Avenir Next", sans-serif;
      font-size: 1.1rem;
      font-weight: 700;
    }

    .member-description {
      margin: 16px 0 0;
      max-width: 42rem;
      color: var(--muted);
      line-height: 1.8;
    }

    .profile-links {
      margin-top: 22px;
    }

    .site-footer {
      margin-top: 24px;
      padding: 18px 24px;
      border-radius: 26px;
      background: rgba(255, 252, 247, 0.72);
    }

    .footer-note {
      margin: 0;
      color: var(--muted);
      line-height: 1.7;
    }

    .footer-note strong {
      color: var(--ink);
      font-family: "Trebuchet MS", "Avenir Next", sans-serif;
    }

    @media (max-width: 860px) {
      .topbar,
      .section-heading,
      .site-footer {
        flex-direction: column;
      }

      .hero-grid,
      .team-card {
        grid-template-columns: 1fr;
      }

      .hero-panel {
        justify-self: stretch;
        max-width: none;
      }
    }

    @media (max-width: 580px) {
      .site-shell {
        padding: 16px 14px 32px;
      }

      .site-hero,
      .section-shell,
      .site-footer {
        padding: 20px;
      }

      .project-card,
      .team-card {
        padding: 18px;
      }

      .hero-copy h1 {
        max-width: none;
      }

      .panel-meta {
        grid-template-columns: 1fr;
      }
    }
"""


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
        "Data WiseGuys builds operator-led software that turns messy workflows and domain data into practical automation, intelligence, and decision-support tools.",
    )
    company_email = _extract_default_scalar(
        template_text,
        "company_email",
        "datawiseguysllc@gmail.com",
    )
    company_logo_url = _extract_default_scalar(
        template_text,
        "company_logo_url",
        "docs/data_wiseguys_logo_20230401.jpg",
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

    project_html = []
    for project in projects:
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

        project_html.append(
            "          <article class=\"project-card\">\n"
            "            <div class=\"project-media\">\n"
            f"              <img class=\"project-logo\" src=\"{logo_url}\" alt=\"{logo_alt}\">\n"
            "            </div>\n"
            "            <div class=\"project-copy\">\n"
            f"              <h3>{name}</h3>\n"
            f"              <p class=\"project-description\">{description}</p>\n"
            "            </div>\n"
            f"{actions_html}"
            f"{social_html}"
            f"{empty_note}"
            "          </article>"
        )

    team_html = []
    for member in team_members:
        member_name = _safe_text(member.get("name"), "Team Member")
        image_url = _safe_text(member.get("image_url"), "#")
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

        team_html.append(
            "          <article class=\"team-card\">\n"
            "            <div class=\"team-photo-wrap\">\n"
            f"              <img class=\"team-photo\" src=\"{image_url}\" alt=\"{image_alt}\">\n"
            "            </div>\n"
            "            <div class=\"team-copy\">\n"
            "              <p class=\"eyebrow\">Founder-led</p>\n"
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
  <style>
{STYLES}
  </style>
</head>
<body>
  <div class="site-shell">
    <header class="site-hero" id="top">
      <div class="topbar">
        <div class="brand-lockup">
          <p class="brand-kicker">Operator-led software portfolio</p>
          <a class="brand-name" href="#top">{escaped_company_name}</a>
        </div>

        <nav class="topnav" aria-label="Primary">
          <a class="nav-pill" href="#projects">Projects</a>
          <a class="nav-pill" href="#team">Founder</a>
          <a class="nav-pill nav-pill-accent" href="mailto:{escaped_company_email}">Contact</a>
        </nav>
      </div>

      <div class="hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">Operator-led data ventures</p>
          <h1>{escaped_company_name}</h1>
          <p class="hero-text">{escaped_company_tagline}</p>

          <div class="hero-actions">
            <a class="hero-action hero-action-primary" href="#projects">Explore Projects</a>
            <a class="hero-action" href="mailto:{escaped_company_email}">{escaped_company_email}</a>
          </div>
{company_social_html}        </div>

        <aside class="hero-panel">
          <div class="hero-logo-shell">
            <img class="hero-logo" src="{escaped_company_logo_url}" alt="Data WiseGuys, LLC logo">
          </div>
          <p class="panel-label">Primary contact</p>
          <a class="panel-email" href="mailto:{escaped_company_email}">{escaped_company_email}</a>

          <div class="panel-meta">
            <div class="panel-stat">
              <span class="stat-label">Founder</span>
              <strong>Roland Heinze</strong>
            </div>
            <div class="panel-stat">
              <span class="stat-label">Projects</span>
              <strong>{project_count}</strong>
            </div>
          </div>
        </aside>
      </div>
    </header>

    <main class="page-sections">
      <section class="section-shell" id="projects" aria-labelledby="projects-title">
        <div class="section-heading">
          <div>
            <p class="eyebrow">Current builds</p>
            <h2 id="projects-title">Projects</h2>
          </div>
          <p>The portfolio spans social publishing automation, prospect research, AI-assisted analytics, mobile journaling, and real-time pricing tools.</p>
        </div>

        <div class="project-grid">
{chr(10).join(project_html)}
        </div>
      </section>

      <section class="section-shell section-shell-team" id="team" aria-labelledby="team-title">
        <div class="section-heading">
          <div>
            <p class="eyebrow">Leadership</p>
            <h2 id="team-title">Founder Spotlight</h2>
          </div>
          <p>The company is built around hands-on product execution, with each product shaped around a clear workflow or decision problem.</p>
        </div>

        <div class="team-grid">
{chr(10).join(team_html)}
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <p class="footer-note"><strong>{escaped_company_name}</strong> builds focused software that turns workflows, signals, and domain data into practical tools people can use immediately.</p>
      <a class="nav-pill nav-pill-accent" href="mailto:{escaped_company_email}">Get in Touch</a>
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
