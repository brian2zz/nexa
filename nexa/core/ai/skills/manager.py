import os
import re
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class SkillItem:
    name: str
    description: str
    content: str
    source_path: str
    scope: str  # "project" or "global"

class SkillManager:
    """
    Manages loading, parsing, and injecting autonomous agent skills
    from both project-local (./skills) and global (~/.gemini/config/skills) directories.
    """

    def __init__(self, cwd: str):
        self.cwd = cwd
        self.project_skills_dir = os.path.join(self.cwd, "skills")
        self.global_skills_dir = os.path.expanduser("~/.gemini/config/skills")
        self.builtin_skills_dir = os.path.expanduser("~/.gemini/antigravity-ide/builtin/skills")

    def _parse_skill_file(self, file_path: str, scope: str) -> Optional[SkillItem]:
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
        except Exception:
            return None

        # Check for YAML frontmatter between --- and ---
        name = os.path.basename(os.path.dirname(file_path))
        description = "No description provided."
        content = raw_text

        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw_text, re.DOTALL)
        if frontmatter_match:
            fm_text = frontmatter_match.group(1)
            content = frontmatter_match.group(2).strip()
            
            # Simple YAML parser for key-value
            for line in fm_text.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip().lower()
                    val = val.strip().strip("\"'")
                    if key == "name":
                        name = val
                    elif key == "description":
                        description = val

        return SkillItem(
            name=name,
            description=description,
            content=content,
            source_path=file_path,
            scope=scope
        )

    def load_all_skills(self) -> List[SkillItem]:
        """
        Discovers and parses all SKILL.md files from project, global, and builtin directories.
        Project skills take precedence over global skills with the same name.
        """
        skills: Dict[str, SkillItem] = {}

        # 1. Builtin skills
        if os.path.exists(self.builtin_skills_dir):
            for d in os.listdir(self.builtin_skills_dir):
                spath = os.path.join(self.builtin_skills_dir, d, "SKILL.md")
                skill = self._parse_skill_file(spath, "builtin")
                if skill:
                    skills[skill.name] = skill

        # 2. Global skills
        if os.path.exists(self.global_skills_dir):
            for d in os.listdir(self.global_skills_dir):
                spath = os.path.join(self.global_skills_dir, d, "SKILL.md")
                skill = self._parse_skill_file(spath, "global")
                if skill:
                    skills[skill.name] = skill

        # 3. Project skills (highest priority)
        if os.path.exists(self.project_skills_dir):
            for d in os.listdir(self.project_skills_dir):
                spath = os.path.join(self.project_skills_dir, d, "SKILL.md")
                skill = self._parse_skill_file(spath, "project")
                if skill:
                    skills[skill.name] = skill

        return list(skills.values())

    def format_skills_for_prompt(self, skills: Optional[List[SkillItem]] = None) -> str:
        """
        Formats loaded skills into a system instruction block for the agent LLM.
        """
        if skills is None:
            skills = self.load_all_skills()

        if not skills:
            return ""

        lines = [
            "\n## Available Autonomous Skills",
            "You have access to specialized skills and domain knowledge. Follow these instructions when applicable:\n"
        ]

        for s in skills:
            lines.append(f"### Skill: {s.name} ({s.scope})")
            lines.append(f"Description: {s.description}")
            lines.append("Instructions:")
            lines.append(s.content)
            lines.append("\n---")

        return "\n".join(lines)
