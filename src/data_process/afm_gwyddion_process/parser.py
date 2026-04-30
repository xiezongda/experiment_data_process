# 读取 Gwyddion 导出的 CSV
# 自动尝试不同编码
# 自动识别分隔符
# 保留原始数据列和拟合曲线列
from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_gwyddion_csv(csv_path: Path) -> pd.DataFrame:
    """
    读取 Gwyddion 导出的 CSV 文件。

    特点：
    - 自动尝试常见编码；
    - 自动识别分隔符；
    - 保留所有列，包括原始曲线和拟合曲线；
    - 不在这里做复杂清洗，清洗交给 preprocess.py。

    参数
    ----
    csv_path:
        CSV 文件路径。

    返回
    ----
    pandas.DataFrame
    """
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV 文件不存在：{csv_path}")

    encodings = [
        "utf-8-sig",
        "utf-8",
        "gbk",
        "gb18030",
        "latin1",
    ]

    last_error: Exception | None = None

    for encoding in encodings:
        try:
            df = pd.read_csv(
                csv_path,
                sep=None,         #自动识别分隔符，支持逗号、分号、制表符等
                engine="python",  #使用 Python 引擎以支持自动分隔符识别
                encoding=encoding,
                comment=None,
            )
            return df

        except Exception as exc:
            last_error = exc

    raise RuntimeError(
        f"读取 CSV 失败：{csv_path}\n"
        f"最后一次错误信息：{last_error}"
    )


def read_csv_with_metadata(csv_path: Path) -> tuple[pd.DataFrame, dict]:
    """
    读取 CSV，同时返回简单元数据。

    这个函数方便后面写入 Excel 时添加说明。
    """
    df = read_gwyddion_csv(csv_path)

    metadata = {
        "file_name": csv_path.name,
        "file_path": str(csv_path),
        "n_rows": len(df),
        "n_columns": len(df.columns),
        "columns": list(df.columns),
    }

    return df, metadata