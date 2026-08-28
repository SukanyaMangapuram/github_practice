import os
import re

changelog_file = os.environ.get("CHANGELOG_FILE", "CHANGELOG.md")

if not os.path.exists(changelog_file):
    print(f"Error: {changelog_file} not found.")
    exit(1)

with open(changelog_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

release_lines = []
found = False

for line in lines:
    if line.strip().startswith("### Release ") or line.strip().startswith("## Release "):
        if found:
            break
        found = True
        continue

    if found:
        release_lines.append(line.strip())

features, bugs, stories = [], [], []

jira_pattern = re.compile(
    r'\[([A-Z0-9]+-[0-9]+)\]\((https://[^\s\)]+)\)'
)

for line in release_lines:
    if not line:
        continue

    match = jira_pattern.search(line)
    if match:
        jira_id = match.group(1)
        jira_url = match.group(2)

        # Cleanup description text
        desc = line
        desc = re.sub(r'^\s*[\*\-]\s*', '', desc)  # remove leading bullets/hyphens
        desc = re.sub(r'\*\*(.*?)\*\*', r'\1', desc)  # remove bold Markdown tags
        desc = re.sub(r'\[([A-Z0-9]+-[0-9]+)\]\([^\s\)]+\):?', '', desc)  # remove raw Jira link
        desc = re.sub(r'^(feat|fix|story|bug)\s*\([^\)]*\)\s*:?\s*', '', desc, flags=re.IGNORECASE)  # strip fix(), feat(), etc.
        desc = re.sub(r'^\s*[\*\-]\s*', '', desc)  # clean up remaining hyphens/spaces
        desc = desc.strip()

        row = (
            f'        <tr>\n'
            f'          <td>\n'
            f'            <a href="{jira_url}">{jira_id}</a>\n'
            f'          </td>\n'
            f'          <td>\n'
            f'            <a href="{jira_url}">{desc}</a>\n'
            f'          </td>\n'
            f'        </tr>'
        )

        line_lower = line.lower()
        if "feat" in line_lower:
            features.append(row)
        elif "story" in line_lower:
            stories.append(row)
        else:
            bugs.append(row)

sections = []

if features:
    sections.append(
        "      <h3>Feature</h3>\n"
        "      <table class=\"black-table\">\n" +
        "\n".join(features) +
        "\n      </table>"
    )

if bugs:
    sections.append(
        "      <h3>Bug</h3>\n"
        "      <table class=\"black-table\">\n" +
        "\n".join(bugs) +
        "\n      </table>"
    )

if stories:
    sections.append(
        "      <h3>Story</h3>\n"
        "      <table class=\"black-table\">\n" +
        "\n".join(stories) +
        "\n      </table>"
    )

# Appends break tags at the end to create breathing room before the next release section
head_section = "\n\n".join(sections) + "\n<br><br>\n\n"

with open("release_head.html", "w", encoding="utf-8") as f:
    f.write(head_section)
