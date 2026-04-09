import re

# 句子拆分正则（增强对问号、感叹号、英文句点的支持）
SENTENCE_RE = re.compile(
    r"""
    # 中文标点 + 可选右引号/括号
    ( [。！？!?；;…]+ (?:[”’」』）】]?) )
    |
    # 英文标点后跟随空格或行结束
    ( (?<=[.!?])\s+ | [.!?]+(?=\s|$) )
    """,
    re.VERBOSE | re.UNICODE,
)


def split_sentences(text: str) -> list[str]:
    """
    句子拆分：适用于 Markdown、咨询问题、中英文混合文本。
    """
    if not text or not text.strip():
        return []

    stripped = text.strip()

    # 先按双换行（段落）粗拆，再在段落内细拆句子
    paragraphs = re.split(r"\n\s*\n+", stripped)

    sentences = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # 如果段落很短或为标题/列表，直接保留为一个单元
        if len(para) < 80 or re.match(r"^(###|##|#|-|\*\*|\d+\.)", para):
            sentences.append(para)
            continue

        # 在段落内进行句子拆分
        parts = SENTENCE_RE.split(para)
        current = ""
        for part in parts:
            if part is None:
                continue
            part = part.strip()
            if not part:
                continue

            # 如果是标点，附加到当前句子
            if re.match(r"^[。！？!?；;….”’」』）】.?!]+$", part):
                if current:
                    current += part
                    sentences.append(current.strip())
                    current = ""
                continue

            if current:
                sentences.append(current.strip())
            current = part

        if current:
            sentences.append(current.strip())

    # 去除极短无效片段
    cleaned = [s for s in sentences if len(s.strip()) > 3]

    return cleaned if cleaned else [stripped]


# 段落拆分 兼容中英文
PARAGRAPH_RE = re.compile(r"\n\s*\n+")


def split_paragraphs(text: str) -> list[str]:
    """
    将文本拆分为段落列表（保持不变，兼容中英文）。

    拆分逻辑：
    - 以连续换行（至少两个换行，中间可有空格）作为段落边界。
    - 适用于 Markdown、纯文本等格式。
    """
    if not text:
        return []

    raw_paragraphs = PARAGRAPH_RE.split(text)

    paragraphs = [
        paragraph.strip() for paragraph in raw_paragraphs if paragraph.strip()
    ]

    return paragraphs if paragraphs else [text.strip()]


if __name__ == "__main__":
    """
    uv run src/index/spliters.py
    """
    with open("z_using_files/md/test_split2.md", "r", encoding="utf-8") as f:
        sample_text = f.read()

    # ==================== 测试 split_sentences ====================
    print("=== 测试句子拆分 ===")
    sentences = split_sentences(sample_text)
    for i, sentence in enumerate(sentences, 1):
        print(f"句子 {i}: {sentence}")

    print("\n" + "=" * 60 + "\n")

    # ==================== 测试 split_paragraphs ====================
    print("=== 测试段落拆分 ===")
    paragraphs = split_paragraphs(sample_text)
    for i, paragraph in enumerate(paragraphs, 1):
        print(f"段落 {i} ({len(paragraph)} 字符):")
        print(paragraph)
        print("-" * 40)
