# ERP 沙盘 AI 助手

> 基于大语言模型的企业经营沙盘模拟比赛智能决策辅助工具

## 概述

ERP 沙盘 AI 助手是一款面向**企业经营沙盘模拟大赛**（ERP 沙盘比赛）的桌面端智能辅助工具。当前稳定入口是 `erp_agent.py`，通过接入本地大模型（Ollama + Qwen3），结合财务数据和市场情报，为参赛团队提供**多维度、可量化的战略决策建议**，帮助团队在比赛中更科学地制定经营策略，提升所有者权益。核心业务逻辑已和 Tkinter 界面拆分，便于后续测试和扩展。

### 解决的核心问题

在 ERP 沙盘比赛中，参赛者需要在有限时间内综合分析财务状况、市场竞争、研发投入等多方面因素，做出最优经营决策。本工具通过 AI 辅助分析，帮助参赛者：

- **快速掌握财务状况**：实时展示现金、固定资产、库存、贷款、所有者权益等关键指标
- **量化现金流风险**：自动计算现金可支撑的季度数，提前预警资金链断裂风险
- **科学制定广告策略**：基于对手历史数据，推荐最优广告费区间
- **获取战略决策建议**：结合财务数据和市场信息，由 AI 生成全方位的经营决策建议
- **自动化订单分析**：Notebook 原型中包含从 Excel 订单数据筛选高毛利订单的探索代码

## 功能特性

### 1. AI 战略顾问

连接本地大模型，根据当前财务状况和市场信息，自动生成 5 项关键决策建议：

| 决策维度 | 说明 |
|---------|------|
| 广告费建议 | 推荐金额及详细理由 |
| 贷款决策 | 是否贷款、贷多少 |
| 生产线调整 | 扩产、维持或缩减建议 |
| 研发投入 | P1/P2 研发优先级建议 |
| 本轮优先事项 | 最关键的 1-3 项行动 |

### 2. 现金流预警

- 自动计算每季度固定支出（含贷款利息）
- 预测在无新订单情况下现金可支撑的季度数
- 高危状态（≤2 季度）自动触发警示

### 3. 竞争对手分析

- 记录对手历史广告费数据
- 计算历史平均值和最高值
- 推荐本轮广告费投入区间

### 4. 订单数据分析（Notebook 原型）

- 读取经销商订单 Excel 文件
- 自动计算每笔订单的估算毛利
- 按年份/季度筛选最优订单

### 5. 图像识别（Notebook 原型）

- 支持通过 Qwen3-VL 视觉模型识别比赛截图
- 自动提取订单中的产品名、数量、单价等信息

## 快速开始

### 前置依赖

- Python 3.10+
- 一个 OpenAI 兼容 API。可以使用云端 API，也可以继续使用本地 Ollama。

### 安装与运行

```bash
# 1. 安装 Ollama 并拉取模型
ollama pull qwen3-vl:8b

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 复制配置模板并填写 .env
copy .env.example .env

# 4. 运行程序
python erp_agent.py
```

### 使用流程

1. **启动程序**：运行后弹出桌面窗口
2. **输入市场信息**：在文本框输入当前市场情报（如"需求旺盛，对手广告费高"）
3. **获取 AI 建议**：按 Enter 或点击发送，AI 自动生成决策建议
4. **参考执行**：根据 AI 建议调整广告费、贷款、生产线等策略

> 提示：首次连接 AI 可能需要 10-30 秒，请耐心等待。

## 项目结构

```
agent/
├── erp_agent.py                         # 桌面版 GUI 主程序（Tkinter + OpenAI SDK）
├── erp_agent_core.py                    # 财务状态、现金流、竞品分析、模型调用
├── erp_agent_ui.py                      # Tkinter 界面和交互线程
├── requirements.txt                     # Python 依赖清单
├── tests/
│   └── test_erp_agent_core.py           # 不依赖 Ollama 的核心逻辑测试
├── notebooks/
│   ├── erp_agent_prototype.ipynb        # Jupyter Notebook 原型（核心逻辑实现）
│   ├── erp_agent_enhanced.ipynb         # 增强版 Notebook（图像识别、订单分析探索）
│   ├── app_prototype.ipynb              # 应用原型 Notebook
│   ├── main_prototype.ipynb             # Notebook 版本主入口原型
│   └── legacy_main_notebook.ipynb       # 原 main .py，实际内容为 Notebook JSON
├── README.md
└── .gitignore
```

### 打包部署

如需打包为 Windows 单文件可执行程序，可使用 PyInstaller：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed erp_agent.py
```

打包产物默认位于 `dist/erp_agent.exe`。如果后续需要固定图标、版本信息或隐藏资源文件，可再补充 `erp_agent.spec`。

## 技术栈

| 技术 | 用途 |
|------|------|
| Python | 核心开发语言 |
| Tkinter | 桌面 GUI 框架 |
| Ollama + Qwen3 | 本地大语言模型推理 |
| OpenAI Python SDK | Ollama 兼容接口 |
| Pandas | Notebook 订单 Excel 数据分析原型 |
| Requests | Notebook 原型中调用 Ollama 原生接口 |
| PyInstaller | Windows 可执行程序打包 |

## 配置说明

### 模型连接配置

默认会自动读取项目根目录下的 `.env` 文件。先复制模板：

```bash
copy .env.example .env
```

然后按你使用的 API 修改 `.env`：

```env
ERP_AGENT_BASE_URL=http://localhost:11434/v1/
ERP_AGENT_API_KEY=ollama
ERP_AGENT_MODEL=qwen3-vl:8b
ERP_AGENT_TIMEOUT=180
```

- 如需使用云端 API，设置 `ERP_AGENT_BASE_URL` 和 `ERP_AGENT_API_KEY`
- 如需更换模型，设置 `ERP_AGENT_MODEL`
- 如需调整模型请求超时，设置 `ERP_AGENT_TIMEOUT`

继续使用 Ollama 时，需要先启动本地服务：

```bash
ollama serve
```

### 测试

核心逻辑测试不依赖 Ollama，可直接运行：

```bash
python -m unittest discover -s tests -v
```

### 财务参数

在 Notebook 原型中可配置比赛官方参数：

```python
params = {
    "初始现金": 100000,
    "初始所有者权益": 700000,
    "所得税率": 0.25,
    "每季管理费": 10000,
    # 更多参数...
}
```

## 注意事项

- 本工具需配合本地 Ollama 服务使用，首次运行请确保 Ollama 已启动
- AI 建议仅供参考，最终决策请结合比赛实际情况
- 图像识别功能依赖视觉模型，识别效果可能因截图质量而异
- 基于系统提示（prompt）模板，可根据比赛规则自行调整提示词

## 许可证

本项目仅供学习交流使用。

## 作者

ERP 沙盘 AI 助手 - 让数据驱动决策，用 AI 赋能比赛
