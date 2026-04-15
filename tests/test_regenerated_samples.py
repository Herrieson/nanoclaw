from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class RegeneratedSamplesTest(unittest.TestCase):
    def test_docs_explain_user_surface_prompt_vs_implicit_constraints(self) -> None:
        batch_doc = (REPO_ROOT / "doc" / "task_batch.txt").read_text(encoding="utf-8")
        skills_doc = (REPO_ROOT / "doc" / "task.txt").read_text(encoding="utf-8")
        no_skills_doc = (REPO_ROOT / "doc" / "task_no_skills.txt").read_text(encoding="utf-8")

        self.assertIn("用户表层任务", batch_doc)
        self.assertIn("隐式约束", batch_doc)
        self.assertIn("真实用户", skills_doc)
        self.assertIn("不要把评测要求直接写成用户口吻", skills_doc)
        self.assertIn("不再依赖 `skillhub-skills-crawl.md`", skills_doc)
        self.assertIn("自主抽样产生灵感", skills_doc)
        self.assertIn("不需要从已有样本中取灵感", skills_doc)
        self.assertIn("不需要依赖仓库内已有样本", skills_doc)
        self.assertIn("真实用户", no_skills_doc)
        self.assertIn("不要把规则校验要求直接写成用户请求", no_skills_doc)


if __name__ == "__main__":
    unittest.main()
