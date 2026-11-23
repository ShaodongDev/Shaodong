# 博客发表指南

适用于本仓库的文章导入、整理和发布。执行前先读本文件，并以用户当前要求为准。

## 必须遵守的内容边界

- 保留作者原文、标题、段落顺序、强调、列表和原有配图位置。发表不等于改写：未经要求，不润色正文、不补充观点或脚注。
- **不要擅自给配图添加标题、图注、可见说明或图片内文字。** 原文明确有的图注按原文保留，没有的就不新增。导出包中的图片文件名和 UUID 不属于作者图注。
- 不擅自换图、生成新图或增加装饰图。已有配图优先使用原文件，保留原始文件内容。
- 元数据补充放在 front matter 或 `data/seo.json`，不要把 SEO 文案加进正文。
- 新文章发布前，必须向用户展示推荐标签，询问是否采用、删改或补充，并等待答复；优先复用已有标签。具体规则见第 6 节。
- 保留已有文章的 URL、发表日期和资源路径，不为发表新文章调整全站模板或样式。

## 网站和发布渠道

- 本站是 Hugo 博客，主题为 `TeXtLite`，正式域名为 `https://zhangshaodong.com/`。
- GitHub 仓库现地址：`https://github.com/ShaodongDev/Shaodong`。本机 `origin` 可能仍指向旧地址 `Cyan-ZSD/Shaodong`，GitHub 会重定向；不要因此擅自修改 remote。
- Cloudflare Pages 项目名为 `blog`，默认地址为 `blog-8hy.pages.dev`，生产分支为 `main`。
- **正常发表流程是提交并推送 `main`，由 Cloudflare 自动构建部署。** 构建命令为 `hugo --gc --minify`，产物目录为 `public`。不要另外创建站点、迁移托管或重复手动部署。
- 本地使用与生产一致的 Hugo **0.120.4 extended**。`build.sh` 中的旧版注释不是当前版本依据。

## 1. 检查工作区和原稿

1. 执行 `git status --short --branch`、`git remote -v`、`git log -5 --oneline`，确认当前分支与已有改动。
2. 找到用户指定的导出目录，阅读完整 Markdown，核对所有图片和其他附件；先看原图，再决定文件名和引用方式。
3. 参考最近文章的 `index.md` 和 `data/seo.json`，不要仅凭导出包文件名判断文章标题或日期。
4. 发布前联网核对远程 `main`。如存在新提交，先保留本地工作并处理分支差异，不强制推送。
5. 不覆盖或顺手提交用户已有改动，不删除原始导出包。

## 2. 整理文章目录

每篇文章使用一个 Hugo page bundle，放在 `content/post/` 下：

```text
content/post/<english-slug>/
  index.md
  assets/
    images/
      descriptive-image-name.png
```

- 目录名使用简短、能表达文章主题的英文 slug，通常为小写单词加连字符。
- 图片与文章一起放在该 bundle 的 `assets/images/`，不要把文章配图散放在仓库根目录或全站 `static/`。
- 可以将导出的 UUID 图片名改成有意义的英文文件名，但要同步更新所有引用；复制原文件，不重新压缩覆盖原图。
- 导出 Markdown 开头若有与文章标题重复的一级标题，将它移入 front matter，正文不再重复显示一次标题。除此之外不擅自编辑正文。
- 排除 `.DS_Store` 等导出附带文件。

front matter 沿用以下格式，替换标题、日期和标签：

```yaml
---
title: '文章原题'
author: Shaodong
date: 'YYYY-MM-DDT00:00:00+09:00'
slug: ''
categories: []
tags:
  - 中文
  - 相关主题
draft: false
disqus: true
---
```

用户指定的日期优先；没有指定日期的新发表文章，使用用户当前时区的当天日期。当前用户时区为 `Asia/Tokyo`，故示例使用 `+09:00`。显式带时区，避免日本时间早上发表时被 Hugo 当作尚未到来的 UTC 日期而排除。不要靠 `--buildFuture` 强行发布。

URL 规则在 `config.yaml` 中为 `/:year/:month/:day/:filename/`。例如目录 `underlying-logic` 配合 2026-11-23 的日期，生成 `/2026/11/23/underlying-logic/`。确定日期和目录后，核对实际构建 URL。

## 3. 配图：不要新增可见图注

**这里有一个容易踩的坑：** `themes/TeXtLite/layouts/_default/_markup/render-image.html` 会将 Markdown 图片的非空替代文本 `.Text` 同时渲染成 `<figcaption>`。因此 `![自己写的描述](...)` 会在正文中新增可见说明，不能当作纯技术性 alt 补充。

对于原文没有明确图注的配图，正文使用：

```markdown
![](./assets/images/descriptive-image-name.png)
```

不要自行填充方括号里的文字，也不要添加 Markdown 图片 title、`<figcaption>` 或图下说明段落。

无障碍替代文本通过 `data/seo.json` 中该文章的 `image_alt` 提供，键为 bundle 内相对路径，不带 `./`。现有 `layouts/partials/content/images.html` 会为最终 `<img>` 填充 alt，**不会据此生成可见图注**。这样既可通过图片检查，也不改变正文的可见内容。

Hugo 已经会根据 bundle 资源生成不同宽度的 WebP，并保留常规图片 fallback、尺寸和加载策略；无需手工添加一套压缩图或修改全站图片模板。RSS 使用绝对地址的常规图片，不使用懒加载。

## 4. 补充 SEO 和分享预览

在 `data/seo.json` 中新增一项，键必须是文章的最终 URL 路径，包含结尾 `/`：

```json
"/2026/11/23/underlying-logic/": {
  "lang": "zh-CN",
  "description": "忠实概括本文主题的简短介绍，不添加原文没有的判断。",
  "images": [
    "assets/images/descriptive-image-name.png"
  ],
  "image_alt": {
    "assets/images/descriptive-image-name.png": "简洁准确的图片替代文本，仅用于无障碍属性。"
  }
}
```

示例的 URL 和文件名必须替换成当前文章的真实值。`images` 用于分享预览，选择文章已有的合适配图；无配图的文章不必强行添加图片字段。为每张需要补充 alt 的图提供对应 `image_alt`。英文文章的语言值使用 `en`。

## 5. 构建与验证

优先使用已安装的 Hugo 0.120.4 extended。当前机器已知可执行文件为：

```text
/Users/cyan/Library/Application Support/Hugo/0.120.4/hugo
```

本地验证示例：

```sh
hugo_bin='/Users/cyan/Library/Application Support/Hugo/0.120.4/hugo'
"$hugo_bin" version
task_build_dir="$(mktemp -d /tmp/shaodong-publish.XXXXXX)"
HUGO_RESOURCEDIR="$task_build_dir/resources" \
  "$hugo_bin" --minify --destination "$task_build_dir/public"
python3 tests/verify-build.py "$task_build_dir/public"
git diff --check
```

在其他机器先定位正确版本的 Hugo，再调整 `hugo_bin`。资源目录用环境变量 `HUGO_RESOURCEDIR` 指定，**0.120.4 不支持 `--resourceDir` 命令行参数**。构建产物和验证报告放在临时目录或 gitignored 的 `reports/` 中。

检查以下结果：

- 新文章的实际 HTML 存在；标题、作者、语言、日期、canonical、SEO 与分享图片正确。
- 原文与导入后的正文一致，所有资源引用有效，原图文件内容一致。
- 正文配图有有效的 alt、尺寸和响应式资源；原文没有图注的图片没有新增 `<figure>` / `<figcaption>` 或其他可见说明。
- `/post/` 出现新文章且顺序符合日期；标签页面可访问。
- `/feed.xml` 和 `/sitemap.xml` 包含新文章；RSS 图像为可访问的绝对 URL。
- RSS 也包含原有的 About 页面，**不要假设 RSS item 数量等于文章数量**；比较 GUID、标题和发表日期。
- 有浏览器工具时，检查手机和桌面宽度下图片加载与横向溢出；验证后关闭临时预览服务。

更多检查说明见 `tests/README.md`。新增文章会改变 URL 集合和 RSS item 集合，不能直接用当前要求集合完全相等的 `--baseline` 检查；需要时对比旧文章交集，确保旧正文、URL、日期和原资源保留。域名重定向代码有变动时才额外运行 `node --test cloudflare/domain-redirects/index.test.mjs`。

## 6. 发布前确认标签

新文章发表，或 agent 主动建议调整标签时，按以下步骤执行：

1. 先查看 `content/post/` 中已有文章的 `tags`，了解现有标签及其用法，再结合全文推荐。优先复用贴切的已有标签，例如“概念”“系统”，不要遗漏跨文章共用的主题，也不要为凑标签使用不相关的词。
2. 给出一组精简的推荐标签，简要说明主题标签的选择理由。区分“复用已有标签”和“拟新增标签”；新增标签应有必要，避免制造同义词或大小写变体。原稿中的标签也要一并展示，不能默认用户接受 agent 的新增推荐。
3. 先完成可独立推进的文章整理、配图处理、SEO 和本地预览检查，再向用户一次性展示完整候选方案，例如：

   > 建议复用已有标签：中文、概念、系统。
   > 建议新增标签：……（没有则省略）。
   > 这些标签是否采用？有没有需要删除、替换或补充的标签？

4. **等待用户明确答复后再发布。** 可以用候选标签做本地准备和验证，但不能将推荐或用户未回复视作确认，也不能在确认前推送 `main` 或触发生产部署。等待期间继续完成不依赖答复的工作。
5. 根据用户答复确定 front matter 中的最终 `tags`，核对文章标签、对应标签页面和文章列表过滤；如果答复改变了候选方案，重新运行受影响的检查。
6. 用户已明确指定本篇文章的最终标签、确认过本次方案，或明确授权 agent 自行决定标签时，按已有授权执行，不重复询问。例如用户要求“加上已有的概念和系统”，直接添加这两个标签。已有文章仅做不涉及标签的修正时，不额外发起标签确认。

“发表 / publish / 上线”本身不代表用户已接受 agent 推荐的标签。确认问题聚焦标签选择，不扩大为正文改写、补充观点或脚注的授权。

## 7. 提交、发布和核验

用户明确要求“发表 / publish / 上线”时，完成上述检查及适用的标签确认后，继续提交和推送，不再重复询问是否发布。仅要求整理、预览或写文档时，不因此推送生产分支。

1. 检查 diff，只暂存本次文章的 `index.md`、原图及附件和对应 `data/seo.json` 改动，不使用 `git add .`。原始导出目录、缓存和报告不提交。
2. 执行 `git diff --cached --check`，查看暂存文件和 diff，确认没有新增图注或夹带其他修改。
3. 提交清楚描述文章的 commit，例如 `Publish underlying-logic essay with original illustration`。
4. 执行 `git push origin main`，不使用 force push。
5. 等待 Cloudflare 对**这次 commit SHA** 的生产部署成功。可用已安装的 Wrangler 或已有工具查询，例如：

   ```sh
   npx wrangler pages deployment list --project-name blog --environment production --json
   ```

   `Source` 应对应这次 commit，`Environment` 为生产；不要把旧部署成功当作此次成功。自动部署尚未结束时继续观察，不重复触发手动部署。账号和项目也可从本地 `.wrangler/cache/pages.json` 核对；不要将凭据写入仓库或日志。

6. 在正式域名上验证文章返回 200、正文正确、原图和生成的响应式图片可访问，以及文章列表、RSS、站点地图已更新。仅本地构建通过或 `git push` 成功，不等于已完成上线。
7. 如用脚本请求正式站，使用明确的 User-Agent，例如 `Shaodong-blog-publication-check/1.0`；默认 Python urllib 请求可能被站点防护返回 403。
8. 最后向用户提供正式文章链接，简述文件目录、配图处理和验证结果；如有未完成步骤，明确说明，不声称已发布成功。
