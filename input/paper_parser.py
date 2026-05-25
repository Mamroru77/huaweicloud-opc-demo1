import re
import fitz  # PyMuPDF


def parse_pdf(file_path: str) -> str:
    """解析PDF文件，返回完整文本内容"""
    doc = fitz.open(file_path)
    text_parts = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            text_parts.append(text.strip())
    doc.close()
    return "\n\n".join(text_parts)


def parse_txt(file_path: str) -> str:
    """解析TXT文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def _extract_metadata(text: str) -> dict:
    """从论文文本中提取元信息"""
    meta = {}
    # DOI
    doi_match = re.search(r'DOI[: ]?\s*([0-9]+\.[0-9]+/[^\s]+)', text, re.IGNORECASE)
    if doi_match:
        meta["doi"] = doi_match.group(1)

    # 期刊名 (常见模式)
    journal_patterns = [
        r'(CCS Chem\.)', r'(J\.\s*Am\.\s*Chem\.\s*Soc\.)',
        r'(Angew\.\s*Chem\.)', r'(Nat\.\s*Commun\.)',
        r'(Frontiers in [A-Za-z]+)', r'(ACS [A-Za-z]+)',
        r'published in ([A-Za-z\s]+)',
    ]
    for pat in journal_patterns:
        m = re.search(pat, text[:2000])
        if m:
            meta["journal"] = m.group(1).strip()
            break

    # 发表日期
    date_patterns = [
        r'(?:Published|Received).*?(\d{4})',
        r'(\d{4})\s*(?:;|,|\.)',
    ]
    for pat in date_patterns:
        m = re.search(pat, text[:1000])
        if m:
            meta["year"] = m.group(1)
            break

    # 标题 (取第一段非空行)
    lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 10]
    if lines:
        meta["title"] = lines[0][:200]

    return meta


def _extract_abstract(text: str) -> str:
    """提取摘要部分"""
    # 尝试找 Abstract 关键词
    abs_match = re.search(
        r'(?:Abstract|ABSTRACT|摘要)[:\s]*(.*?)(?:\n\n|\n[A-Z][a-z]+\n|Introduction|INTRODUCTION)',
        text, re.DOTALL | re.IGNORECASE
    )
    if abs_match:
        return abs_match.group(1).strip()[:1000]

    # 取前1500个字符作为摘要替代
    return text[:1500]


def parse_paper(file_path: str) -> dict:
    """统一的论文解析入口，根据文件类型自动选择解析器"""
    if file_path.lower().endswith(".pdf"):
        content = parse_pdf(file_path)
        file_type = "pdf"
    elif file_path.lower().endswith(".txt"):
        content = parse_txt(file_path)
        file_type = "txt"
    else:
        raise ValueError(f"不支持的文件格式: {file_path}")

    # 元信息提取
    metadata = _extract_metadata(content)
    abstract = _extract_abstract(content)

    # 截断策略优化: 保留前35000字符，确保LLM获取足够信息
    max_chars = 35000
    truncated = content[:max_chars] if len(content) > max_chars else content

    return {
        "file_type": file_type,
        "full_text": content,
        "processed_text": truncated,
        "word_count": len(content),
        "metadata": metadata,
        "abstract": abstract,
    }
