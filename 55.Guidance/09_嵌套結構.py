#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Guidance 嵌套結構示例
====================================================

本模塊展示如何使用 Guidance 生成複雜的嵌套數據結構:
1. 基本嵌套對象
2. 多層嵌套 JSON
3. 嵌套數組結構
4. 混合嵌套類型
5. 遞歸數據結構
6. 樹形結構生成
7. 圖結構表示
8. 複雜文檔結構

嵌套結構是實際應用中常見的需求，Guidance 提供了
強大的約束機制來確保生成正確的嵌套結構。

作者: Guidance 示例團隊
日期: 2025-01-01
"""

import os
import sys
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

try:
    from guidance import models, gen, select
    import guidance
except ImportError:
    print("錯誤: 請先安裝 guidance 庫")
    sys.exit(1)


class NestedStructureDemo:
    """
    嵌套結構演示類

    展示如何生成各種複雜的嵌套數據結構。
    """

    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        """初始化嵌套結構演示器"""
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.generated_structures: List[Dict] = []

    def example_basic_nesting(self) -> None:
        """
        示例 1: 基本嵌套對象

        演示如何生成簡單的嵌套對象結構。
        """
        print(f"\n{'='*60}")
        print("示例 1: 基本嵌套對象")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        # 兩層嵌套
        print("生成兩層嵌套對象:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "user": {\n'
        lm += '    "name": "'
        lm += gen(name="user_name", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '    "age": '
        lm += gen(name="age", regex=r'\d{1,3}')
        lm += '\n'
        lm += '  },\n'
        lm += '  "email": "'
        lm += gen(name="email", regex=r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        lm += '"\n'
        lm += '}'

        data = {
            "user": {
                "name": lm["user_name"],
                "age": int(lm["age"])
            },
            "email": lm["email"]
        }

        print("生成的嵌套對象:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # 三層嵌套
        print("\n\n生成三層嵌套對象:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "company": {\n'
        lm += '    "name": "'
        lm += gen(name="company_name", max_tokens=15, stop='"')
        lm += '",\n'
        lm += '    "department": {\n'
        lm += '      "name": "'
        lm += gen(name="dept_name", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '      "head": {\n'
        lm += '        "name": "'
        lm += gen(name="head_name", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '        "title": "'
        lm += gen(name="title", max_tokens=15, stop='"')
        lm += '"\n'
        lm += '      }\n'
        lm += '    }\n'
        lm += '  }\n'
        lm += '}'

        company_data = {
            "company": {
                "name": lm["company_name"],
                "department": {
                    "name": lm["dept_name"],
                    "head": {
                        "name": lm["head_name"],
                        "title": lm["title"]
                    }
                }
            }
        }

        print("生成的三層嵌套:")
        print(json.dumps(company_data, indent=2, ensure_ascii=False))
        print()

    def example_nested_arrays(self) -> None:
        """
        示例 2: 嵌套數組

        演示如何生成包含數組的嵌套結構。
        """
        print(f"\n{'='*60}")
        print("示例 2: 嵌套數組")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        # 對象中的數組
        print("生成包含數組的對象:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "project": "'
        lm += gen(name="project_name", max_tokens=15, stop='"')
        lm += '",\n'
        lm += '  "tags": [\n'

        tags = []
        for i in range(3):
            lm += '    "'
            lm += gen(name=f"tag_{i}", max_tokens=10, stop='"')
            lm += '"'
            if i < 2:
                lm += ','
            lm += '\n'
            tags.append(lm[f"tag_{i}"])

        lm += '  ]\n'
        lm += '}'

        project_data = {
            "project": lm["project_name"],
            "tags": tags
        }

        print(json.dumps(project_data, indent=2, ensure_ascii=False))

        # 數組中的對象
        print("\n\n生成對象數組:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "employees": [\n'

        employees = []
        for i in range(2):
            lm += '    {\n'
            lm += '      "id": '
            lm += gen(name=f"emp_id_{i}", regex=r'\d+')
            lm += ',\n'
            lm += '      "name": "'
            lm += gen(name=f"emp_name_{i}", max_tokens=10, stop='"')
            lm += '",\n'
            lm += '      "department": "'
            lm += gen(name=f"dept_{i}", max_tokens=10, stop='"')
            lm += '"\n'
            lm += '    }'

            if i < 1:
                lm += ','
            lm += '\n'

            employees.append({
                "id": int(lm[f"emp_id_{i}"]),
                "name": lm[f"emp_name_{i}"],
                "department": lm[f"dept_{i}"]
            })

        lm += '  ]\n'
        lm += '}'

        employee_data = {"employees": employees}
        print(json.dumps(employee_data, indent=2, ensure_ascii=False))
        print()

    def example_deep_nesting(self) -> None:
        """
        示例 3: 深層嵌套

        演示如何生成多層深度的嵌套結構。
        """
        print(f"\n{'='*60}")
        print("示例 3: 深層嵌套 (5層)")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 構建 5 層嵌套
        lm += '{\n'
        lm += '  "level1": {\n'
        lm += '    "name": "'
        lm += gen(name="l1_name", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '    "level2": {\n'
        lm += '      "name": "'
        lm += gen(name="l2_name", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '      "level3": {\n'
        lm += '        "name": "'
        lm += gen(name="l3_name", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '        "level4": {\n'
        lm += '          "name": "'
        lm += gen(name="l4_name", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '          "level5": {\n'
        lm += '            "name": "'
        lm += gen(name="l5_name", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '            "value": '
        lm += gen(name="final_value", regex=r'\d+')
        lm += '\n'
        lm += '          }\n'
        lm += '        }\n'
        lm += '      }\n'
        lm += '    }\n'
        lm += '  }\n'
        lm += '}'

        deep_data = {
            "level1": {
                "name": lm["l1_name"],
                "level2": {
                    "name": lm["l2_name"],
                    "level3": {
                        "name": lm["l3_name"],
                        "level4": {
                            "name": lm["l4_name"],
                            "level5": {
                                "name": lm["l5_name"],
                                "value": int(lm["final_value"])
                            }
                        }
                    }
                }
            }
        }

        print("5層嵌套結構:")
        print(json.dumps(deep_data, indent=2, ensure_ascii=False))
        print()

    def example_mixed_nesting(self) -> None:
        """
        示例 4: 混合嵌套類型

        演示包含對象、數組、原始類型的混合嵌套。
        """
        print(f"\n{'='*60}")
        print("示例 4: 混合嵌套類型")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 複雜的混合結構
        lm += '{\n'
        lm += '  "blog": {\n'
        lm += '    "title": "'
        lm += gen(name="blog_title", max_tokens=20, stop='"')
        lm += '",\n'
        lm += '    "author": {\n'
        lm += '      "name": "'
        lm += gen(name="author_name", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '      "social": {\n'
        lm += '        "twitter": "'
        lm += gen(name="twitter", regex=r'@[a-zA-Z0-9_]+')
        lm += '",\n'
        lm += '        "followers": '
        lm += gen(name="followers", regex=r'\d+')
        lm += '\n'
        lm += '      }\n'
        lm += '    },\n'
        lm += '    "posts": [\n'

        posts = []
        for i in range(2):
            lm += '      {\n'
            lm += '        "id": '
            lm += gen(name=f"post_id_{i}", regex=r'\d+')
            lm += ',\n'
            lm += '        "title": "'
            lm += gen(name=f"post_title_{i}", max_tokens=20, stop='"')
            lm += '",\n'
            lm += '        "tags": ['

            post_tags = []
            for j in range(2):
                lm += '"'
                lm += gen(name=f"tag_{i}_{j}", max_tokens=8, stop='"')
                lm += '"'
                if j < 1:
                    lm += ', '
                post_tags.append(lm[f"tag_{i}_{j}"])

            lm += '],\n'
            lm += '        "published": '
            lm += select(["true", "false"], name=f"published_{i}")
            lm += '\n'
            lm += '      }'

            if i < 1:
                lm += ','
            lm += '\n'

            posts.append({
                "id": int(lm[f"post_id_{i}"]),
                "title": lm[f"post_title_{i}"],
                "tags": post_tags,
                "published": lm[f"published_{i}"] == "true"
            })

        lm += '    ]\n'
        lm += '  }\n'
        lm += '}'

        blog_data = {
            "blog": {
                "title": lm["blog_title"],
                "author": {
                    "name": lm["author_name"],
                    "social": {
                        "twitter": lm["twitter"],
                        "followers": int(lm["followers"])
                    }
                },
                "posts": posts
            }
        }

        print("混合嵌套結構:")
        print(json.dumps(blog_data, indent=2, ensure_ascii=False))
        print()

    def example_tree_structure(self) -> None:
        """
        示例 5: 樹形結構

        演示如何生成樹形數據結構。
        """
        print(f"\n{'='*60}")
        print("示例 5: 樹形結構")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        print("生成文件系統樹:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 根節點
        lm += '{\n'
        lm += '  "name": "'
        lm += gen(name="root_name", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '  "type": "directory",\n'
        lm += '  "children": [\n'

        children = []

        # 子節點
        for i in range(2):
            lm += '    {\n'
            lm += '      "name": "'
            lm += gen(name=f"child_name_{i}", max_tokens=10, stop='"')
            lm += '",\n'
            lm += '      "type": "'
            lm += select(["file", "directory"], name=f"child_type_{i}")
            lm += '"'

            child = {
                "name": lm[f"child_name_{i}"],
                "type": lm[f"child_type_{i}"]
            }

            # 如果是目錄，添加子文件
            if lm[f"child_type_{i}"] == "directory":
                lm += ',\n'
                lm += '      "children": [\n'
                lm += '        {\n'
                lm += '          "name": "'
                lm += gen(name=f"grandchild_{i}", max_tokens=10, stop='"')
                lm += '",\n'
                lm += '          "type": "file"\n'
                lm += '        }\n'
                lm += '      ]'

                child["children"] = [{
                    "name": lm[f"grandchild_{i}"],
                    "type": "file"
                }]

            lm += '\n'
            lm += '    }'

            if i < 1:
                lm += ','
            lm += '\n'

            children.append(child)

        lm += '  ]\n'
        lm += '}'

        tree_data = {
            "name": lm["root_name"],
            "type": "directory",
            "children": children
        }

        print(json.dumps(tree_data, indent=2, ensure_ascii=False))

        # 打印樹形視圖
        print("\n樹形視圖:")
        self._print_tree(tree_data, prefix="")
        print()

    def _print_tree(self, node: Dict, prefix: str = "", is_last: bool = True) -> None:
        """打印樹形結構"""
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{node['name']} ({node['type']})")

        if "children" in node:
            extension = "    " if is_last else "│   "
            for i, child in enumerate(node["children"]):
                is_last_child = i == len(node["children"]) - 1
                self._print_tree(child, prefix + extension, is_last_child)

    def example_graph_structure(self) -> None:
        """
        示例 6: 圖結構

        演示如何表示圖數據結構。
        """
        print(f"\n{'='*60}")
        print("示例 6: 圖結構 (社交網絡)")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 節點和邊
        lm += '{\n'
        lm += '  "nodes": [\n'

        nodes = []
        for i in range(3):
            lm += '    {\n'
            lm += '      "id": '
            lm += gen(name=f"node_id_{i}", regex=r'\d+')
            lm += ',\n'
            lm += '      "name": "'
            lm += gen(name=f"node_name_{i}", max_tokens=10, stop='"')
            lm += '",\n'
            lm += '      "type": "'
            lm += select(["user", "group", "page"], name=f"node_type_{i}")
            lm += '"\n'
            lm += '    }'

            if i < 2:
                lm += ','
            lm += '\n'

            nodes.append({
                "id": int(lm[f"node_id_{i}"]),
                "name": lm[f"node_name_{i}"],
                "type": lm[f"node_type_{i}"]
            })

        lm += '  ],\n'
        lm += '  "edges": [\n'

        edges = []
        for i in range(2):
            lm += '    {\n'
            lm += '      "from": '
            lm += gen(name=f"edge_from_{i}", regex=r'\d+')
            lm += ',\n'
            lm += '      "to": '
            lm += gen(name=f"edge_to_{i}", regex=r'\d+')
            lm += ',\n'
            lm += '      "type": "'
            lm += select(["friend", "follow", "like"], name=f"edge_type_{i}")
            lm += '"\n'
            lm += '    }'

            if i < 1:
                lm += ','
            lm += '\n'

            edges.append({
                "from": int(lm[f"edge_from_{i}"]),
                "to": int(lm[f"edge_to_{i}"]),
                "type": lm[f"edge_type_{i}"]
            })

        lm += '  ]\n'
        lm += '}'

        graph_data = {
            "nodes": nodes,
            "edges": edges
        }

        print("圖結構:")
        print(json.dumps(graph_data, indent=2, ensure_ascii=False))

        print("\n關係視圖:")
        for edge in edges:
            from_node = next((n for n in nodes if n["id"] == edge["from"]), None)
            to_node = next((n for n in nodes if n["id"] == edge["to"]), None)

            if from_node and to_node:
                print(f"  {from_node['name']} --[{edge['type']}]--> {to_node['name']}")

        print()

    def example_document_structure(self) -> None:
        """
        示例 7: 複雜文檔結構

        演示如何生成複雜的文檔結構。
        """
        print(f"\n{'='*60}")
        print("示例 7: 複雜文檔結構")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 文檔結構
        lm += '{\n'
        lm += '  "document": {\n'
        lm += '    "metadata": {\n'
        lm += '      "title": "'
        lm += gen(name="doc_title", max_tokens=20, stop='"')
        lm += '",\n'
        lm += '      "author": "'
        lm += gen(name="author", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '      "version": "'
        lm += gen(name="version", regex=r'\d+\.\d+\.\d+')
        lm += '",\n'
        lm += '      "created": "'
        lm += gen(name="created", regex=r'\d{4}-\d{2}-\d{2}')
        lm += '"\n'
        lm += '    },\n'
        lm += '    "sections": [\n'

        sections = []
        for i in range(2):
            lm += '      {\n'
            lm += '        "title": "'
            lm += gen(name=f"section_title_{i}", max_tokens=20, stop='"')
            lm += '",\n'
            lm += '        "content": {\n'
            lm += '          "paragraphs": [\n'

            paragraphs = []
            for j in range(2):
                lm += '            "'
                lm += gen(name=f"para_{i}_{j}", max_tokens=40, stop='"')
                lm += '"'
                if j < 1:
                    lm += ','
                lm += '\n'
                paragraphs.append(lm[f"para_{i}_{j}"])

            lm += '          ],\n'
            lm += '          "footnotes": ['

            footnotes = []
            for k in range(1):
                lm += '"'
                lm += gen(name=f"footnote_{i}_{k}", max_tokens=20, stop='"')
                lm += '"'
                footnotes.append(lm[f"footnote_{i}_{k}"])

            lm += ']\n'
            lm += '        }\n'
            lm += '      }'

            if i < 1:
                lm += ','
            lm += '\n'

            sections.append({
                "title": lm[f"section_title_{i}"],
                "content": {
                    "paragraphs": paragraphs,
                    "footnotes": footnotes
                }
            })

        lm += '    ]\n'
        lm += '  }\n'
        lm += '}'

        doc_data = {
            "document": {
                "metadata": {
                    "title": lm["doc_title"],
                    "author": lm["author"],
                    "version": lm["version"],
                    "created": lm["created"]
                },
                "sections": sections
            }
        }

        print("文檔結構:")
        print(json.dumps(doc_data, indent=2, ensure_ascii=False))
        print()

    def example_config_structure(self) -> None:
        """
        示例 8: 配置文件結構

        演示複雜的配置文件嵌套結構。
        """
        print(f"\n{'='*60}")
        print("示例 8: 配置文件結構")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "application": {\n'
        lm += '    "name": "'
        lm += gen(name="app_name", max_tokens=15, stop='"')
        lm += '",\n'
        lm += '    "server": {\n'
        lm += '      "host": "'
        lm += gen(name="host", regex=r'[a-z0-9.-]+')
        lm += '",\n'
        lm += '      "port": '
        lm += gen(name="port", regex=r'\d{4,5}')
        lm += ',\n'
        lm += '      "ssl": {\n'
        lm += '        "enabled": '
        lm += select(["true", "false"], name="ssl_enabled")
        lm += ',\n'
        lm += '        "certificate": "'
        lm += gen(name="cert_path", regex=r'/[a-z/]+\.crt')
        lm += '"\n'
        lm += '      }\n'
        lm += '    },\n'
        lm += '    "database": {\n'
        lm += '      "primary": {\n'
        lm += '        "host": "'
        lm += gen(name="db_host", regex=r'[a-z0-9.-]+')
        lm += '",\n'
        lm += '        "port": '
        lm += gen(name="db_port", regex=r'\d{4,5}')
        lm += '\n'
        lm += '      },\n'
        lm += '      "replica": {\n'
        lm += '        "host": "'
        lm += gen(name="replica_host", regex=r'[a-z0-9.-]+')
        lm += '",\n'
        lm += '        "port": '
        lm += gen(name="replica_port", regex=r'\d{4,5}')
        lm += '\n'
        lm += '      }\n'
        lm += '    },\n'
        lm += '    "logging": {\n'
        lm += '      "level": "'
        lm += select(["DEBUG", "INFO", "WARN", "ERROR"], name="log_level")
        lm += '",\n'
        lm += '      "handlers": ['

        handlers = []
        for i in range(2):
            lm += '"'
            lm += select(["console", "file", "syslog"], name=f"handler_{i}")
            lm += '"'
            if i < 1:
                lm += ', '
            handlers.append(lm[f"handler_{i}"])

        lm += ']\n'
        lm += '    }\n'
        lm += '  }\n'
        lm += '}'

        config_data = {
            "application": {
                "name": lm["app_name"],
                "server": {
                    "host": lm["host"],
                    "port": int(lm["port"]),
                    "ssl": {
                        "enabled": lm["ssl_enabled"] == "true",
                        "certificate": lm["cert_path"]
                    }
                },
                "database": {
                    "primary": {
                        "host": lm["db_host"],
                        "port": int(lm["db_port"])
                    },
                    "replica": {
                        "host": lm["replica_host"],
                        "port": int(lm["replica_port"])
                    }
                },
                "logging": {
                    "level": lm["log_level"],
                    "handlers": handlers
                }
            }
        }

        print("配置文件:")
        print(json.dumps(config_data, indent=2, ensure_ascii=False))
        print()

    def example_api_response_structure(self) -> None:
        """
        示例 9: API 響應結構

        演示複雜的 API 響應嵌套結構。
        """
        print(f"\n{'='*60}")
        print("示例 9: API 響應結構")
        print(f"{'='*60}\n")

        if not self.api_key:
            print("⚠️  未設置 API 密鑰，跳過此示例")
            return

        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "status": "success",\n'
        lm += '  "data": {\n'
        lm += '    "user": {\n'
        lm += '      "id": '
        lm += gen(name="user_id", regex=r'\d+')
        lm += ',\n'
        lm += '      "profile": {\n'
        lm += '        "username": "'
        lm += gen(name="username", regex=r'[a-z0-9_]{3,16}')
        lm += '",\n'
        lm += '        "settings": {\n'
        lm += '          "privacy": "'
        lm += select(["public", "private", "friends"], name="privacy")
        lm += '",\n'
        lm += '          "notifications": {\n'
        lm += '            "email": '
        lm += select(["true", "false"], name="notif_email")
        lm += ',\n'
        lm += '            "push": '
        lm += select(["true", "false"], name="notif_push")
        lm += '\n'
        lm += '          }\n'
        lm += '        }\n'
        lm += '      }\n'
        lm += '    },\n'
        lm += '    "posts": [\n'

        posts = []
        for i in range(2):
            lm += '      {\n'
            lm += '        "id": '
            lm += gen(name=f"post_id_{i}", regex=r'\d+')
            lm += ',\n'
            lm += '        "content": "'
            lm += gen(name=f"content_{i}", max_tokens=30, stop='"')
            lm += '",\n'
            lm += '        "stats": {\n'
            lm += '          "likes": '
            lm += gen(name=f"likes_{i}", regex=r'\d+')
            lm += ',\n'
            lm += '          "comments": '
            lm += gen(name=f"comments_{i}", regex=r'\d+')
            lm += '\n'
            lm += '        }\n'
            lm += '      }'

            if i < 1:
                lm += ','
            lm += '\n'

            posts.append({
                "id": int(lm[f"post_id_{i}"]),
                "content": lm[f"content_{i}"],
                "stats": {
                    "likes": int(lm[f"likes_{i}"]),
                    "comments": int(lm[f"comments_{i}"])
                }
            })

        lm += '    ]\n'
        lm += '  },\n'
        lm += '  "meta": {\n'
        lm += '    "timestamp": "'
        lm += gen(name="timestamp", regex=r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
        lm += '",\n'
        lm += '    "version": "'
        lm += gen(name="api_version", regex=r'\d+\.\d+')
        lm += '"\n'
        lm += '  }\n'
        lm += '}'

        api_response = {
            "status": "success",
            "data": {
                "user": {
                    "id": int(lm["user_id"]),
                    "profile": {
                        "username": lm["username"],
                        "settings": {
                            "privacy": lm["privacy"],
                            "notifications": {
                                "email": lm["notif_email"] == "true",
                                "push": lm["notif_push"] == "true"
                            }
                        }
                    }
                },
                "posts": posts
            },
            "meta": {
                "timestamp": lm["timestamp"],
                "version": lm["api_version"]
            }
        }

        print("API 響應:")
        print(json.dumps(api_response, indent=2, ensure_ascii=False))
        print()

    def example_validation(self) -> None:
        """
        示例 10: 嵌套結構驗證

        演示如何驗證生成的嵌套結構。
        """
        print(f"\n{'='*60}")
        print("示例 10: 嵌套結構驗證")
        print(f"{'='*60}\n")

        print("驗證嵌套結構的技巧:")

        tips = [
            "1. 使用 JSON Schema 定義結構規範",
            "2. 遞歸驗證每一層嵌套",
            "3. 檢查必需字段的存在性",
            "4. 驗證數據類型和範圍",
            "5. 處理可選字段和默認值",
            "6. 測試邊界情況和異常值",
            "7. 使用自動化測試工具",
            "8. 記錄驗證失敗的詳細信息"
        ]

        for tip in tips:
            print(f"  {tip}")

        print("\n示例驗證代碼:")

        validation_code = """
def validate_nested_structure(data: Dict, schema: Dict) -> bool:
    '''驗證嵌套結構'''

    def validate_field(value, field_schema):
        if field_schema['type'] == 'object':
            if not isinstance(value, dict):
                return False
            for key, sub_schema in field_schema.get('properties', {}).items():
                if key in field_schema.get('required', []):
                    if key not in value:
                        return False
                    if not validate_field(value[key], sub_schema):
                        return False
            return True

        elif field_schema['type'] == 'array':
            if not isinstance(value, list):
                return False
            for item in value:
                if not validate_field(item, field_schema['items']):
                    return False
            return True

        elif field_schema['type'] == 'string':
            return isinstance(value, str)

        elif field_schema['type'] == 'integer':
            return isinstance(value, int)

        elif field_schema['type'] == 'boolean':
            return isinstance(value, bool)

        return True

    return validate_field(data, schema)

# 使用示例
schema = {
    "type": "object",
    "properties": {
        "user": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
    },
    "required": ["user"]
}

data = {
    "user": {
        "name": "Alice",
        "age": 25
    }
}

is_valid = validate_nested_structure(data, schema)
print(f"驗證結果: {is_valid}")
"""

        print(validation_code)
        print()

    def run_all_examples(self) -> None:
        """運行所有示例"""
        print(f"\n{'='*60}")
        print("Guidance 嵌套結構 - 完整示例")
        print(f"{'='*60}")

        self.example_basic_nesting()
        self.example_nested_arrays()
        self.example_deep_nesting()
        self.example_mixed_nesting()
        self.example_tree_structure()
        self.example_graph_structure()
        self.example_document_structure()
        self.example_config_structure()
        self.example_api_response_structure()
        self.example_validation()

        print(f"\n{'='*60}")
        print("執行摘要")
        print(f"{'='*60}")
        print(f"✓ 所有嵌套結構示例執行完成!")


def main():
    """主函數"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         Guidance 框架 - 嵌套結構示例                       ║
    ║                                                            ║
    ║  生成和控制複雜的嵌套數據結構                              ║
    ║  包括多層對象、數組、樹、圖等結構                          ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    demo = NestedStructureDemo(
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    try:
        demo.run_all_examples()
    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷執行")
    except Exception as e:
        print(f"\n✗ 執行出錯: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
