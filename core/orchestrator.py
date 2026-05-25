import json
import os
import time
from datetime import datetime
from input.paper_parser import parse_paper
from agents.tech_understanding import run_tech_understanding
from agents.scene_matching import run_scene_matching
from agents.execution_output import run_execution_output
from core.cache import get_cached, save_cache


class PipelineResult:
    """封装整个流水线的执行结果"""

    def __init__(self):
        self.paper_info: dict = {}
        self.tech_params: dict = {}
        self.scene_matching: dict = {}
        self.final_output: dict = {}
        self.execution_time: float = 0.0
        self.errors: list = []

    def to_dict(self) -> dict:
        return {
            "paper_info": self.paper_info,
            "tech_params": self.tech_params,
            "scene_matching": self.scene_matching,
            "final_output": self.final_output,
            "execution_time_seconds": self.execution_time,
            "errors": self.errors,
        }


def run_full_pipeline(paper_path: str, force_refresh: bool = False) -> PipelineResult:
    """运行完整的转化医学Agent流水线（带缓存）"""
    # 检查缓存
    if not force_refresh:
        cached = get_cached(paper_path)
        if cached:
            result = PipelineResult()
            result.paper_info = cached.get("paper_info", {})
            result.tech_params = cached.get("tech_params", {})
            result.scene_matching = cached.get("scene_matching", {})
            result.final_output = cached.get("final_output", {})
            result.execution_time = cached.get("execution_time_seconds", 0)
            result.errors = cached.get("errors", [])
            result.from_cache = True
            return result

    result = PipelineResult()
    start_time = time.time()

    # Step 1: 解析论文
    try:
        paper_info = parse_paper(paper_path)
        result.paper_info = {
            "file_type": paper_info["file_type"],
            "word_count": paper_info["word_count"],
            "metadata": paper_info.get("metadata", {}),
        }
        paper_text = paper_info["processed_text"]
        paper_meta = paper_info.get("metadata", {})
        paper_abstract = paper_info.get("abstract", "")
    except Exception as e:
        result.errors.append(f"论文解析失败: {str(e)}")
        return result

    # Step 2: 析微 — 技术理解
    try:
        result.tech_params = run_tech_understanding(paper_text, paper_meta, paper_abstract)
    except Exception as e:
        result.errors.append(f"析微Agent执行失败: {str(e)}")
        return result

    # Step 3: 明途 — 场景匹配
    try:
        result.scene_matching = run_scene_matching(result.tech_params)
    except Exception as e:
        result.errors.append(f"明途Agent执行失败: {str(e)}")
        return result

    # Step 4: 智策 — 执行输出
    try:
        result.final_output = run_execution_output(
            result.tech_params, result.scene_matching
        )
    except Exception as e:
        result.errors.append(f"智策Agent执行失败: {str(e)}")
        return result

    result.execution_time = round(time.time() - start_time, 2)

    # 保存缓存
    save_cache(paper_path, result.to_dict())

    return result


def run_pipeline_step_by_step(paper_path: str):
    """生成器模式：逐步执行并yield每个阶段的进度"""
    yield {"stage": "parsing", "status": "running", "message": "正在解析论文..."}

    try:
        paper_info = parse_paper(paper_path)
    except Exception as e:
        yield {"stage": "parsing", "status": "error", "message": str(e)}
        return

    yield {
        "stage": "parsing",
        "status": "done",
        "word_count": paper_info["word_count"],
        "metadata": paper_info.get("metadata", {}),
    }

    paper_text = paper_info["processed_text"]
    paper_meta = paper_info.get("metadata", {})
    paper_abstract = paper_info.get("abstract", "")

    # 析微 — 技术理解
    yield {"stage": "tech_understanding", "status": "running", "message": "析微 Agent 正在分析探针参数..."}

    try:
        tech_params = run_tech_understanding(paper_text, paper_meta, paper_abstract)
    except Exception as e:
        yield {"stage": "tech_understanding", "status": "error", "message": str(e)}
        return

    yield {"stage": "tech_understanding", "status": "done", "data": tech_params}

    # 明途 — 场景匹配
    yield {"stage": "scene_matching", "status": "running", "message": "明途 Agent 正在匹配手术成像平台..."}

    try:
        scene_result = run_scene_matching(tech_params)
    except Exception as e:
        yield {"stage": "scene_matching", "status": "error", "message": str(e)}
        return

    yield {"stage": "scene_matching", "status": "done", "data": scene_result}

    # 智策 — 执行输出
    yield {"stage": "execution_output", "status": "running", "message": "智策 Agent 正在生成临床方案和融资计划..."}

    try:
        final_output = run_execution_output(tech_params, scene_result)
    except Exception as e:
        yield {"stage": "execution_output", "status": "error", "message": str(e)}
        return

    yield {"stage": "execution_output", "status": "done", "data": final_output}
    yield {"stage": "complete", "status": "done", "message": "全流程执行完毕"}
