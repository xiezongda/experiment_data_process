# 把 scanner、parser、preprocess、excel_writer 串起来

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .scanner import scan_csv_files, scan_sample_dirs
from .parser import read_gwyddion_csv
from .preprocess import (
    preprocess_gwyddion_dataframe,
    build_summary_row,
)
from .excel_writer import write_tables_to_excel


def process_one_sample(
    sample_dir: Path,
    output_root: Path | None = None,
    excel_name: str | None = None,
    mode: str = "replace_file",
    add_metadata: bool = True,
) -> Path:
    """
    处理单个样本文件夹。

    输入示例：
    sample_001/
    ├── ACF_horizontal.csv
    ├── ACF_vertical.csv
    ├── PSD_horizontal.csv
    └── PSD_vertical.csv

    输出示例：
    data/processed/gwyddion/sample_001/sample_001_gwyddion.xlsx

    参数
    ----
    sample_dir:
        单个样本文件夹。

    output_root:
        输出根目录。如果为 None，则输出到 sample_dir 本身。

    excel_name:
        输出 Excel 文件名。如果为 None，则自动使用：
        {sample_id}_gwyddion.xlsx

    mode:
        - "replace_file": 每次重新生成 Excel；
        - "append_new_sheets": 保留旧 sheet，新数据追加为新 sheet。

    add_metadata:
        是否给每个 sheet 添加 sample_id、data_type、direction、source_file 列。

    返回
    ----
    Path:
        生成的 Excel 文件路径。
    """
    sample_dir = Path(sample_dir)
    sample_id = sample_dir.name

    if output_root is None:
        output_dir = sample_dir
    else:
        output_dir = Path(output_root) / sample_id

    if excel_name is None:
        excel_name = f"{sample_id}_gwyddion.xlsx"

    excel_path = output_dir / excel_name

    csv_infos = scan_csv_files(sample_dir)

    if len(csv_infos) == 0:
        raise FileNotFoundError(
            f"样本文件夹中没有找到 CSV 文件：{sample_dir}"
        )

    tables: dict[str, pd.DataFrame] = {}
    summary_rows: list[dict] = []

    for info in csv_infos:
        raw_df = read_gwyddion_csv(info.path)

        processed_df = preprocess_gwyddion_dataframe(
            df=raw_df,
            info=info,
            add_metadata=add_metadata, 
        )

        tables[info.sheet_name] = processed_df   #每个 sheet 的名字由 scanner.py 根据 data_type 和 direction 自动生成

        summary_rows.append(
            build_summary_row(
                info=info,
                df=processed_df,
            )
        )

    summary_df = pd.DataFrame(summary_rows)    #summary_df里面的每一个元素都是一个字典，每个字典代表一个csv文件的统计信息和处理后数据

    ordered_tables: dict[str, pd.DataFrame] = {
        "summary": summary_df,
    }
    ordered_tables.update(tables)   #保证tables中的sheet在summary之后

    write_tables_to_excel(
        excel_path=excel_path,
        tables=ordered_tables,
        mode=mode,
        auto_width=True,
    )

    return excel_path


def process_all_samples(
    input_root: Path,
    output_root: Path,
    mode: str = "replace_file",
    add_metadata: bool = True,
) -> list[Path]:
    """
    批量处理所有样本文件夹。

    输入目录示例：
    data/raw/gwyddion/
    ├── sample_001/
    ├── sample_002/
    └── sample_003/

    输出目录示例：
    data/processed/gwyddion/
    ├── sample_001/
    │   └── sample_001_gwyddion.xlsx
    ├── sample_002/
    │   └── sample_002_gwyddion.xlsx
    └── sample_003/
        └── sample_003_gwyddion.xlsx
    """
    input_root = Path(input_root)
    output_root = Path(output_root)

    sample_dirs = scan_sample_dirs(input_root)

    if len(sample_dirs) == 0:
        raise FileNotFoundError(
            f"输入目录下没有找到样本文件夹：{input_root}"
        )

    output_paths: list[Path] = []

    for sample_dir in sample_dirs:
        excel_path = process_one_sample(
            sample_dir=sample_dir,
            output_root=output_root,
            mode=mode,
            add_metadata=add_metadata,
        )
        output_paths.append(excel_path)

    return output_paths