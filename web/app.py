"""智慧医疗Agent - Web交互界面"""
import json
import os
import sys
import tempfile
import time

import streamlit as st

# 将项目根目录加入路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator import run_full_pipeline


st.set_page_config(
    page_title="智慧医疗 Agent",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义字体样式
st.markdown("""
<style>
.stApp {
  font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------- 侧边栏 ----------
with st.sidebar:
    st.title("🧬 智慧医疗 Agent")
    st.markdown("**从实验室到临床**")
    st.markdown("---")
    st.markdown("""
    ### 工作流程
    1. 📄 **上传论文** - 提交学术论文PDF/TXT
    2. 🔬 **析微** - 技术理解，提取探针关键参数
    3. 🏥 **明途** - 场景匹配，匹配手术平台与科室
    4. 📋 **智策** - 执行输出，生成临床方案与融资计划
    """)
    st.markdown("---")
    st.caption("华为云杯 2026 AI OPC 应用创新大赛")

# ---------- 主界面 ----------
st.title("🧬 智慧医疗 Agent")
st.markdown("### 从实验室到临床 —— AI 驱动的转化医学智能助手")

# 检查API配置
has_api_key = bool(os.getenv("LLM_API_KEY"))
if not has_api_key:
    st.warning("⚠️ 请先配置 LLM_API_KEY 环境变量（在 .env 文件中设置）")

# 论文上传
st.markdown("---")
st.subheader("📄 Step 1: 上传学术论文")

uploaded_file = st.file_uploader(
    "支持 PDF 和 TXT 格式",
    type=["pdf", "txt"],
    help="上传一篇关于新型荧光探针或其他医疗技术的学术论文",
)

# 示例论文输入
st.markdown("---")
st.subheader("📝 或者直接粘贴论文摘要")
paper_text_input = st.text_area(
    "粘贴论文内容",
    height=200,
    placeholder="在此粘贴论文摘要或全文...\n\n如果同时上传文件和粘贴文本，将优先使用上传的文件。",
)

# 执行按钮
run_disabled = not has_api_key or (not uploaded_file and not paper_text_input.strip())
if st.button(
    "🚀 启动转化医学分析",
    type="primary",
    disabled=run_disabled,
    use_container_width=True,
):
    # 准备输入
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}"
        ) as tmp:
            tmp.write(uploaded_file.getvalue())
            paper_path = tmp.name
        st.info(f"已上传文件: {uploaded_file.name}")
    else:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".txt", mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write(paper_text_input)
            paper_path = tmp.name
        st.info("使用粘贴的文本内容")

    # 进度条
    progress_bar = st.progress(0, text="准备中...")
    status_area = st.empty()

    # 占位区域
    tech_container = st.empty()
    scene_container = st.empty()
    output_container = st.empty()

    # 执行流水线
    try:
        # 先检查缓存
        from core.cache import get_cached
        if get_cached(paper_path):
            status_area.info("💾 检测到缓存结果，直接加载（如需刷新请勾选下方选项）")

        progress_bar.progress(10, text="正在解析论文...")
        time.sleep(0.2)

        result = run_full_pipeline(paper_path)
        progress_bar.progress(100, text="完成!")

        cache_label = " (缓存)" if getattr(result, 'from_cache', False) else " (实时)"
        if result.errors:
            status_area.error(f"执行出错: {'; '.join(result.errors)}")
        else:
            status_area.success(f"✅ 全流程分析完成! 耗时 {result.execution_time}s{cache_label}")

            # ---- Agent 1 结果 ----
            with tech_container.container():
                st.markdown("---")
                st.subheader("🔬 析微 (XiWei) — 技术理解")

                tp = result.tech_params
                if "parse_error" not in tp:
                    # 基本信息行
                    st.markdown(f"**{tp.get('probe_name', 'N/A')}** | {tp.get('probe_type', '')} | TRL: {tp.get('translational_potential', {}).get('clinical_readiness_score', 'N/A')}")

                    # 三列核心参数
                    cols = st.columns(3)
                    with cols[0]:
                        st.markdown("**🎯 靶向与激活**")
                        st.markdown(f"- 靶点: {tp.get('target_biomarker', 'N/A')}")
                        st.markdown(f"- 机制: {tp.get('activation_mechanism', 'N/A')}")
                        st.markdown(f"- 荧光团: {tp.get('fluorophore', 'N/A')}")
                        st.markdown(f"- 策略: {tp.get('targeting_strategy', 'N/A')[:80]}...")
                    with cols[1]:
                        st.markdown("**🔬 光学性质**")
                        op = tp.get('optical_properties', {})
                        st.markdown(f"- 吸收峰: {op.get('absorption_max', {}).get('value', 'N/A')}")
                        st.markdown(f"- 发射峰: {op.get('emission_max', {}).get('value', 'N/A')}")
                        st.markdown(f"- Stokes位移: {op.get('stokes_shift', {}).get('value', 'N/A')}")
                        st.markdown(f"- 量子产率: {op.get('quantum_yield', {}).get('value', 'N/A')}")
                    with cols[2]:
                        st.markdown("**💊 性能与安全**")
                        iv = tp.get('in_vitro_performance', {})
                        sa = tp.get('safety_assessment', {})
                        st.markdown(f"- T/N比: {iv.get('tumor_to_normal_ratio', {}).get('value', 'N/A')}")
                        st.markdown(f"- 最小检出: {iv.get('detection_limit', {}).get('value', 'N/A')}")
                        st.markdown(f"- 体内毒性: {sa.get('in_vivo_toxicity', {}).get('value', 'N/A')[:50]}")

                    # 转化潜力
                    tr = tp.get('translational_potential', {})
                    advantages = tr.get('key_advantages', [])
                    indications = tr.get('suggested_indications', [])
                    if advantages:
                        st.markdown("**🏆 核心优势:**")
                        for adv in advantages:
                            st.markdown(f"- {adv}")
                    if indications:
                        st.markdown(f"**🏥 建议适应症:** {' | '.join(indications)}")

                    with st.expander("查看完整技术参数 JSON"):
                        st.json(tp)
                else:
                    st.text(tp.get("raw_output", "无输出"))

            # ---- Agent 2 结果 ----
            with scene_container.container():
                st.markdown("---")
                st.subheader("🏥 明途 (MingTu) — 场景匹配")

                sm = result.scene_matching
                if "parse_error" not in sm:
                    depts = sm.get("recommended_departments", [])
                    if depts:
                        st.markdown("**推荐科室:** " + " | ".join(f"`{d}`" for d in depts))
                        if sm.get("department_rationale"):
                            st.caption(sm["department_rationale"][:200])

                    if sm.get("compatibility_analysis"):
                        st.markdown(f"**兼容性分析:** {sm['compatibility_analysis'][:300]}")

                    platforms = sm.get("top3_imaging_platforms") or sm.get("top3_robots", [])
                    if platforms:
                        st.markdown("**TOP3 适配荧光成像平台:**")
                        plat_cols = st.columns(min(len(platforms), 3))
                        for i, plat in enumerate(platforms):
                            with plat_cols[i]:
                                name = plat.get("platform_name") or plat.get("robot_model", "N/A")
                                ptype = plat.get("platform_type", "")
                                st.metric(
                                    f"#{plat.get('rank', i+1)} {name}",
                                    f"综合评分: {plat.get('compatibility_score', 'N/A')}/10",
                                )
                                if ptype:
                                    st.caption(f"类型: {ptype}")
                                st.caption(f"厂商: {plat.get('manufacturer', 'N/A')}")
                                st.caption(f"装机量: {plat.get('estimated_installations_china', 'N/A')}")
                                if plat.get("administration_fit"):
                                    st.caption(f"给药适配: {plat['administration_fit'][:80]}")

                    if sm.get("market_analysis"):
                        with st.expander("市场分析"):
                            st.markdown(sm["market_analysis"])

                    with st.expander("查看完整场景匹配 JSON"):
                        st.json(sm)
                else:
                    st.text(sm.get("raw_output", "无输出"))

            # ---- Agent 3 结果 ----
            with output_container.container():
                st.markdown("---")
                st.subheader("📋 智策 (ZhiCe) — 执行输出")

                fo = result.final_output
                if "clinical_trial_design" in fo:
                    with st.expander("📄 临床试验设计方案 (Phase I)", expanded=True):
                        st.markdown(fo["clinical_trial_design"])
                        if "clinical_trial_design_file" in fo:
                            st.caption(f"已保存至: {fo['clinical_trial_design_file']}")

                if "financing_plan" in fo:
                    with st.expander("💰 创新医疗器械融资计划书", expanded=False):
                        st.markdown(fo["financing_plan"])
                        if "financing_plan_file" in fo:
                            st.caption(f"已保存至: {fo['financing_plan_file']}")

    except Exception as e:
        st.error(f"执行失败: {str(e)}")
    finally:
        # 清理临时文件
        if os.path.exists(paper_path):
            os.unlink(paper_path)

# 页脚
st.markdown("---")
st.caption("智慧医疗 Agent v1.0 | 华为云杯 2026 AI OPC 应用创新大赛")
