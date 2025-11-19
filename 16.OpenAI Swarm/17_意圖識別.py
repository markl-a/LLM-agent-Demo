#!/usr/bin/env python3
"""OpenAI Swarm - 意圖識別"""

class IntentClassifier:
    def classify(self, message: str) -> dict:
        intents = {
            "購買": ["買", "購買", "訂購"],
            "諮詢": ["怎麼", "如何", "是什麼"],
            "投訴": ["問題", "故障", "不滿"]
        }

        for intent, keywords in intents.items():
            if any(k in message for k in keywords):
                return {"intent": intent, "confidence": 0.9}

        return {"intent": "其他", "confidence": 0.5}

classifier = IntentClassifier()
msgs = ["我想買手機", "這個怎麼用", "產品有問題"]

for msg in msgs:
    result = classifier.classify(msg)
    print(f"'{msg}' → {result['intent']} ({result['confidence']:.0%})")

print("\n✅ 意圖識別完成")
