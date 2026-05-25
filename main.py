"""转化医学Agent - 命令行入口"""
import sys
import json
import os

# Windows 终端 UTF-8 兼容
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from core.orchestrator import run_full_pipeline


def main():
    if len(sys.argv) < 2:
        print("使用方法: python main.py <论文文件路径>")
        print("支持格式: PDF, TXT")
        sys.exit(1)

    paper_path = sys.argv[1]
    print(f"\n{'='*60}")
    print(f"  转化医学 Agent - 从实验室到临床")
    print(f"  输入论文: {paper_path}")
    print(f"{'='*60}\n")

    result = run_full_pipeline(paper_path)

    if result.errors:
        print("\n[错误] 执行过程中出现错误:")
        for err in result.errors:
            print(f"  - {err}")
        sys.exit(1)

    print(f"\n[完成] 执行完成 (耗时 {result.execution_time}s)")

    # 输出结果摘要
    print(f"\n{'='*60}")
    print(f"  结果摘要")
    print(f"{'='*60}")

    if "probe_name" in result.tech_params:
        tp = result.tech_params
        print(f"\n探针: {tp.get('probe_name', 'N/A')}")
        print(f"类型: {tp.get('probe_type', 'N/A')}")
        print(f"靶点: {tp.get('target_biomarker', 'N/A')}")
        print(f"机制: {tp.get('activation_mechanism', 'N/A')}")

    if "recommended_departments" in result.scene_matching:
        depts = result.scene_matching.get("recommended_departments", [])
        print(f"\n推荐科室: {', '.join(depts)}")

    platforms = result.scene_matching.get("top3_imaging_platforms") or result.scene_matching.get("top3_robots", [])
    if platforms:
        print(f"TOP3 适配成像平台:")
        for p in platforms:
            name = p.get("platform_name") or p.get("robot_model", "N/A")
            print(f"   {p.get('rank', '?')}. {name} ({p.get('compatibility_score', 'N/A')}/10)")

    if "clinical_trial_design_file" in result.final_output:
        print(f"\n临床试验设计方案: {result.final_output['clinical_trial_design_file']}")
    if "financing_plan_file" in result.final_output:
        print(f"融资计划书: {result.final_output['financing_plan_file']}")

    # 保存完整结果JSON
    output_dict = result.to_dict()
    output_path = "output/full_result.json"
    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_dict, f, ensure_ascii=False, indent=2)
    print(f"\n完整结果已保存至: {output_path}")


if __name__ == "__main__":
    main()
