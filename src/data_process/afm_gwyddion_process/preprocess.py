# 清洗列名
# 删除全空行/全空列
# 把能转成数字的列转成数字
# 给数据加上 sample_id、data_type、direction 等信息

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .scanner import CSVFileInfo


def convert_possible_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    尽量把可以转成数字的列转成数字。
    不能转数字的文本列保持原样。
    """
    df = df.copy()

    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")

        non_empty_mask = (
            df[col].notna()
            & (df[col].astype(str).str.strip() != "")
        )

        if non_empty_mask.sum() == 0:
            continue

        # 只有当这一列所有非空值都能成功转成数字时，才替换
        if converted[non_empty_mask].notna().all():
            df[col] = converted

    return df

def clean_column_name(column: object) -> str:
    """
    清洗单个列名。

    Gwyddion 导出的列名可能包含：
    - 前后空格
    - 单位
    - 奇怪符号
    - 重复空格
    """
    name = str(column).strip()

    name = name.replace("\ufeff", "")
    name = re.sub(r"\s+", "_", name)
    name = name.replace("/", "_per_")
    name = name.replace("\\", "_")
    name = name.replace("(", "")
    name = name.replace(")", "")
    name = name.replace("[", "")
    name = name.replace("]", "")
    name = name.replace(":", "_")

    if name == "":
        name = "unnamed"

    return name


def make_unique_columns(columns: list[str]) -> list[str]:
    """
    避免重复列名。

    例如：
    ["x", "y", "y"] -> ["x", "y", "y_2"]
    """
    seen: dict[str, int] = {}
    new_columns: list[str] = []

    for col in columns:
        if col not in seen:
            seen[col] = 1
            new_columns.append(col)
        else:
            seen[col] += 1
            new_columns.append(f"{col}_{seen[col]}")

    return new_columns


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    对 Gwyddion CSV 数据做基础清洗。

    处理内容：
    - 删除全空行；
    - 删除全空列；
    - 清洗列名；
    - 尽量把数据列转成数值；
    """
    df = df.copy()

    df = df.dropna(axis=0, how="all")
    df = df.dropna(axis=1, how="all")

    cleaned_columns = [
        clean_column_name(col)
        for col in df.columns
    ]
    df.columns = make_unique_columns(cleaned_columns)

    df = convert_possible_numeric_columns(df)

    return df


def add_metadata_columns(
    df: pd.DataFrame,
    info: CSVFileInfo,
) -> pd.DataFrame:
    """
    给 DataFrame 添加来源信息。

    这样后面多个 sheet 或多个样本合并时，不容易混。
    """
    df = df.copy()

    df.insert(0, "source_file", info.path.name)
    df.insert(0, "direction", info.direction)
    df.insert(0, "data_type", info.data_type)
    df.insert(0, "sample_id", info.sample_id)

    return df


def preprocess_gwyddion_dataframe(
    df: pd.DataFrame,
    info: CSVFileInfo,
    add_metadata: bool = True,
) -> pd.DataFrame:
    """
    完整预处理入口。
    """
    df = clean_dataframe(df)

    if add_metadata:
        df = add_metadata_columns(df, info)

    return df


def build_summary_row(
    info: CSVFileInfo,
    df: pd.DataFrame,
) -> dict:
    """
    为 summary sheet 生成一行信息。

    注意：
    这里只做文件级别统计，不解析具体 ACF/PSD 参数。
    后面可以继续扩展，比如自动识别 tau、sigma、H 等列。
    """
    return {
        "sample_id": info.sample_id,
        "file_name": info.path.name,
        "sheet_name": info.sheet_name,
        "data_type": info.data_type,
        "direction": info.direction,
        "n_rows": len(df),
        "n_columns": len(df.columns),
        "columns": ", ".join(map(str, df.columns)),# 逗号分隔的列名
    }