"""
Modal 數據處理示例

本示例展示：
1. 大規模數據處理管道
2. 並行數據處理
3. 數據轉換和清洗
4. ETL 流程
"""

import modal
from rich.console import Console
from rich.panel import Panel
import time

console = Console()

# 創建應用
app = modal.App("data-processing")

# 定義數據處理鏡像
data_image = modal.Image.debian_slim().pip_install(
    "pandas",
    "numpy",
    "pillow"
)


# 示例 1: CSV 數據處理
@app.function(image=data_image)
def process_csv_data(data: list) -> dict:
    """
    處理 CSV 格式的數據

    Args:
        data: 數據行列表

    Returns:
        處理結果統計
    """
    import pandas as pd

    print(f"處理 {len(data)} 行數據...")

    # 創建 DataFrame
    df = pd.DataFrame(data)

    # 數據清洗和轉換
    result = {
        "total_rows": len(df),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": df.isnull().sum().to_dict(),
        "summary": df.describe().to_dict() if len(df) > 0 else {}
    }

    print(f"處理完成: {result['total_rows']} 行")
    return result


# 示例 2: 並行處理大型數據集
@app.function(image=data_image)
def process_chunk(chunk_id: int, data_chunk: list) -> dict:
    """
    處理單個數據塊（用於並行處理）

    Args:
        chunk_id: 塊編號
        data_chunk: 數據塊

    Returns:
        處理結果
    """
    import pandas as pd

    print(f"處理數據塊 {chunk_id}，包含 {len(data_chunk)} 行")

    # 模擬數據處理
    time.sleep(0.5)

    # 簡單的聚合
    df = pd.DataFrame(data_chunk)

    result = {
        "chunk_id": chunk_id,
        "rows_processed": len(df),
        "sum": df.select_dtypes(include=['number']).sum().to_dict() if len(df) > 0 else {}
    }

    print(f"塊 {chunk_id} 處理完成")
    return result


# 示例 3: 圖像批量處理
@app.function(image=data_image)
def process_image(image_url: str, operations: list) -> dict:
    """
    處理單張圖像

    Args:
        image_url: 圖像 URL
        operations: 操作列表 ['resize', 'grayscale', 'rotate']

    Returns:
        處理結果
    """
    from PIL import Image
    import requests
    from io import BytesIO
    import base64

    print(f"處理圖像: {image_url}")

    # 下載圖像
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    original_size = img.size

    # 執行操作
    for operation in operations:
        if operation == 'resize':
            img = img.resize((224, 224))
        elif operation == 'grayscale':
            img = img.convert('L')
        elif operation == 'rotate':
            img = img.rotate(90)

    # 轉換為 base64（用於返回）
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    return {
        "original_size": original_size,
        "processed_size": img.size,
        "operations": operations,
        "image_base64": img_base64[:100] + "..."  # 截斷用於顯示
    }


# 示例 4: 數據清洗
@app.function(image=data_image)
def clean_data(records: list) -> dict:
    """
    數據清洗和驗證

    Args:
        records: 原始數據記錄

    Returns:
        清洗後的數據和統計
    """
    import pandas as pd

    print(f"清洗 {len(records)} 條記錄...")

    df = pd.DataFrame(records)

    # 刪除重複項
    original_count = len(df)
    df = df.drop_duplicates()
    duplicates_removed = original_count - len(df)

    # 填充缺失值
    missing_before = df.isnull().sum().sum()
    df = df.fillna(method='ffill').fillna(0)
    missing_after = df.isnull().sum().sum()

    # 移除異常值（示例：使用 IQR 方法）
    numeric_cols = df.select_dtypes(include=['number']).columns
    outliers_removed = 0

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        before = len(df)
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        outliers_removed += before - len(df)

    cleaned_data = df.to_dict('records')

    return {
        "original_count": original_count,
        "cleaned_count": len(cleaned_data),
        "duplicates_removed": duplicates_removed,
        "missing_filled": missing_before - missing_after,
        "outliers_removed": outliers_removed,
        "cleaned_data": cleaned_data[:10]  # 返回前 10 條用於預覽
    }


# 示例 5: ETL 管道
@app.function(image=data_image)
def extract_data(source: str) -> list:
    """提取數據（Extract）"""
    print(f"從 {source} 提取數據...")

    # 模擬數據提取
    data = [
        {"id": i, "value": i * 10, "category": f"cat_{i % 3}"}
        for i in range(100)
    ]

    print(f"提取了 {len(data)} 條記錄")
    return data


@app.function(image=data_image)
def transform_data(data: list) -> list:
    """轉換數據（Transform）"""
    import pandas as pd

    print(f"轉換 {len(data)} 條記錄...")

    df = pd.DataFrame(data)

    # 數據轉換
    df['value_squared'] = df['value'] ** 2
    df['value_normalized'] = (df['value'] - df['value'].mean()) / df['value'].std()

    # 分組聚合
    df_grouped = df.groupby('category').agg({
        'value': ['mean', 'sum', 'count'],
        'value_squared': 'sum'
    }).reset_index()

    transformed = df_grouped.to_dict('records')

    print(f"轉換完成，生成 {len(transformed)} 條聚合記錄")
    return transformed


@app.function(image=data_image)
def load_data(data: list, destination: str) -> dict:
    """加載數據（Load）"""
    print(f"加載 {len(data)} 條記錄到 {destination}...")

    # 模擬數據加載（實際應用中會寫入數據庫或文件）
    time.sleep(0.5)

    result = {
        "destination": destination,
        "records_loaded": len(data),
        "status": "success"
    }

    print(f"加載完成: {result}")
    return result


@app.local_entrypoint()
def main():
    """本地測試"""
    console.print(Panel.fit(
        "[bold cyan]Modal 數據處理示例[/bold cyan]\n"
        "[dim]大規模數據處理管道[/dim]",
        border_style="cyan"
    ))

    # 1. CSV 數據處理
    console.print("\n[cyan]1. 處理 CSV 數據[/cyan]")
    sample_data = [
        {"name": "Alice", "age": 30, "score": 85},
        {"name": "Bob", "age": 25, "score": 92},
        {"name": "Charlie", "age": 35, "score": 78}
    ]
    result = process_csv_data.remote(sample_data)
    console.print(f"[green]結果: 處理了 {result['total_rows']} 行[/green]")

    # 2. 並行處理大型數據集
    console.print("\n[cyan]2. 並行處理數據塊[/cyan]")

    # 創建測試數據並分塊
    large_dataset = [
        {"id": i, "value": i * 2}
        for i in range(1000)
    ]

    chunk_size = 100
    chunks = [
        large_dataset[i:i + chunk_size]
        for i in range(0, len(large_dataset), chunk_size)
    ]

    # 並行處理所有塊
    start_time = time.time()
    results = list(process_chunk.map(
        enumerate(chunks),
        kwargs=[{"data_chunk": chunk} for chunk in chunks]
    ))
    elapsed = time.time() - start_time

    console.print(f"[green]並行處理 {len(chunks)} 個數據塊[/green]")
    console.print(f"[dim]耗時: {elapsed:.2f} 秒[/dim]")

    # 3. 數據清洗
    console.print("\n[cyan]3. 數據清洗[/cyan]")
    dirty_data = [
        {"name": "Alice", "score": 85},
        {"name": "Bob", "score": 92},
        {"name": "Alice", "score": 85},  # 重複
        {"name": "Charlie", "score": None},  # 缺失
        {"name": "David", "score": 200}  # 異常值
    ]
    result = clean_data.remote(dirty_data)
    console.print(f"[green]清洗結果:[/green]")
    console.print(f"  原始: {result['original_count']} 條")
    console.print(f"  清洗後: {result['cleaned_count']} 條")
    console.print(f"  移除重複: {result['duplicates_removed']} 條")

    # 4. ETL 管道
    console.print("\n[cyan]4. 執行 ETL 管道[/cyan]")

    # Extract
    console.print("[yellow]  提取數據...[/yellow]")
    extracted = extract_data.remote("database")

    # Transform
    console.print("[yellow]  轉換數據...[/yellow]")
    transformed = transform_data.remote(extracted)

    # Load
    console.print("[yellow]  加載數據...[/yellow]")
    loaded = load_data.remote(transformed, "warehouse")

    console.print(f"[green]ETL 完成: {loaded}[/green]")

    console.print("\n" + "="*60)
    console.print("[bold green]✓ 數據處理示例完成！[/bold green]")


def print_data_processing_guide():
    """打印數據處理指南"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]數據處理最佳實踐:[/bold cyan]")
    console.print("""
[green]1. 並行處理大型數據集:[/green]

# 分塊處理
chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

# 並行處理
results = list(process_chunk.map(chunks))

# 合併結果
final_result = combine(results)

[green]2. ETL 管道:[/green]

# Extract
data = extract_data.remote(source)

# Transform
transformed = transform_data.remote(data)

# Load
load_data.remote(transformed, destination)

[green]3. 錯誤處理:[/green]

@app.function(retries=3)
def robust_processing(data):
    try:
        return process(data)
    except Exception as e:
        log_error(e)
        raise

[yellow]性能優化:[/yellow]

✓ 使用 map() 並行處理
✓ 合理設置 chunk_size
✓ 使用 pandas 向量化操作
✓ 避免不必要的數據複製
✓ 使用生成器處理大文件

[yellow]成本優化:[/yellow]

✓ 批量處理減少函數調用
✓ 使用合適的 CPU/內存配置
✓ 設置合理的超時時間
✓ 緩存中間結果
    """)
    console.print("="*60 + "\n")


if __name__ == "__main__":
    print_data_processing_guide()
    console.print("[yellow]運行數據處理示例:[/yellow]")
    console.print("  modal run 07_數據處理.py\n")
