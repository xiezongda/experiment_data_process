#扫描样本文件夹和 CSV 文件
#识别文件类型：ACF / PSD
#识别方向：horizontal / vertical

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class CSVFileInfo:
    """
    保存一个 Gwyddion CSV 文件的基本信息。
    """

    path: Path
    sample_id: str
    data_type: str       # acf / psd / unknown
    direction: str       # horizontal / vertical / unknown
    sheet_name: str      # 写入 Excel 时使用的 sheet 名称


def infer_data_type(file_name: str) -> str:
    """
    从文件名判断数据类型。
    """
    name = file_name.lower()    #转换为小写，方便判断

    if "acf" in name:
        return "acf"

    if "psd" in name or "psdf" in name:
        return "psd"

    return "unknown"


def infer_direction(file_name: str) -> str:
    """
    从文件名判断方向。
    """
    name = file_name.lower()

    if "horizontal" in name or "hori" in name or "_h" in name:
        return "horizontal"

    if "vertical" in name or "vert" in name or "_v" in name:
        return "vertical"

    return "unknown"


def build_sheet_name(data_type: str, direction: str, file_stem: str) -> str:
    """
    根据数据类型和方向生成 Excel sheet 名。
    """
    if data_type != "unknown" and direction != "unknown":
        return f"{data_type}_{direction}"

    if data_type != "unknown":
        return data_type

    return file_stem


def scan_csv_files(sample_dir: Path) -> list[CSVFileInfo]:
    """
    扫描一个样本文件夹中的 CSV 文件。

    参数
    ----
    sample_dir:
        单个样本文件夹，例如 data/raw/gwyddion/sample_001

    返回
    ----
    list[CSVFileInfo]
    """
    sample_dir = Path(sample_dir)

    if not sample_dir.exists():
        raise FileNotFoundError(f"样本文件夹不存在：{sample_dir}")

    if not sample_dir.is_dir():
        raise NotADirectoryError(f"不是文件夹：{sample_dir}")

    sample_id = sample_dir.name
    csv_infos: list[CSVFileInfo] = []

    for csv_path in sorted(sample_dir.glob("*.csv")):
        if "fit" in csv_path.stem.lower():
            continue
        data_type = infer_data_type(csv_path.name)
        direction = infer_direction(csv_path.name)
        sheet_name = build_sheet_name(
            data_type=data_type,
            direction=direction,
            file_stem=csv_path.stem,
        )

        csv_infos.append(
            CSVFileInfo(
                path=csv_path,
                sample_id=sample_id,
                data_type=data_type,
                direction=direction,
                sheet_name=sheet_name,
            )
        )

    return csv_infos


def scan_sample_dirs(input_root: Path) -> list[Path]:
    """
    扫描总输入目录下的样本文件夹。

    例如：
    data/raw/gwyddion/
    ├── sample_001/
    ├── sample_002/
    └── sample_003/
    """
    input_root = Path(input_root)

    if not input_root.exists():
        raise FileNotFoundError(f"输入目录不存在：{input_root}")

    if not input_root.is_dir():
        raise NotADirectoryError(f"不是文件夹：{input_root}")

    sample_dirs = [
        p for p in sorted(input_root.iterdir())
        if p.is_dir()
    ]

    return sample_dirs