#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Guidance JSON 生成示例
====================================================

本模塊展示如何使用 Guidance 生成符合 JSON Schema 的結構化數據:
1. 基本 JSON 對象生成
2. JSON Schema 約束
3. 嵌套對象和數組
4. 複雜數據結構
5. API 響應生成
6. 配置文件生成
7. 數據模型實例化
8. JSON 驗證和轉換

Guidance 的 JSON 生成功能保證 100% 語法正確的 JSON 輸出，
這在傳統方法中經常出現語法錯誤。

作者: Guidance 示例團隊
日期: 2025-01-01
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

try:
    from guidance import models, gen, select
    import guidance
except ImportError:
    print("錯誤: 請先安裝 guidance 庫")
    sys.exit(1)


class JSONGenerator:
    """
    JSON 生成演示類

    展示 Guidance 的 JSON Schema 功能和結構化數據生成。

    Attributes:
        model_name: 模型名稱
        api_key: API 密鑰
        generated_jsons: 已生成的 JSON 記錄
    """

    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        """初始化 JSON 生成器"""
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.generated_jsons: List[Dict] = []

    def example_basic_json(self) -> None:
        """
        示例 1: 基本 JSON 生成

        演示如何生成簡單的 JSON 對象。
        """
        print(f"\n{'='*60}")
        print("示例 1: 基本 JSON 生成")
        print(f"{'='*60}\n")

        # 簡單對象
        print("生成用戶對象:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 手動構建 JSON
        lm += '{\n'
        lm += '  "name": "'
        lm += gen(name="name", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '  "age": '
        lm += gen(name="age", regex=r'\d{1,3}')
        lm += ',\n'
        lm += '  "email": "'
        lm += gen(name="email", regex=r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        lm += '"\n'
        lm += '}'

        # 解析生成的 JSON
        json_str = f'{{\n  "name": "{lm["name"]}",\n  "age": {lm["age"]},\n  "email": "{lm["email"]}"\n}}'
        user_data = json.loads(json_str)

        print("生成的用戶數據:")
        print(json.dumps(user_data, indent=2, ensure_ascii=False))

        # 布爾值
        print("\n\n生成帶布爾值的配置:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "enabled": '
        lm += select(["true", "false"], name="enabled")
        lm += ',\n'
        lm += '  "debug": '
        lm += select(["true", "false"], name="debug")
        lm += ',\n'
        lm += '  "timeout": '
        lm += gen(name="timeout", regex=r'\d+')
        lm += '\n}'

        config_str = f'{{\n  "enabled": {lm["enabled"]},\n  "debug": {lm["debug"]},\n  "timeout": {lm["timeout"]}\n}}'
        config_data = json.loads(config_str)

        print("生成的配置:")
        print(json.dumps(config_data, indent=2))

    def example_json_schema(self) -> Dict[str, Any]:
        """
        示例 2: JSON Schema 約束

        演示如何使用 JSON Schema 定義和生成複雜的 JSON 結構。

        Returns:
            生成的 JSON 數據
        """
        print(f"\n{'='*60}")
        print("示例 2: JSON Schema 約束")
        print(f"{'='*60}\n")

        # 定義 JSON Schema
        user_schema = {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 20
                },
                "email": {
                    "type": "string",
                    "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                },
                "age": {
                    "type": "integer",
                    "minimum": 18,
                    "maximum": 120
                },
                "is_active": {
                    "type": "boolean"
                },
                "role": {
                    "type": "string",
                    "enum": ["admin", "user", "guest"]
                }
            },
            "required": ["username", "email", "age"]
        }

        print("使用 Schema 生成用戶數據:")
        print(f"\nSchema 定義:")
        print(json.dumps(user_schema, indent=2))

        # 根據 schema 生成數據
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "username": "'
        lm += gen(name="username", regex=r'[a-zA-Z0-9_]{3,20}')
        lm += '",\n'
        lm += '  "email": "'
        lm += gen(name="email", regex=r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        lm += '",\n'
        lm += '  "age": '
        lm += gen(name="age", regex=r'[1-9]\d{1,2}')
        lm += ',\n'
        lm += '  "is_active": '
        lm += select(["true", "false"], name="is_active")
        lm += ',\n'
        lm += '  "role": "'
        lm += select(["admin", "user", "guest"], name="role")
        lm += '"\n}'

        user_json = {
            "username": lm["username"],
            "email": lm["email"],
            "age": int(lm["age"]),
            "is_active": lm["is_active"] == "true",
            "role": lm["role"]
        }

        print(f"\n生成的用戶數據:")
        print(json.dumps(user_json, indent=2, ensure_ascii=False))

        return user_json

    def example_nested_objects(self) -> None:
        """
        示例 3: 嵌套對象

        演示如何生成包含嵌套對象的複雜 JSON 結構。
        """
        print(f"\n{'='*60}")
        print("示例 3: 嵌套對象")
        print(f"{'='*60}\n")

        # 生成嵌套的用戶資料
        print("生成完整用戶資料 (包含地址):")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "user": {\n'
        lm += '    "id": '
        lm += gen(name="user_id", regex=r'\d+')
        lm += ',\n'
        lm += '    "name": "'
        lm += gen(name="name", max_tokens=10, stop='"')
        lm += '"\n'
        lm += '  },\n'
        lm += '  "address": {\n'
        lm += '    "street": "'
        lm += gen(name="street", max_tokens=20, stop='"')
        lm += '",\n'
        lm += '    "city": "'
        lm += gen(name="city", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '    "zipCode": "'
        lm += gen(name="zip", regex=r'\d{5}')
        lm += '"\n'
        lm += '  },\n'
        lm += '  "settings": {\n'
        lm += '    "theme": "'
        lm += select(["light", "dark"], name="theme")
        lm += '",\n'
        lm += '    "notifications": '
        lm += select(["true", "false"], name="notifications")
        lm += '\n'
        lm += '  }\n'
        lm += '}'

        profile = {
            "user": {
                "id": int(lm["user_id"]),
                "name": lm["name"]
            },
            "address": {
                "street": lm["street"],
                "city": lm["city"],
                "zipCode": lm["zip"]
            },
            "settings": {
                "theme": lm["theme"],
                "notifications": lm["notifications"] == "true"
            }
        }

        print("生成的資料:")
        print(json.dumps(profile, indent=2, ensure_ascii=False))

        # 多層嵌套
        print("\n\n生成組織架構 (多層嵌套):")
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
        lm += '      "manager": {\n'
        lm += '        "name": "'
        lm += gen(name="manager_name", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '        "title": "'
        lm += gen(name="title", max_tokens=15, stop='"')
        lm += '"\n'
        lm += '      }\n'
        lm += '    }\n'
        lm += '  }\n'
        lm += '}'

        org = {
            "company": {
                "name": lm["company_name"],
                "department": {
                    "name": lm["dept_name"],
                    "manager": {
                        "name": lm["manager_name"],
                        "title": lm["title"]
                    }
                }
            }
        }

        print("組織架構:")
        print(json.dumps(org, indent=2, ensure_ascii=False))

    def example_arrays(self) -> None:
        """
        示例 4: 數組生成

        演示如何生成包含數組的 JSON 結構。
        """
        print(f"\n{'='*60}")
        print("示例 4: 數組生成")
        print(f"{'='*60}\n")

        # 簡單數組
        print("生成標籤數組:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
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

        tag_data = {"tags": tags}
        print("標籤數據:")
        print(json.dumps(tag_data, indent=2, ensure_ascii=False))

        # 對象數組
        print("\n\n生成產品列表:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "products": [\n'

        products = []
        for i in range(3):
            lm += '    {\n'
            lm += '      "id": '
            lm += gen(name=f"prod_id_{i}", regex=r'\d+')
            lm += ',\n'
            lm += '      "name": "'
            lm += gen(name=f"prod_name_{i}", max_tokens=15, stop='"')
            lm += '",\n'
            lm += '      "price": '
            lm += gen(name=f"price_{i}", regex=r'\d+\.\d{2}')
            lm += '\n'
            lm += '    }'

            if i < 2:
                lm += ','
            lm += '\n'

            products.append({
                "id": int(lm[f"prod_id_{i}"]),
                "name": lm[f"prod_name_{i}"],
                "price": float(lm[f"price_{i}"])
            })

        lm += '  ]\n'
        lm += '}'

        product_data = {"products": products}
        print("產品列表:")
        print(json.dumps(product_data, indent=2, ensure_ascii=False))

    def example_api_responses(self) -> None:
        """
        示例 5: API 響應生成

        演示如何生成標準的 API 響應格式。
        """
        print(f"\n{'='*60}")
        print("示例 5: API 響應生成")
        print(f"{'='*60}\n")

        # 成功響應
        print("生成成功響應:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "status": "success",\n'
        lm += '  "code": 200,\n'
        lm += '  "data": {\n'
        lm += '    "id": '
        lm += gen(name="id", regex=r'\d+')
        lm += ',\n'
        lm += '    "message": "'
        lm += gen(name="message", max_tokens=30, stop='"')
        lm += '"\n'
        lm += '  },\n'
        lm += '  "timestamp": "'
        lm += gen(name="timestamp", regex=r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
        lm += '"\n'
        lm += '}'

        success_response = {
            "status": "success",
            "code": 200,
            "data": {
                "id": int(lm["id"]),
                "message": lm["message"]
            },
            "timestamp": lm["timestamp"]
        }

        print(json.dumps(success_response, indent=2, ensure_ascii=False))

        # 錯誤響應
        print("\n\n生成錯誤響應:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "status": "error",\n'
        lm += '  "code": '
        lm += select(["400", "401", "403", "404", "500"], name="error_code")
        lm += ',\n'
        lm += '  "error": {\n'
        lm += '    "type": "'
        lm += gen(name="error_type", max_tokens=15, stop='"')
        lm += '",\n'
        lm += '    "message": "'
        lm += gen(name="error_message", max_tokens=50, stop='"')
        lm += '"\n'
        lm += '  }\n'
        lm += '}'

        error_response = {
            "status": "error",
            "code": int(lm["error_code"]),
            "error": {
                "type": lm["error_type"],
                "message": lm["error_message"]
            }
        }

        print(json.dumps(error_response, indent=2, ensure_ascii=False))

        # 分頁響應
        print("\n\n生成分頁響應:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "data": [],\n'
        lm += '  "pagination": {\n'
        lm += '    "page": '
        lm += gen(name="page", regex=r'\d+')
        lm += ',\n'
        lm += '    "perPage": '
        lm += gen(name="per_page", regex=r'\d+')
        lm += ',\n'
        lm += '    "total": '
        lm += gen(name="total", regex=r'\d+')
        lm += ',\n'
        lm += '    "totalPages": '
        lm += gen(name="total_pages", regex=r'\d+')
        lm += '\n'
        lm += '  }\n'
        lm += '}'

        pagination_response = {
            "data": [],
            "pagination": {
                "page": int(lm["page"]),
                "perPage": int(lm["per_page"]),
                "total": int(lm["total"]),
                "totalPages": int(lm["total_pages"])
            }
        }

        print(json.dumps(pagination_response, indent=2))

    def example_config_files(self) -> None:
        """
        示例 6: 配置文件生成

        演示如何生成各種類型的配置文件。
        """
        print(f"\n{'='*60}")
        print("示例 6: 配置文件生成")
        print(f"{'='*60}\n")

        # 數據庫配置
        print("生成數據庫配置:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "database": {\n'
        lm += '    "host": "'
        lm += gen(name="db_host", regex=r'[a-z0-9.-]+')
        lm += '",\n'
        lm += '    "port": '
        lm += gen(name="db_port", regex=r'\d{4,5}')
        lm += ',\n'
        lm += '    "username": "'
        lm += gen(name="db_user", regex=r'[a-z0-9_]+')
        lm += '",\n'
        lm += '    "password": "'
        lm += gen(name="db_pass", max_tokens=20, stop='"')
        lm += '",\n'
        lm += '    "database": "'
        lm += gen(name="db_name", regex=r'[a-z0-9_]+')
        lm += '"\n'
        lm += '  }\n'
        lm += '}'

        db_config = {
            "database": {
                "host": lm["db_host"],
                "port": int(lm["db_port"]),
                "username": lm["db_user"],
                "password": "********",  # 不顯示密碼
                "database": lm["db_name"]
            }
        }

        print(json.dumps(db_config, indent=2))

        # 應用配置
        print("\n\n生成應用配置:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "app": {\n'
        lm += '    "name": "'
        lm += gen(name="app_name", max_tokens=15, stop='"')
        lm += '",\n'
        lm += '    "version": "'
        lm += gen(name="version", regex=r'\d+\.\d+\.\d+')
        lm += '",\n'
        lm += '    "environment": "'
        lm += select(["development", "staging", "production"], name="env")
        lm += '",\n'
        lm += '    "debug": '
        lm += select(["true", "false"], name="debug")
        lm += ',\n'
        lm += '    "logLevel": "'
        lm += select(["debug", "info", "warn", "error"], name="log_level")
        lm += '"\n'
        lm += '  }\n'
        lm += '}'

        app_config = {
            "app": {
                "name": lm["app_name"],
                "version": lm["version"],
                "environment": lm["env"],
                "debug": lm["debug"] == "true",
                "logLevel": lm["log_level"]
            }
        }

        print(json.dumps(app_config, indent=2, ensure_ascii=False))

    def example_data_models(self) -> None:
        """
        示例 7: 數據模型實例化

        演示如何為常見的數據模型生成實例。
        """
        print(f"\n{'='*60}")
        print("示例 7: 數據模型實例化")
        print(f"{'='*60}\n")

        # 博客文章模型
        print("生成博客文章:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "id": '
        lm += gen(name="post_id", regex=r'\d+')
        lm += ',\n'
        lm += '  "title": "'
        lm += gen(name="title", max_tokens=30, stop='"')
        lm += '",\n'
        lm += '  "slug": "'
        lm += gen(name="slug", regex=r'[a-z0-9-]+')
        lm += '",\n'
        lm += '  "author": {\n'
        lm += '    "id": '
        lm += gen(name="author_id", regex=r'\d+')
        lm += ',\n'
        lm += '    "name": "'
        lm += gen(name="author_name", max_tokens=15, stop='"')
        lm += '"\n'
        lm += '  },\n'
        lm += '  "published": '
        lm += select(["true", "false"], name="published")
        lm += ',\n'
        lm += '  "tags": ['

        tags = []
        for i in range(3):
            lm += '"'
            lm += gen(name=f"tag_{i}", max_tokens=10, stop='"')
            lm += '"'
            if i < 2:
                lm += ', '
            tags.append(lm[f"tag_{i}"])

        lm += '],\n'
        lm += '  "createdAt": "'
        lm += gen(name="created_at", regex=r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
        lm += '"\n'
        lm += '}'

        post = {
            "id": int(lm["post_id"]),
            "title": lm["title"],
            "slug": lm["slug"],
            "author": {
                "id": int(lm["author_id"]),
                "name": lm["author_name"]
            },
            "published": lm["published"] == "true",
            "tags": tags,
            "createdAt": lm["created_at"]
        }

        print("文章數據:")
        print(json.dumps(post, indent=2, ensure_ascii=False))

        # 訂單模型
        print("\n\n生成訂單:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "orderId": "'
        lm += gen(name="order_id", regex=r'ORD-\d{6}')
        lm += '",\n'
        lm += '  "customer": {\n'
        lm += '    "name": "'
        lm += gen(name="customer_name", max_tokens=15, stop='"')
        lm += '",\n'
        lm += '    "email": "'
        lm += gen(name="customer_email", regex=r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        lm += '"\n'
        lm += '  },\n'
        lm += '  "status": "'
        lm += select(["pending", "processing", "shipped", "delivered", "cancelled"], name="status")
        lm += '",\n'
        lm += '  "total": '
        lm += gen(name="total", regex=r'\d+\.\d{2}')
        lm += '\n'
        lm += '}'

        order = {
            "orderId": lm["order_id"],
            "customer": {
                "name": lm["customer_name"],
                "email": lm["customer_email"]
            },
            "status": lm["status"],
            "total": float(lm["total"])
        }

        print("訂單數據:")
        print(json.dumps(order, indent=2, ensure_ascii=False))

    def example_complex_structures(self) -> Dict[str, Any]:
        """
        示例 8: 複雜數據結構

        演示如何生成包含多層嵌套、數組、混合類型的複雜結構。

        Returns:
            複雜的 JSON 數據
        """
        print(f"\n{'='*60}")
        print("示例 8: 複雜數據結構")
        print(f"{'='*60}\n")

        print("生成完整的用戶配置:")
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        # 構建複雜的 JSON 結構
        lm += '{\n'
        lm += '  "user": {\n'
        lm += '    "profile": {\n'
        lm += '      "username": "'
        lm += gen(name="username", regex=r'[a-z0-9_]{3,20}')
        lm += '",\n'
        lm += '      "displayName": "'
        lm += gen(name="display_name", max_tokens=15, stop='"')
        lm += '"\n'
        lm += '    },\n'
        lm += '    "preferences": {\n'
        lm += '      "theme": "'
        lm += select(["light", "dark", "auto"], name="theme")
        lm += '",\n'
        lm += '      "language": "'
        lm += select(["en", "zh", "ja"], name="language")
        lm += '",\n'
        lm += '      "notifications": {\n'
        lm += '        "email": '
        lm += select(["true", "false"], name="notif_email")
        lm += ',\n'
        lm += '        "push": '
        lm += select(["true", "false"], name="notif_push")
        lm += '\n'
        lm += '      }\n'
        lm += '    },\n'
        lm += '    "roles": ['

        roles = []
        for i in range(2):
            lm += '"'
            role = select(["admin", "editor", "viewer"], name=f"role_{i}")
            lm += role
            lm += '"'
            if i < 1:
                lm += ', '
            roles.append(lm[f"role_{i}"])

        lm += '],\n'
        lm += '    "metadata": {\n'
        lm += '      "lastLogin": "'
        lm += gen(name="last_login", regex=r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
        lm += '",\n'
        lm += '      "loginCount": '
        lm += gen(name="login_count", regex=r'\d+')
        lm += '\n'
        lm += '    }\n'
        lm += '  }\n'
        lm += '}'

        complex_data = {
            "user": {
                "profile": {
                    "username": lm["username"],
                    "displayName": lm["display_name"]
                },
                "preferences": {
                    "theme": lm["theme"],
                    "language": lm["language"],
                    "notifications": {
                        "email": lm["notif_email"] == "true",
                        "push": lm["notif_push"] == "true"
                    }
                },
                "roles": roles,
                "metadata": {
                    "lastLogin": lm["last_login"],
                    "loginCount": int(lm["login_count"])
                }
            }
        }

        print("複雜配置:")
        print(json.dumps(complex_data, indent=2, ensure_ascii=False))

        return complex_data

    def example_json_validation(self) -> None:
        """
        示例 9: JSON 驗證

        演示如何驗證生成的 JSON 是否符合預期。
        """
        print(f"\n{'='*60}")
        print("示例 9: JSON 驗證")
        print(f"{'='*60}\n")

        print("生成並驗證 JSON:")

        # 生成 JSON
        lm = models.OpenAI(self.model_name, api_key=self.api_key)

        lm += '{\n'
        lm += '  "name": "'
        lm += gen(name="name", max_tokens=10, stop='"')
        lm += '",\n'
        lm += '  "value": '
        lm += gen(name="value", regex=r'\d+')
        lm += '\n'
        lm += '}'

        json_str = f'{{\n  "name": "{lm["name"]}",\n  "value": {lm["value"]}\n}}'

        # 驗證 JSON 語法
        try:
            data = json.loads(json_str)
            print(f"✓ JSON 語法有效")
            print(f"數據: {json.dumps(data, indent=2, ensure_ascii=False)}")

            # 驗證數據類型
            assert isinstance(data["name"], str), "name 必須是字符串"
            assert isinstance(data["value"], int), "value 必須是整數"
            print(f"✓ 數據類型驗證通過")

            # 驗證數據範圍
            assert len(data["name"]) > 0, "name 不能為空"
            assert data["value"] >= 0, "value 必須非負"
            print(f"✓ 數據範圍驗證通過")

        except json.JSONDecodeError as e:
            print(f"✗ JSON 語法錯誤: {e}")
        except AssertionError as e:
            print(f"✗ 驗證失敗: {e}")

    def example_batch_generation(self) -> List[Dict]:
        """
        示例 10: 批量生成

        演示如何批量生成多個 JSON 對象。

        Returns:
            生成的 JSON 列表
        """
        print(f"\n{'='*60}")
        print("示例 10: 批量 JSON 生成")
        print(f"{'='*60}\n")

        print("批量生成用戶數據:")

        users = []
        for i in range(3):
            lm = models.OpenAI(self.model_name, api_key=self.api_key)

            lm += '{\n'
            lm += '  "id": '
            lm += gen(name="id", regex=r'\d+')
            lm += ',\n'
            lm += '  "username": "'
            lm += gen(name="username", regex=r'[a-z0-9_]{3,16}')
            lm += '",\n'
            lm += '  "email": "'
            lm += gen(name="email", regex=r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
            lm += '",\n'
            lm += '  "role": "'
            lm += select(["admin", "user", "guest"], name="role")
            lm += '"\n'
            lm += '}'

            user = {
                "id": int(lm["id"]),
                "username": lm["username"],
                "email": lm["email"],
                "role": lm["role"]
            }

            users.append(user)
            print(f"\n用戶 {i+1}:")
            print(json.dumps(user, indent=2, ensure_ascii=False))

        print(f"\n\n生成了 {len(users)} 個用戶")

        return users

    def run_all_examples(self) -> None:
        """運行所有示例"""
        print(f"\n{'='*60}")
        print("Guidance JSON 生成 - 完整示例")
        print(f"{'='*60}")

        self.example_basic_json()
        user_data = self.example_json_schema()
        self.example_nested_objects()
        self.example_arrays()
        self.example_api_responses()
        self.example_config_files()
        self.example_data_models()
        complex_data = self.example_complex_structures()
        self.example_json_validation()
        batch_users = self.example_batch_generation()

        print(f"\n{'='*60}")
        print("執行摘要")
        print(f"{'='*60}")
        print(f"✓ 所有 JSON 生成示例執行完成!")
        print(f"\n批量生成的用戶數: {len(batch_users)}")


def main():
    """主函數"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         Guidance 框架 - JSON 生成示例                      ║
    ║                                                            ║
    ║  使用 JSON Schema 確保 100% 語法正確的 JSON 輸出           ║
    ║  適用於 API 響應、配置文件、數據模型等場景                 ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  警告: 未設置 OPENAI_API_KEY 環境變量")
        return

    generator = JSONGenerator(
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    try:
        generator.run_all_examples()
    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷執行")
    except Exception as e:
        print(f"\n✗ 執行出錯: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
