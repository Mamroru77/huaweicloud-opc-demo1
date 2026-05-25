import json
import re


def extract_json(text: str) -> dict:
    """从LLM返回的文本中鲁棒地提取JSON，支持多种格式"""

    # 策略1: 提取 ```json ... ``` 代码块
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 策略2: 提取第一个完整的 { ... } 对象
    # 使用括号匹配来找到完整的JSON对象
    start = text.find("{")
    if start != -1:
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(text)):
            c = text[i]
            if escape:
                escape = False
                continue
            if c == "\\":
                escape = True
                continue
            if c == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    json_str = text[start:i + 1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        break

    # 策略3: 全都失败了，返回原始输出
    return {"raw_output": text, "parse_error": True}
