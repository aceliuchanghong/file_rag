## step

```
00.md (原始 Markdown 文件)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  1. parsers.py - 解析阶段                                     │
│     └── markdown_to_payload()                               │
│         • HEADING_RE 正则匹配 # 标题                         │
│         • 按空行分割段落                                     │
│         • 调用 text_utils.py 分割句子                       │
│         • 输出: DocumentPayload                             │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  2. types.py - 数据结构定义                                   │
│     DocumentPayload                                         │
│       └── sections: list[SectionPayload]                    │
│              └── paragraphs: list[ParagraphPayload]         │
│                     └── sentences: list[SentencePayload]    │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  3. indexer.py - 索引构建                                    │
│     DocumentIndexer.index()                                 │
│       ├── _build_tree() → 构建 TreeNode 层次结构            │
│       │     • doc:sec1:p1:s1 层级ID生成                    │
│       │     • DOCUMENT → SECTION → PARAGRAPH → SENTENCE     │
│       │                                                    │
│       └── _embed_tree() → 计算嵌入向量                     │
│             ├── 批量嵌入所有句子 (调用 embeddings.py)       │
│             └── _propagate_embeddings() 向上传播到父节点    │
│                   段落嵌入 = 平均(句子嵌入)                │
│                   章节嵌入 = 平均(段落嵌入)                │
│                   文档嵌入 = 平均(章节嵌入)                │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  4. embeddings.py - 嵌入计算                                │
│     JinaEmbeddingModel / JinaV4EmbeddingModel               │
│       └── embed(texts) → 返回向量列表                       │
│     average_embeddings() → 平均多个嵌入向量                  │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  5. types.py - 转换为存储格式                                │
│     TreeNode → StoredNode                                   │
│       • node_id: "doc:sec1:p1:s1"                          │
│       • parent_id: 父节点引用                               │
│       • kind: NodeKind (DOCUMENT/SECTION/PARAGRAPH/SENTENCE)│
│       • embedding: np.ndarray                              │
│       • child_ids: 子节点ID列表                             │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  6. datastore.py - 持久化存储                                │
│     KVaultNodeStore.upsert_nodes(nodes)                    │
│       • SQLite 存储节点元数据                               │
│       • sqlite-vec 存储向量嵌入                              │
└─────────────────────────────────────────────────────────────┘
```

```
文件	职责	主要函数/类
parsers.py	Markdown → 结构化数据	markdown_to_payload()
text_utils.py	文本分割	split_paragraphs(), split_sentences()
types.py	数据结构定义	DocumentPayload, TreeNode, StoredNode
indexer.py	层次索引构建	DocumentIndexer._build_tree(), _embed_tree()
embeddings.py	向量嵌入	JinaEmbeddingModel.embed()
datastore.py	SQLite 存储	KVaultNodeStore.upsert_nodes()
```