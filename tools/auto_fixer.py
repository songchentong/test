"""运行 pytest，并让 OpenAI 自动修复失败的测试文件。

用法示例::

    # 修复所有失败的测试
    python tools/auto_fixer.py

    # 最多尝试 3 轮，只修复指定文件
    python tools/auto_fixer.py --max-attempts 3 -- -q tests/test_example.py

    # 指定模型
    python tools/auto_fixer.py --model gpt-5.5

依赖:
    pip install openai

环境变量:
    OPENAI_API_KEY   - OpenAI（或中转服务）的 API Key
    OPENAI_BASE_URL  - 可选，如果是中转服务，需要设置（如 https://apinebula.ai/v1）

安全机制:
    - 只允许写入 tests/ 目录下的 .py 文件
    - 写入前会做语法检查（ast.parse）
    - 不会修改源代码
"""

from __future__ import annotations

import argparse
import ast
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Sequence


# ========== 默认配置 ==========
DEFAULT_MODEL = "gpt-5.5"          # 默认使用的 AI 模型
DEFAULT_MAX_ATTEMPTS = 3           # 最多修复几轮

# 匹配 pytest 输出中的 "FAILED tests/xxx.py::test_yyy - 说明"
_FAILED_LINE = re.compile(
    r"^FAILED\s+(.+?\.py)(?:::[^\s]+)?(?:\s+-\s+.*)?$",
    re.MULTILINE
)

# 匹配 pytest 输出中的 "ERROR tests/xxx.py::test_yyy - 说明"
_ERROR_LINE = re.compile(
    r"^ERROR\s+(.+?\.py)(?:::[^\s]+)?(?:\s+-\s+.*)?$",
    re.MULTILINE
)

# 匹配 traceback 中的文件路径，例如: File "tests/test_xxx.py", line 10
_TRACEBACK_FILE = re.compile(r'File "([^"\r\n]+\.py)", line \d+')

# 匹配 AI 返回的 Markdown 代码块（```python ... ```）
_CODE_FENCE = re.compile(
    r"^```(?:python)?\s*\r?\n(?P<code>.*)\r?\n```\s*$",
    re.DOTALL
)


# ========== 1. 运行 pytest ==========

def _run_pytest(
    project_root: Path,
    pytest_args: Sequence[str],
) -> subprocess.CompletedProcess[str]:
    """在项目根目录运行 pytest，返回结果。

    参数:
        project_root: 项目根目录
        pytest_args: 传给 pytest 的参数，如 ["-q", "tests/test_x.py"]

    返回:
        CompletedProcess 对象，包含 returncode 和 stdout
    """
    # 拼装命令: python -m pytest <参数>
    command = [sys.executable, "-m", "pytest", *pytest_args]
    print(f"\n$ {' '.join(command)}", flush=True)

    # 运行命令
    result = subprocess.run(
        command,
        cwd=project_root,          # 在项目根目录运行
        text=True,                  # 文本模式
        encoding="utf-8",
        errors="replace",           # 编码错误不崩溃
        stdout=subprocess.PIPE,     # 捕获输出
        stderr=subprocess.STDOUT,   # stderr 合并到 stdout
        check=False,                # 不抛异常，靠 returncode 判断
    )

    # 打印 pytest 输出
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    return result


# ========== 2. 判断路径是否在 tests/ 下 ==========

def _is_relative_to(path: Path, directory: Path) -> bool:
    """判断 path 是否在 directory 目录下（Python 3.9+ 兼容写法）。"""
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


# ========== 3. 从 pytest 输出中找出失败的测试文件 ==========

def _test_files_from_matches(
    matches: Sequence[str], project_root: Path
) -> list[Path]:
    """把 pytest 输出中匹配到的路径转换为安全的测试文件路径。

    安全机制:
        - 只返回 tests/ 目录下的文件
        - 只返回存在的 .py 文件
        - 去重
    """
    tests_root = (project_root / "tests").resolve()

    found: list[Path] = []

    for raw_path in matches:
        raw_path = raw_path.strip()
        candidate = Path(raw_path)

        # 相对路径转绝对路径
        if not candidate.is_absolute():
            candidate = project_root / candidate
        candidate = candidate.resolve()

        # 过滤: 必须是 tests/ 下的 .py 文件，且存在
        if (
            candidate.suffix == ".py"
            and candidate.is_file()
            and _is_relative_to(candidate, tests_root)
            and candidate not in found
        ):
            found.append(candidate)

    return found


def _error_test_files(output: str, project_root: Path) -> list[Path]:
    """提取发生 ERROR 的测试文件；ERROR 始终优先修复。"""
    return _test_files_from_matches(_ERROR_LINE.findall(output), project_root)


def _failed_test_files(output: str, project_root: Path) -> list[Path]:
    """提取发生 FAILED 的测试文件。"""
    failed_matches = _FAILED_LINE.findall(output)
    if not failed_matches:
        # 某些 pytest 插件不输出标准 FAILED 摘要，此时才使用 traceback 兜底。
        failed_matches = _TRACEBACK_FILE.findall(output)
    return _test_files_from_matches(failed_matches, project_root)


# ========== 4. 从 AI 返回中提取纯代码 ==========

def _extract_source(response_text: str) -> str:
    """从 AI 返回的文本中提取纯 Python 代码。

    AI 可能返回:
        - 带 ```python ... ``` 的 Markdown 代码块
        - 纯代码

    处理:
        1. 去掉 Markdown 代码块标记
        2. 确保末尾有换行
        3. 用 ast.parse 验证语法（语法错误会抛异常）
    """
    text = response_text.strip()

    # 去掉 Markdown 代码块
    fenced = _CODE_FENCE.match(text)
    if fenced:
        text = fenced.group("code")

    # 确保末尾有换行
    if not text.endswith("\n"):
        text += "\n"

    # 语法检查（语法错误会抛 SyntaxError）
    ast.parse(text)
    return text


# ========== 5. 让 OpenAI 修复测试文件 ==========

def _ask_for_fix(
    *,
    model: str,
    test_file: Path,
    project_root: Path,
    failure_output: str,
    issue_type: str,
) -> str:
    """调用 OpenAI，让它返回修复后的测试代码。

    参数:
        model: 模型名，如 gpt-5.5
        test_file: 失败的测试文件路径
        project_root: 项目根目录
        failure_output: pytest 的失败输出

    返回:
        修复后的完整 Python 源码

    异常:
        RuntimeError: 缺少 openai 包或未设置 API Key
    """
    # 延迟导入，避免没装包时直接崩溃
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "缺少 openai 包，请先运行: python -m pip install openai"
        ) from exc

    API_KEY = "sk-HD9FVfXCuyiypZsRtFL3NZqcLwd8q2aPcwDcBju0QDltbiD8"
    BASE_URL = "https://apinebula.ai/v1"
    # 读取原测试源码
    original_source = test_file.read_text(encoding="utf-8")
    relative_name = test_file.relative_to(project_root).as_posix()

    # 构造提示词
    prompt = f"""你是一名资深 Python/pytest 工程师。请修复下面发生 {issue_type} 的测试文件。

规则：
1. 只返回修复后文件的完整 Python 源码，不要 Markdown 代码块，不要解释。
2. 保留与当前失败无关的测试，不要删除或跳过测试，不要使用 xfail。
3. 不要降低断言强度来掩盖产品代码缺陷；仅修复测试本身的错误、过时用法或不稳定性。
4. 不得修改生产代码、配置或其他文件。

测试文件：{relative_name}

pytest 失败输出：
---
{failure_output}
---

当前测试文件源码：
---
{original_source}
---
"""

    # 创建客户端并调用
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )  
    response = client.responses.create(model=model, input=prompt)

    # 提取纯代码
    return _extract_source(response.output_text)


# ========== 6. 自动修复主流程 ==========

def run_auto_fixer(
    *,
    project_root: Path,
    pytest_args: Sequence[str],
    model: str,
    max_attempts: int,
) -> int:
    """运行 pytest 并修复失败的测试，返回进程退出码。

    返回:
        0 - 全部通过
        非 0 - 仍有失败或出错
    """
    # 第一次跑测试
    result = _run_pytest(project_root, pytest_args)

    if result.returncode == 0:
        print("pytest 已全部通过，无需修复。")
        return 0

    # 最多重试 max_attempts 轮
    for attempt in range(1, max_attempts + 1):
        # ERROR 优先：只要存在 ERROR，本轮就不处理 FAILED。
        target_files = _error_test_files(result.stdout, project_root)
        issue_type = "ERROR"
        if not target_files:
            target_files = _failed_test_files(result.stdout, project_root)
            issue_type = "FAILED"

        if not target_files:
            print(
                "无法从 pytest 输出中定位 tests/ 下的 ERROR 或 FAILED 文件，停止自动修复。",
                file=sys.stderr,
            )
            return result.returncode or 1

        print(
            f"\n开始第 {attempt}/{max_attempts} 轮修复："
            f"优先处理 {len(target_files)} 个 {issue_type} 测试文件"
        )
        changed = False

        # 逐个修复
        for test_file in target_files:
            try:
                old_source = test_file.read_text(encoding="utf-8")
                new_source = _ask_for_fix(
                    model=model,
                    test_file=test_file,
                    project_root=project_root,
                    failure_output=result.stdout,
                    issue_type=issue_type,
                )

                # AI 没改
                if new_source == old_source:
                    print(f"AI 未修改 {test_file.relative_to(project_root)}")
                    continue

                # 写回文件（newline="" 保留原有换行风格）
                test_file.write_text(new_source, encoding="utf-8", newline="")
                changed = True
                print(f"已更新 {test_file.relative_to(project_root)}")

            except (OSError, SyntaxError, RuntimeError, AttributeError) as exc:
                print(
                    f"修复 {test_file.relative_to(project_root)} 失败：{exc}",
                    file=sys.stderr,
                )
                return 2

        # 这轮没有任何改动，退出
        if not changed:
            print("本轮没有产生有效修改，停止自动修复。", file=sys.stderr)
            return result.returncode or 1

        # 重跑测试
        result = _run_pytest(project_root, pytest_args)
        if result.returncode == 0:
            print(f"pytest 已通过，共执行 {attempt} 轮修复。")
            return 0

    print(f"达到最大修复次数 {max_attempts}，pytest 仍未通过。", file=sys.stderr)
    return result.returncode or 1


# ========== 7. 命令行参数解析 ==========

def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="使用 OpenAI 自动修复失败的 pytest 测试文件"
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"OpenAI 模型（默认：{DEFAULT_MODEL}）",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=DEFAULT_MAX_ATTEMPTS,
        help=f"最多自动修复轮数（默认：{DEFAULT_MAX_ATTEMPTS}）",
    )
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="传给 pytest 的参数（放在 -- 后）",
    )
    args = parser.parse_args(argv)

    # 校验
    if args.max_attempts < 1:
        parser.error("--max-attempts 必须大于等于 1")

    # 去掉 "--"
    if args.pytest_args[:1] == ["--"]:
        args.pytest_args = args.pytest_args[1:]

    return args


# ========== 8. 入口 ==========

def main(argv: Sequence[str] | None = None) -> int:
    """主入口。"""
    args = _parse_args(argv)

    # 项目根目录 = 本文件所在目录的上一级
    # 即: tools/auto_fixer.py → 项目根目录
    project_root = Path(__file__).resolve().parent.parent

    return run_auto_fixer(
        project_root=project_root,
        pytest_args=args.pytest_args,
        model=args.model,
        max_attempts=args.max_attempts,
    )


if __name__ == "__main__":
    raise SystemExit(main())
