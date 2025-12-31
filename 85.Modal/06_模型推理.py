"""
Modal 模型推理示例

本示例展示：
1. 部署機器學習模型
2. 文本生成 API
3. 圖像分類
4. 批量推理優化
"""

import modal
from rich.console import Console
from rich.panel import Panel

console = Console()

# 創建應用
app = modal.App("model-inference")

# 定義模型鏡像
model_image = modal.Image.debian_slim().pip_install(
    "torch>=2.0.0",
    "transformers>=4.30.0",
    "pillow",
    "numpy"
)


# 示例 1: 文本分類模型
@app.cls(
    gpu="T4",
    image=model_image,
    container_idle_timeout=300  # 5 分鐘後停止容器
)
class TextClassifier:
    """文本分類模型服務"""

    def __enter__(self):
        """容器啟動時加載模型（只執行一次）"""
        from transformers import pipeline

        print("加載文本分類模型...")
        self.classifier = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=0  # 使用 GPU
        )
        print("模型加載完成！")

    @modal.method()
    def classify(self, text: str) -> dict:
        """分類單個文本"""
        print(f"分類: {text}")
        result = self.classifier(text)[0]
        return {
            "text": text,
            "label": result["label"],
            "score": float(result["score"])
        }

    @modal.method()
    def classify_batch(self, texts: list) -> list:
        """批量分類"""
        print(f"批量分類 {len(texts)} 個文本")
        results = self.classifier(texts)
        return [
            {
                "text": text,
                "label": r["label"],
                "score": float(r["score"])
            }
            for text, r in zip(texts, results)
        ]


# 示例 2: 文本生成模型
@app.cls(
    gpu="T4",
    image=model_image,
    container_idle_timeout=300
)
class TextGenerator:
    """文本生成模型服務"""

    def __enter__(self):
        """加載生成模型"""
        from transformers import pipeline

        print("加載文本生成模型...")
        self.generator = pipeline(
            "text-generation",
            model="gpt2",
            device=0
        )
        print("生成模型加載完成！")

    @modal.method()
    def generate(self, prompt: str, max_length: int = 50) -> dict:
        """生成文本"""
        print(f"生成文本，提示: {prompt}")

        results = self.generator(
            prompt,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7
        )

        generated_text = results[0]["generated_text"]

        return {
            "prompt": prompt,
            "generated": generated_text,
            "length": len(generated_text)
        }


# 示例 3: 圖像分類模型
@app.cls(
    gpu="T4",
    image=model_image,
    container_idle_timeout=300
)
class ImageClassifier:
    """圖像分類模型服務"""

    def __enter__(self):
        """加載圖像分類模型"""
        from transformers import pipeline

        print("加載圖像分類模型...")
        self.classifier = pipeline(
            "image-classification",
            model="google/vit-base-patch16-224"
        )
        print("圖像模型加載完成！")

    @modal.method()
    def classify_url(self, image_url: str) -> list:
        """分類網絡圖像"""
        from PIL import Image
        import requests
        from io import BytesIO

        print(f"下載圖像: {image_url}")
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))

        print("分類圖像...")
        results = self.classifier(image)

        return [
            {
                "label": r["label"],
                "score": float(r["score"])
            }
            for r in results[:5]  # 返回前 5 個結果
        ]

    @modal.method()
    def classify_base64(self, image_base64: str) -> list:
        """分類 Base64 編碼的圖像"""
        from PIL import Image
        import base64
        from io import BytesIO

        print("解碼 Base64 圖像...")
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))

        print("分類圖像...")
        results = self.classifier(image)

        return [
            {
                "label": r["label"],
                "score": float(r["score"])
            }
            for r in results[:5]
        ]


# 示例 4: 將模型服務暴露為 Web API
@app.function(image=model_image)
@modal.web_endpoint(method="POST")
def text_classification_api(request: dict):
    """
    文本分類 Web API

    POST /text_classification_api
    {
        "text": "I love this movie!"
    }
    """
    text = request.get("text", "")

    if not text:
        return {"error": "text is required"}, 400

    # 調用分類器
    classifier = TextClassifier()
    result = classifier.classify.remote(text)

    return result


@app.function(image=model_image)
@modal.web_endpoint(method="POST")
def text_generation_api(request: dict):
    """
    文本生成 Web API

    POST /text_generation_api
    {
        "prompt": "Once upon a time",
        "max_length": 100
    }
    """
    prompt = request.get("prompt", "")
    max_length = request.get("max_length", 50)

    if not prompt:
        return {"error": "prompt is required"}, 400

    # 調用生成器
    generator = TextGenerator()
    result = generator.generate.remote(prompt, max_length)

    return result


# 示例 5: 批量推理 API
@app.function(image=model_image)
@modal.web_endpoint(method="POST")
def batch_classification_api(request: dict):
    """
    批量文本分類 API

    POST /batch_classification_api
    {
        "texts": ["text1", "text2", "text3"]
    }
    """
    texts = request.get("texts", [])

    if not texts or not isinstance(texts, list):
        return {"error": "texts must be a non-empty list"}, 400

    # 批量分類
    classifier = TextClassifier()
    results = classifier.classify_batch.remote(texts)

    return {
        "count": len(texts),
        "results": results
    }


@app.local_entrypoint()
def main():
    """本地測試"""
    console.print(Panel.fit(
        "[bold cyan]Modal 模型推理示例[/bold cyan]\n"
        "[dim]部署機器學習模型 API[/dim]",
        border_style="cyan"
    ))

    # 測試文本分類
    console.print("\n[cyan]1. 測試文本分類[/cyan]")
    classifier = TextClassifier()

    text = "This is an amazing product! I love it!"
    result = classifier.classify.remote(text)
    console.print(f"[green]結果: {result}[/green]")

    # 測試批量分類
    console.print("\n[cyan]2. 測試批量分類[/cyan]")
    texts = [
        "I love this!",
        "This is terrible.",
        "It's okay, I guess."
    ]
    results = classifier.classify_batch.remote(texts)
    for r in results:
        console.print(f"[green]  {r}[/green]")

    # 測試文本生成
    console.print("\n[cyan]3. 測試文本生成[/cyan]")
    generator = TextGenerator()

    prompt = "Artificial intelligence is"
    result = generator.generate.remote(prompt, max_length=50)
    console.print(f"[green]生成: {result['generated']}[/green]")

    console.print("\n" + "="*60)
    console.print("[bold green]✓ 模型推理測試完成！[/bold green]")


def print_model_deployment_guide():
    """打印模型部署指南"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]模型部署指南:[/bold cyan]")
    console.print("""
[green]1. 使用 Class 部署模型:[/green]

@app.cls(gpu="T4", image=model_image)
class MyModel:
    def __enter__(self):
        # 加載模型（只執行一次）
        self.model = load_model()

    @modal.method()
    def predict(self, x):
        return self.model(x)

優點:
✓ 模型只加載一次（__enter__）
✓ 容器保持溫暖（避免冷啟動）
✓ 支持批量推理

[green]2. 部署為 Web API:[/green]

@app.function()
@modal.web_endpoint(method="POST")
def api(request: dict):
    model = MyModel()
    return model.predict.remote(request["input"])

[green]3. 批量推理優化:[/green]

# 使用 Class 的 batch 方法
@modal.method()
def predict_batch(self, inputs: list):
    return self.model(inputs)

# 調用
results = model.predict_batch.remote(batch_inputs)

[yellow]成本優化:[/yellow]

✓ 使用合適的 GPU（T4 用於推理）
✓ 設置 container_idle_timeout 自動停止
✓ 批量處理提升吞吐量
✓ 使用模型量化（FP16）
✓ 緩存常用結果

[yellow]性能優化:[/yellow]

✓ 預加載模型到 GPU
✓ 使用批量推理
✓ 啟用 TorchScript/ONNX
✓ 合理設置 batch_size
✓ 使用 GPU 加速
    """)
    console.print("="*60 + "\n")


if __name__ == "__main__":
    print_model_deployment_guide()
    console.print("[yellow]運行測試:[/yellow]")
    console.print("  modal run 06_模型推理.py\n")
    console.print("[yellow]部署為 API:[/yellow]")
    console.print("  modal deploy 06_模型推理.py\n")
