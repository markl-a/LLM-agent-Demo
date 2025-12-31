#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenLLM 自定義模型示例
====================

本示例展示如何添加和使用自定義模型，包括：
1. 註冊自定義模型
2. 配置模型參數
3. Fine-tuned 模型使用
4. 自定義提示模板
5. 模型適配器

適用場景：
- 使用私有或未內置的模型
- 加載 fine-tuned 模型
- 自定義模型配置
"""

import sys
from typing import Dict, Any, Optional


def register_custom_model():
    """
    註冊自定義模型

    展示如何註冊 OpenLLM 未內置的模型
    """
    print("=" * 80)
    print("示例 1: 註冊自定義模型")
    print("=" * 80)

    print("\n📝 註冊自定義模型配置：")
    print("-" * 80)

    registration_code = '''
import openllm
from openllm import LLMConfig

# 定義自定義模型配置
@openllm.model_config()
class CustomModelConfig(LLMConfig):
    """自定義模型配置"""

    # 模型基本信息
    model_name = "custom-model"
    model_type = "causal_lm"  # 或 "seq2seq_lm"

    # 默認生成參數
    default_max_new_tokens = 256
    default_temperature = 0.7
    default_top_p = 0.95
    default_top_k = 50

    # 模型特定配置
    trust_remote_code = True
    use_fast_tokenizer = True

    # 停止序列
    default_stop_sequences = ["<|endoftext|>", "</s>"]

# 註冊模型
@openllm.model(
    config=CustomModelConfig,
    model_id="your-org/your-custom-model"
)
class CustomModel:
    """自定義模型類"""

    def load_model(self, model_id, **kwargs):
        """加載模型邏輯"""
        from transformers import AutoModelForCausalLM, AutoTokenizer

        # 加載 tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True,
        )

        # 加載模型
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            **kwargs
        )

        return model, tokenizer

    def generate(self, prompt, **kwargs):
        """生成文本"""
        # 實現生成邏輯
        pass

# 使用自定義模型
llm = openllm.LLM(
    "custom-model",
    model_id="your-org/your-custom-model"
)

result = llm("Your prompt here")
print(result)
'''

    print(registration_code)


def use_finetuned_model():
    """
    使用 Fine-tuned 模型

    展示如何加載和使用微調後的模型
    """
    print("\n" + "=" * 80)
    print("示例 2: 使用 Fine-tuned 模型")
    print("=" * 80)

    print("\n📝 加載 Fine-tuned Llama 模型：")
    print("-" * 80)

    finetuned_code = '''
import openllm

# 方式 1: 從 HuggingFace Hub 加載
llm = openllm.LLM(
    "llama",
    model_id="your-username/llama-2-7b-finetuned",
    trust_remote_code=True,
)

# 方式 2: 從本地路徑加載
llm = openllm.LLM(
    "llama",
    model_id="/path/to/local/finetuned-model",
)

# 使用模型
prompt = "Your domain-specific prompt"
result = llm(prompt, max_new_tokens=200)
print(result)
'''

    print(finetuned_code)

    print("\n加載 LoRA 適配器：")
    print("-" * 80)

    lora_code = '''
import openllm

# 使用 LoRA 適配器
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-hf",  # 基礎模型
    adapter_id="your-username/llama-2-7b-lora",  # LoRA 適配器
    adapter_type="lora",
)

# 或使用多個 LoRA 適配器
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-hf",
    adapters=[
        {"id": "adapter1", "type": "lora"},
        {"id": "adapter2", "type": "lora"},
    ],
)
'''

    print(lora_code)

    print("\nCLI 使用 Fine-tuned 模型：")
    print("-" * 80)

    cli_code = '''
# 從 HuggingFace 加載
openllm start llama \\
  --model-id your-username/llama-2-7b-finetuned \\
  --trust-remote-code

# 從本地加載
openllm start llama \\
  --model-id /path/to/finetuned-model

# 使用 LoRA 適配器
openllm start llama \\
  --model-id meta-llama/Llama-2-7b-hf \\
  --adapter-id your-username/llama-2-7b-lora
'''

    print(cli_code)


def custom_prompt_template():
    """
    自定義提示模板

    展示如何為模型配置自定義提示模板
    """
    print("\n" + "=" * 80)
    print("示例 3: 自定義提示模板")
    print("=" * 80)

    print("\n📝 定義提示模板：")
    print("-" * 80)

    template_code = '''
import openllm
from openllm import PromptTemplate

# 定義聊天模板
chat_template = PromptTemplate(
    template="""<|system|>
{system_message}
<|user|>
{user_message}
<|assistant|>
""",
    input_variables=["system_message", "user_message"],
)

# 定義指令模板
instruction_template = PromptTemplate(
    template="""### Instruction:
{instruction}

### Input:
{input}

### Response:
""",
    input_variables=["instruction", "input"],
)

# 使用模板
llm = openllm.LLM("llama", model_id="meta-llama/Llama-2-7b-chat-hf")

# 應用模板
prompt = chat_template.format(
    system_message="You are a helpful assistant.",
    user_message="What is machine learning?"
)

result = llm(prompt, max_new_tokens=200)
print(result)
'''

    print(template_code)

    print("\n常見提示模板：")
    print("-" * 80)

    templates = {
        "Llama 2 Chat": """[INST] <<SYS>>
{system_message}
<</SYS>>

{user_message} [/INST]""",

        "Mistral Instruct": """<s>[INST] {instruction} [/INST]""",

        "Alpaca": """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:""",

        "Vicuna": """A chat between a curious user and an artificial intelligence assistant.

USER: {user_message}
ASSISTANT:""",
    }

    for name, template in templates.items():
        print(f"\n{name}:")
        print(template)
        print()


def model_configuration():
    """
    模型配置

    展示詳細的模型配置選項
    """
    print("\n" + "=" * 80)
    print("示例 4: 詳細模型配置")
    print("=" * 80)

    print("\n📝 完整配置示例：")
    print("-" * 80)

    config_code = '''
import openllm
from transformers import GenerationConfig

# 創建生成配置
generation_config = GenerationConfig(
    max_new_tokens=256,
    temperature=0.7,
    top_p=0.95,
    top_k=50,
    repetition_penalty=1.1,
    do_sample=True,
    num_return_sequences=1,
    pad_token_id=0,
    eos_token_id=2,
    bos_token_id=1,
)

# 加載模型並應用配置
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-chat-hf",

    # 加載配置
    torch_dtype="float16",
    device_map="auto",
    load_in_8bit=False,

    # 生成配置
    generation_config=generation_config,

    # Tokenizer 配置
    tokenizer_config={
        "padding_side": "left",
        "truncation_side": "left",
        "max_length": 4096,
    },

    # 安全選項
    trust_remote_code=True,
)

# 使用配置
result = llm("Your prompt", max_new_tokens=200)
print(result)
'''

    print(config_code)

    print("\nYAML 配置文件：")
    print("-" * 80)

    yaml_config = '''
# model_config.yaml
model_name: custom-llama
model_id: your-org/your-llama-model

# 加載配置
model_config:
  torch_dtype: float16
  device_map: auto
  trust_remote_code: true

# 生成配置
generation_config:
  max_new_tokens: 256
  temperature: 0.7
  top_p: 0.95
  top_k: 50
  repetition_penalty: 1.1
  do_sample: true

# Tokenizer 配置
tokenizer_config:
  padding_side: left
  max_length: 4096

# 提示模板
prompt_template: |
  [INST] {prompt} [/INST]
'''

    print(yaml_config)


def model_adapter():
    """
    模型適配器

    展示如何使用和切換模型適配器
    """
    print("\n" + "=" * 80)
    print("示例 5: 模型適配器")
    print("=" * 80)

    print("\n📝 使用 PEFT 適配器：")
    print("-" * 80)

    peft_code = '''
import openllm
from peft import PeftConfig, PeftModel

# 方式 1: OpenLLM 內置支持
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-hf",
    adapter_id="your-username/llama-2-7b-peft",
    adapter_type="peft",  # 或 "lora", "prefix_tuning"
)

# 方式 2: 手動加載 PEFT
base_model_id = "meta-llama/Llama-2-7b-hf"
adapter_id = "your-username/llama-2-7b-lora"

# 加載配置
peft_config = PeftConfig.from_pretrained(adapter_id)

# 使用適配器
llm = openllm.LLM(
    "llama",
    model_id=base_model_id,
    peft_config=peft_config,
)
'''

    print(peft_code)

    print("\n動態切換適配器：")
    print("-" * 80)

    dynamic_adapter_code = '''
import openllm

# 加載基礎模型
llm = openllm.LLM(
    "llama",
    model_id="meta-llama/Llama-2-7b-hf",
)

# 添加適配器
llm.load_adapter("adapter1", adapter_id="user/adapter1")
llm.load_adapter("adapter2", adapter_id="user/adapter2")

# 使用適配器 1
llm.set_adapter("adapter1")
result1 = llm("Prompt for adapter 1")

# 切換到適配器 2
llm.set_adapter("adapter2")
result2 = llm("Prompt for adapter 2")

# 卸載適配器
llm.unload_adapter("adapter1")
'''

    print(dynamic_adapter_code)


def main():
    """
    主函數：運行所有示例
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "OpenLLM 自定義模型示例" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # 示例 1: 註冊自定義模型
        register_custom_model()

        # 示例 2: Fine-tuned 模型
        use_finetuned_model()

        # 示例 3: 提示模板
        custom_prompt_template()

        # 示例 4: 模型配置
        model_configuration()

        # 示例 5: 適配器
        model_adapter()

        print("\n" + "=" * 80)
        print("✓ 所有示例展示完成！")
        print("=" * 80)
        print("\n💡 關鍵要點：")
        print("   1. OpenLLM 支持自定義模型註冊")
        print("   2. 可以輕鬆使用 fine-tuned 模型")
        print("   3. 提示模板提高模型效果")
        print("   4. PEFT 適配器支持靈活微調")
        print()

    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 運行出錯: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
