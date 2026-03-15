from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_FILE = ROOT_DIR / "templates" / "datawise_home.html.j2"
OUTPUT_FILE = ROOT_DIR / "index.html"


def _extract_default_scalar(template_text: str, variable: str, fallback: str) -> str:
    pattern = re.compile(r"\{\{\s*" + re.escape(variable) + r"\s*\|\s*default\('([^']*)'\)\s*\}\}")
    match = pattern.search(template_text)
    return match.group(1) if match else fallback


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


def _render_without_jinja(template_text: str) -> str:
    company_name = _extract_default_scalar(template_text, "company_name", "Data WiseGuys, LLC")
    company_tagline = _extract_default_scalar(
        template_text,
        "company_tagline",
        "Turning data into clear, actionable outcomes.",
    )
    social_links = _extract_default_list_or_dict(
        template_text,
        "social_links",
        {"x": "#", "facebook": "#", "instagram": "#", "tiktok": "#"},
    )
    projects = _extract_default_list_or_dict(template_text, "projects", [])
    team_members = _extract_default_list_or_dict(template_text, "team_members", [])

    project_html = []
    for project in projects:
        handles = project.get("social_handles", {})
        name = project.get("name", "Project")
        project_html.append(
            f'''          <article class="project-card">\n'''
            f'''            <img src="{project.get("logo_url", "#")}" alt="{project.get("logo_alt", "Project logo")}" width="160" height="160">\n'''
            f"            <h3>{name}</h3>\n"
            f"            <p>{project.get('description', '')}</p>\n"
            f'''            <p><a href="{project.get("site_url", "#")}" target="_blank" rel="noopener noreferrer">Visit {name}</a></p>\n'''
            f"            <p>\n"
            f"              Follow {name}:\n"
            f'''              <a href="{handles.get("x", "#")}" target="_blank" rel="noopener noreferrer">X</a>,\n'''
            f'''              <a href="{handles.get("facebook", "#")}" target="_blank" rel="noopener noreferrer">Facebook</a>,\n'''
            f'''              <a href="{handles.get("instagram", "#")}" target="_blank" rel="noopener noreferrer">Instagram</a>,\n'''
            f'''              <a href="{handles.get("tiktok", "#")}" target="_blank" rel="noopener noreferrer">TikTok</a>\n'''
            f"            </p>\n"
            f"          </article>"
        )

    team_html = []
    for member in team_members:
        team_html.append(
            f'''          <article class="team-card">\n'''
            f'''            <img src="{member.get("image_url", "#")}" alt="{member.get("image_alt", "Team member")}" width="180" height="180">\n'''
            f"            <h3>{member.get('name', 'Team Member')}</h3>\n"
            f"            <p><strong>{member.get('position', '')}</strong></p>\n"
            f"            <p>{member.get('description', '')}</p>\n"
            f"            <p>\n"
            f'''              <a href="{member.get("minnect_url", "#")}" target="_blank" rel="noopener noreferrer">Minnect Profile</a>\n'''
            f"              |\n"
            f'''              <a href="{member.get("linkedin_url", "#")}" target="_blank" rel="noopener noreferrer">LinkedIn Profile</a>\n'''
            f"            </p>\n"
            f"          </article>"
        )

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{company_name}</title>
</head>
<body>
  <header>
    <h1>{company_name}</h1>
    <p>{company_tagline}</p>

    <nav aria-label="Social media">
      <ul>
        <li><a href="{social_links.get('x', '#')}" target="_blank" rel="noopener noreferrer">X</a></li>
        <li><a href="{social_links.get('facebook', '#')}" target="_blank" rel="noopener noreferrer">Facebook</a></li>
        <li><a href="{social_links.get('instagram', '#')}" target="_blank" rel="noopener noreferrer">Instagram</a></li>
        <li><a href="{social_links.get('tiktok', '#')}" target="_blank" rel="noopener noreferrer">TikTok</a></li>
      </ul>
    </nav>
  </header>

  <main>
    <section id="projects" aria-labelledby="projects-title">
      <h2 id="projects-title">Projects</h2>
      <div class="project-grid">
{chr(10).join(project_html)}
      </div>
    </section>

    <section id="team" aria-labelledby="team-title">
      <h2 id="team-title">Meet the Team</h2>
      <div class="team-grid">
{chr(10).join(team_html)}
      </div>
    </section>
  </main>
</body>
</html>
'''


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
