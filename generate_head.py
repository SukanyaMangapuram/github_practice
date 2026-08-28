import os
import re

changelog_file = os.environ.get("CHANGELOG_FILE", "CHANGELOG.md")

with open(changelog_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

release_lines = []
found = False

for line in lines:
    if line.startswith("### Release "):
        if found:
            break
        found = True
        continue

    if found:
        release_lines.append(line.strip())

features = []
bugs = []
stories = []

pattern = re.compile(
    r'\*\*(feat|fix|story)\(\[([A-Z0-9-]+)\]\((https://devstack\.vwgroup\.com/jira/browse/[A-Z0-9-]+)\)\):\s*(.*?)\*\*',
    re.IGNORECASE
)

for line in release_lines:
    match = pattern.search(line)
    if not match:
        continue

    change_type = match.group(1).lower()
    jira_id = match.group(2)
    jira_url = match.group(3)
    desc = match.group(4)

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

    if change_type == "feat":
        features.append(row)
    elif change_type == "story":
        stories.append(row)
    else:
        bugs.append(row)

sections = ['      <h2 id="_HEAD">Release HEAD</h2>']

if features:
    sections.append(
        "      <h3>Feature</h3>\n"
        "      <table>\n" +
        "\n".join(features) +
        "\n      </table>"
    )

if bugs:
    sections.append(
        "      <h3>Bug</h3>\n"
        "      <table>\n" +
        "\n".join(bugs) +
        "\n      </table>"
    )

if stories:
    sections.append(
        "      <h3>Story</h3>\n"
        "      <table>\n" +
        "\n".join(stories) +
        "\n      </table>"
    )

head_section = "\n\n".join(sections) + "\n\n"

with open("release_head.html", "w", encoding="utf-8") as f:
    f.write(head_section)
