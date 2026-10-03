# 每日精选

站点：https://zhangypsam.github.io/daily-report/

每天北京时间 08:00，由本机 Codex 定时任务读取 Horizon 当前配置、采集最近 24 小时消息，核验并生成中文日报。主题：AI 工具、AI 热门新闻、AI 变现、黄金投资资讯、国际政治、财经新闻。每类最多 5 条，总上限为 5 × 主题数，不凑数。

Codex 将报告写入 `docs/_posts/YYYY-MM-DD-summary-zh.md` 并推送本仓库。GitHub Actions 用 Horizon 原有的 Jekyll 站点方式构建并发布 GitHub Pages；发布成功后，本机 Codex 通过 Server酱 Turbo 发送微信通知和日报链接。每日 UTC 00:00 的计划任务只重新发布已有内容，不生成新闻，不推送旧日报。

## 运行条件

- 电脑开机且 Codex 应用运行；使用现有 Codex 登录，不调用 Horizon 的付费模型 API。
- GitHub 已登录并可推送本仓库。站点及本仓库为公开内容，仅提交日报、站点文件和工作流，不提交密钥、浏览器登录态或 Horizon 原始配置。
- 微信需要登录 https://sct.ftqq.com/sendkey/ 获取 Turbo SCT SendKey，并配置微信通道；密钥只保存在本机 `Horizon/.env.wechat`，由 Codex 安全加载 `SERVERCHAN_SENDKEY` 后运行 `notify_wechat.py`，不上传到 GitHub。没有密钥时，站点正常发布，通知程序明确报告未配置。
- Horizon 自带微信机器人也可扫码绑定，但其回复额度需要用户发消息刷新，故本方案使用 Server酱。免费额度与通道要求以服务官方说明为准。

## 修改主题和筛选规则

本机 `Horizon/精选规则.txt` 和 `Horizon/data/config.json` 是生成依据；`Horizon/每日工作流说明.txt` 记录实际路径与操作。修改后同步更新站点介绍。新闻源限制和未启用的 X/OpenBB 原生采集器见 Horizon 本地安装说明。

## 验证

`python check_publish.py` 验证发布格式与微信通知内容生成。Actions 的 build/deploy 成功后应可访问首页和当天日报。微信程序成功表示服务已接收请求，仍需在微信检查实际到达。

## 日报阅读结构

`docs/_layouts/default.html` 与 `docs/assets/` 提供共享阅读布局。首页自动突出最新一期；文章根据六类二级标题、新闻三级标题生成导航和条目卡片，手机端目录默认收起。禁用 JavaScript 时完整正文和来源仍可阅读。

本次只更新公开阅读布局，生产生成规则保持不变。拟议的私有 `Horizon/日报结构模板.md` 尚未启用，须确认后审定新的 overlay 提交并另行更新生产固定 SHA。三级标题继续只用于新闻，保持现有前三标题通知兼容；已归档文章不追溯改写。
