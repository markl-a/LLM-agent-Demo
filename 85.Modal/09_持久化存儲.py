"""
Modal 持久化存儲示例

本示例展示：
1. 使用 Volumes 持久化文件
2. 使用 Secrets 管理密鑰
3. 使用 Dicts 鍵值存儲
4. 數據共享和管理
"""

import modal
from rich.console import Console
from rich.panel import Panel
import time

console = Console()

# 創建應用
app = modal.App("persistent-storage")

# 創建 Volume（持久化文件存儲）
volume = modal.Volume.from_name("my-data-volume", create_if_missing=True)

# 創建 Dict（鍵值存儲）
kv_store = modal.Dict.from_name("my-kv-store", create_if_missing=True)


# 示例 1: 使用 Volume 存儲文件
@app.function(volumes={"/data": volume})
def write_to_volume(filename: str, content: str) -> dict:
    """
    寫入文件到 Volume

    Volume 在函數執行完後會持久化，下次執行時可以訪問
    """
    filepath = f"/data/{filename}"

    print(f"寫入文件: {filepath}")

    with open(filepath, "w") as f:
        f.write(content)

    # 提交更改（重要！）
    volume.commit()

    return {
        "filepath": filepath,
        "size": len(content),
        "status": "written"
    }


@app.function(volumes={"/data": volume})
def read_from_volume(filename: str) -> dict:
    """從 Volume 讀取文件"""
    filepath = f"/data/{filename}"

    print(f"讀取文件: {filepath}")

    try:
        with open(filepath, "r") as f:
            content = f.read()

        return {
            "filepath": filepath,
            "content": content,
            "size": len(content),
            "status": "success"
        }
    except FileNotFoundError:
        return {
            "filepath": filepath,
            "error": "File not found",
            "status": "error"
        }


@app.function(volumes={"/data": volume})
def list_volume_files() -> dict:
    """列出 Volume 中的所有文件"""
    import os

    print("列出 Volume 中的文件...")

    files = []
    for root, dirs, filenames in os.walk("/data"):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            size = os.path.getsize(filepath)
            files.append({
                "path": filepath,
                "size": size,
                "modified": os.path.getmtime(filepath)
            })

    return {
        "total_files": len(files),
        "files": files
    }


# 示例 2: 使用 Secrets 管理密鑰
@app.function(
    secrets=[modal.Secret.from_dict({
        "API_KEY": "demo-api-key-12345",
        "DATABASE_URL": "postgresql://user:pass@host:5432/db"
    })]
)
def use_secrets() -> dict:
    """
    使用 Secrets

    Secrets 通過環境變量訪問
    """
    import os

    print("訪問 Secrets...")

    # 從環境變量讀取 secrets
    api_key = os.environ.get("API_KEY", "not-set")
    db_url = os.environ.get("DATABASE_URL", "not-set")

    # 不要在日誌中打印完整的 secret！
    print(f"API Key: {api_key[:10]}...")
    print(f"Database URL: {db_url[:20]}...")

    return {
        "has_api_key": api_key != "not-set",
        "has_db_url": db_url != "not-set",
        "api_key_preview": api_key[:10] + "..." if api_key != "not-set" else "not-set"
    }


# 示例 3: 使用 Dict 鍵值存儲
@app.function()
def dict_set(key: str, value: str) -> dict:
    """設置鍵值對"""
    print(f"設置: {key} = {value}")

    kv_store[key] = value

    return {
        "key": key,
        "value": value,
        "status": "set"
    }


@app.function()
def dict_get(key: str) -> dict:
    """獲取鍵值"""
    print(f"獲取: {key}")

    try:
        value = kv_store[key]
        return {
            "key": key,
            "value": value,
            "status": "found"
        }
    except KeyError:
        return {
            "key": key,
            "error": "Key not found",
            "status": "not_found"
        }


@app.function()
def dict_list_all() -> dict:
    """列出所有鍵值對"""
    print("列出所有鍵值對...")

    items = {}
    for key in kv_store.keys():
        items[key] = kv_store[key]

    return {
        "count": len(items),
        "items": items
    }


@app.function()
def dict_delete(key: str) -> dict:
    """刪除鍵值對"""
    print(f"刪除: {key}")

    try:
        del kv_store[key]
        return {
            "key": key,
            "status": "deleted"
        }
    except KeyError:
        return {
            "key": key,
            "error": "Key not found",
            "status": "not_found"
        }


# 示例 4: 緩存計算結果
@app.function()
def expensive_computation(n: int) -> dict:
    """
    昂貴的計算（帶緩存）
    """
    cache_key = f"fib_{n}"

    # 檢查緩存
    try:
        cached_result = kv_store[cache_key]
        print(f"使用緩存結果: {cache_key}")
        return {
            "n": n,
            "result": cached_result,
            "cached": True
        }
    except KeyError:
        pass

    # 計算
    print(f"計算 fibonacci({n})...")

    def fib(x):
        if x <= 1:
            return x
        return fib(x - 1) + fib(x - 2)

    start = time.time()
    result = fib(n)
    elapsed = time.time() - start

    # 存入緩存
    kv_store[cache_key] = result
    print(f"緩存結果: {cache_key} = {result}")

    return {
        "n": n,
        "result": result,
        "cached": False,
        "compute_time": elapsed
    }


# 示例 5: 使用 Volume 進行模型持久化
@app.function(volumes={"/models": volume})
def save_model(model_name: str, model_data: str) -> dict:
    """
    保存模型到 Volume

    實際應用中，model_data 會是序列化的模型權重
    """
    import pickle

    filepath = f"/models/{model_name}.pkl"

    print(f"保存模型: {filepath}")

    with open(filepath, "wb") as f:
        pickle.dump(model_data, f)

    volume.commit()

    return {
        "model_name": model_name,
        "filepath": filepath,
        "status": "saved"
    }


@app.function(volumes={"/models": volume})
def load_model(model_name: str) -> dict:
    """從 Volume 加載模型"""
    import pickle

    filepath = f"/models/{model_name}.pkl"

    print(f"加載模型: {filepath}")

    try:
        with open(filepath, "rb") as f:
            model_data = pickle.load(f)

        return {
            "model_name": model_name,
            "filepath": filepath,
            "model_data": str(model_data)[:100] + "...",
            "status": "loaded"
        }
    except FileNotFoundError:
        return {
            "model_name": model_name,
            "error": "Model not found",
            "status": "error"
        }


@app.local_entrypoint()
def main():
    """本地測試"""
    console.print(Panel.fit(
        "[bold cyan]Modal 持久化存儲示例[/bold cyan]\n"
        "[dim]Volumes, Secrets, Dicts[/dim]",
        border_style="cyan"
    ))

    # 1. Volume 文件存儲
    console.print("\n[cyan]1. 測試 Volume 文件存儲[/cyan]")

    # 寫入文件
    console.print("[yellow]  寫入文件...[/yellow]")
    result = write_to_volume.remote("test.txt", "Hello from Modal Volume!")
    console.print(f"[green]{result}[/green]")

    # 讀取文件
    console.print("[yellow]  讀取文件...[/yellow]")
    result = read_from_volume.remote("test.txt")
    console.print(f"[green]{result}[/green]")

    # 列出文件
    console.print("[yellow]  列出所有文件...[/yellow]")
    result = list_volume_files.remote()
    console.print(f"[green]找到 {result['total_files']} 個文件[/green]")

    # 2. Secrets
    console.print("\n[cyan]2. 測試 Secrets[/cyan]")
    result = use_secrets.remote()
    console.print(f"[green]{result}[/green]")

    # 3. Dict 鍵值存儲
    console.print("\n[cyan]3. 測試 Dict 鍵值存儲[/cyan]")

    # 設置鍵值
    console.print("[yellow]  設置鍵值...[/yellow]")
    dict_set.remote("user:1", "Alice")
    dict_set.remote("user:2", "Bob")
    dict_set.remote("config:version", "1.0.0")

    # 獲取鍵值
    console.print("[yellow]  獲取鍵值...[/yellow]")
    result = dict_get.remote("user:1")
    console.print(f"[green]{result}[/green]")

    # 列出所有
    console.print("[yellow]  列出所有鍵值對...[/yellow]")
    result = dict_list_all.remote()
    console.print(f"[green]共 {result['count']} 個鍵值對: {result['items']}[/green]")

    # 4. 緩存示例
    console.print("\n[cyan]4. 測試計算緩存[/cyan]")

    # 首次計算（無緩存）
    console.print("[yellow]  首次計算...[/yellow]")
    result1 = expensive_computation.remote(30)
    console.print(f"[green]結果: {result1['result']}, 緩存: {result1['cached']}[/green]")

    # 再次計算（使用緩存）
    console.print("[yellow]  再次計算（應該使用緩存）...[/yellow]")
    result2 = expensive_computation.remote(30)
    console.print(f"[green]結果: {result2['result']}, 緩存: {result2['cached']}[/green]")

    # 5. 模型存儲
    console.print("\n[cyan]5. 測試模型持久化[/cyan]")

    # 保存模型
    console.print("[yellow]  保存模型...[/yellow]")
    result = save_model.remote("my_model_v1", "model_weights_data_here")
    console.print(f"[green]{result}[/green]")

    # 加載模型
    console.print("[yellow]  加載模型...[/yellow]")
    result = load_model.remote("my_model_v1")
    console.print(f"[green]{result}[/green]")

    console.print("\n" + "="*60)
    console.print("[bold green]✓ 持久化存儲示例完成！[/bold green]")


def print_storage_guide():
    """打印存儲指南"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]持久化存儲指南:[/bold cyan]")
    console.print("""
[green]1. Volumes（文件存儲）:[/green]

# 創建 Volume
volume = modal.Volume.from_name("my-vol", create_if_missing=True)

# 掛載到函數
@app.function(volumes={"/data": volume})
def use_volume():
    # 讀寫文件
    with open("/data/file.txt", "w") as f:
        f.write("data")

    # 提交更改（重要！）
    volume.commit()

[green]2. Secrets（密鑰管理）:[/green]

# 創建 Secret（CLI）
modal secret create my-secret \\
  API_KEY=xxx \\
  DATABASE_URL=yyy

# 使用 Secret
@app.function(secrets=[modal.Secret.from_name("my-secret")])
def use_secret():
    import os
    api_key = os.environ["API_KEY"]

[green]3. Dicts（鍵值存儲）:[/green]

# 創建 Dict
kv = modal.Dict.from_name("my-dict", create_if_missing=True)

# 使用
kv["key"] = "value"
value = kv["key"]
del kv["key"]

# 遍歷
for key in kv.keys():
    print(kv[key])

[yellow]使用場景:[/yellow]

Volumes:
  ✓ 模型權重持久化
  ✓ 數據集存儲
  ✓ 大文件共享
  ✓ 日誌和輸出

Secrets:
  ✓ API 密鑰
  ✓ 數據庫連接
  ✓ 憑證和令牌
  ✓ 敏感配置

Dicts:
  ✓ 配置管理
  ✓ 緩存
  ✓ 計數器
  ✓ 小量數據共享

[yellow]最佳實踐:[/yellow]

✓ Volume 寫入後必須 commit()
✓ Secret 不要打印到日誌
✓ Dict 適合小數據（< 10MB）
✓ 定期清理不用的 Volume
✓ 使用有意義的名稱
    """)
    console.print("="*60 + "\n")


if __name__ == "__main__":
    print_storage_guide()
    console.print("[yellow]運行存儲示例:[/yellow]")
    console.print("  modal run 09_持久化存儲.py\n")

    console.print("[yellow]管理 Volumes:[/yellow]")
    console.print("  modal volume list")
    console.print("  modal volume delete my-data-volume\n")

    console.print("[yellow]管理 Secrets:[/yellow]")
    console.print("  modal secret list")
    console.print("  modal secret create my-secret KEY=value\n")
