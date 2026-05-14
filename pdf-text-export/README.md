# PDF Text Export

一套可在 GitHub Actions 里运行的 PDF 转文本方案，优先读取文字层，失败时自动走 OCR。

## 目标

- 兼顾无密码 PDF
- 兼顾“可正常打开，但某些工具提示有密码/禁止复制”的 PDF
- 支持显式密码 PDF
- 文字层提取失败时，允许 OCR 兜底
- 输出 `md` 和 `txt`

## 原理

1. 先用 `pypdf` 读取文字层
2. 如果失败，再用 `PyMuPDF` 读取文字层
3. 如果整份文档文字太少，或者根本打不开文字层，再用 `tesseract` OCR

说明：

- 很多保单 PDF 并不是“必须输入打开密码”的强加密，而是设置了权限限制，比如防复制、防编辑。
- 这类文件经常会导致部分工具直接报“有密码”，但系统 PDF 引擎或兼容性更好的库仍然能读到文字层。
- 这套方案先尝试空密码，再尝试配置密码，因此能兼顾这两类情况。

## 目录

- `.github/workflows/pdf-to-text.yml`
- `pdf-text-export/scripts/pdf_to_text.py`
- `pdf-text-export/requirements.txt`

## GitHub Actions 用法

1. 在 GitHub Actions 手动运行 `PDF To Text`
2. 可以任选一种输入方式：

- 方式 A：把 PDF 放到仓库里的某个目录，例如 `input/`
- 方式 B：在 `pdf_urls` 输入框里填写一个或多个 PDF URL，每行一个

3. 可选：在仓库 `Secrets and variables -> Actions` 里配置以下 secret

- `PDF_PASSWORD`
  用于所有 PDF 的默认密码

- `PDF_PASSWORD_MAP_JSON`
  用于按文件名单独配置密码，内容是 JSON，例如：

```json
{
  "a.pdf": "123456",
  "b": "owner-password",
  "input/c.pdf": "secret"
}
```

匹配键支持：

- 完整路径，例如 `input/c.pdf`
- 文件名，例如 `a.pdf`
- 文件 stem，例如 `b`

4. Workflow 运行时会：

- 先打印本次下载/扫描到的 PDF 文件清单
- 转换为 `md` 和 `txt`
- 生成 `conversion-summary.md`
- 在 Job Summary 中展示本次处理历史
- 上传 `pdf-text-output` artifact 供下载

默认输入：

- `input_dir`: `input`
- `pdf_urls`: 空
- `output_dir`: `output`
- `pdf_glob`: `**/*.pdf`
- `enable_ocr`: `true`
- `ocr_languages`: `chi_sim+eng`

5. 运行结束后，从 artifact `pdf-text-output` 下载结果

## URL 输入示例

在 `pdf_urls` 里填：

```text
https://example.com/a.pdf
https://example.com/b.pdf
```

如果这些 URL 需要鉴权，建议先把文件放到仓库里，或者改成你自己可访问的临时下载链接。

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r pdf-text-export/requirements.txt
python pdf-text-export/scripts/pdf_to_text.py --input-dir input --output-dir output --ocr
```

通过 URL 下载后再转换：

```bash
python pdf-text-export/scripts/pdf_to_text.py \
  --input-dir input \
  --output-dir output \
  --pdf-urls $'https://example.com/a.pdf\nhttps://example.com/b.pdf' \
  --summary-file output/conversion-summary.md \
  --ocr
```

如果你有密码：

```bash
export PDF_PASSWORD='123456'
python pdf-text-export/scripts/pdf_to_text.py --input-dir input --output-dir output --ocr
```

或者：

```bash
python pdf-text-export/scripts/pdf_to_text.py \
  --input-dir input \
  --output-dir output \
  --password-file passwords.json \
  --ocr
```

## 失败兜底策略

- `pypdf` 失败：切到 `PyMuPDF`
- 文字层很少：保留已有可读页面，对低质量页面补 OCR
- 整份文档都拿不到文字层：整份 OCR

## 输出格式

每个 PDF 生成：

- `文件名.md`
- `文件名.txt`
- `conversion-summary.md`（整批任务汇总）

Markdown 按页分段：

```md
## Page 1
...
```

纯文本按页分隔：

```txt
===== Page 1 =====
...
```

## 适用边界

这套方案适合：

- 保单
- 合同
- 有文字层的电子 PDF
- 扫描件 PDF

如果 PDF 属于真正的强加密文件，并且既没有空密码也没有正确密码，那么只能走“先解锁再抽取”或纯截图 OCR 的路线；本方案不会尝试破解密码。
