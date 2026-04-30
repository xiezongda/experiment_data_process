from pathlib import Path

from afm_gwyddion_process import process_all_samples


def main():
    project_root = Path(__file__).resolve().parents[2]  
    input_root = project_root / "data" / "AFM"
    output_root = project_root / "data" / "AFM" / "processed"

    excel_paths = process_all_samples(
        input_root=input_root,
        output_root=output_root,
        mode="replace_file",
        add_metadata=True,
    )

    print("处理完成，生成以下 Excel 文件：")
    for path in excel_paths:
        print(path)


if __name__ == "__main__":
    main()