from pathlib import Path
import pandas as pd

#gwyddion保存ACF数据时，类型选择comma-separated values (csv)
#def function_name(var1: type, var2: type) -> return_type:
def load_acf_excel(file_path: str | Path) -> dict[str, pd.DataFrame]:
    """
    读取 Gwyddion 导出的 ACF和PSD_1D Excel 数据

    默认假设：
    - 左边两列是一组：x, acf
    - 右边两列是一组：x, acf
    - 中间允许存在空列
    - Excel 中可以没有表头

    返回：
    {
        "left":  DataFrame,
        "right": DataFrame
    }
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在：{file_path}")

    # header=None：不把第一行当表头，全部按数据读取
    df = pd.read_csv(file_path,sep=';', header=None)

    # 删除全空行、全空列
    # axis=0表示删除行，axis=1表示删除列
    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")

    # 尽量把所有内容转成数字，无法转的变成 NaN
    df_numeric = df.apply(pd.to_numeric, errors="coerce")

    # 再删除全空行、全空列
    df_numeric = df_numeric.dropna(how="all")
    df_numeric = df_numeric.dropna(axis=1, how="all")

    if df_numeric.shape[1] < 4:
        raise ValueError(
            f"有效数值列不足 4 列，目前只有 {df_numeric.shape[1]} 列，请检查 Excel 数据格式。"
        )

    # 取前四个有效数值列
    left = df_numeric.iloc[:, 0:2].copy()
    right = df_numeric.iloc[:, 2:4].copy()

    # 统一列名
    left.columns = ["distance_m", "origin_acf"]
    right.columns = ["distance_m", "corrected_acf"]

    # 删除组内空行
    left = left.dropna(how="any").reset_index(drop=True)
    right = right.dropna(how="any").reset_index(drop=True)

    return {
        "left": left,
        "right": right,
    }


def save_preprocessed(
    file_path: str | Path,
    output_dir: str | Path = "output"
) -> None:
    """
    读取 ACF Excel，并分别保存左右两组数据。
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_acf_excel(file_path)

    if not file_path.name == "PSD_1D_data_horizontal.csv" and not file_path.name == "PSD_1D_data_vertical.csv":

        left_path = output_dir / f"{file_path.name}_origin.csv"
        right_path = output_dir / f"{file_path.name}_corrected.csv"

        data["left"].to_csv(left_path, index=False)
        data["right"].to_csv(right_path, index=False)

        print(f"左侧数据已保存：{left_path}")
        print(f"右侧数据已保存：{right_path}")

#只有当这个 .py 文件被直接运行时，下面的代码才会执行。
#如果这个文件是被别的文件 import 导入的，下面的代码不会执行
if __name__ == "__main__":
    #采用pathlib中的通配匹配所有AFM文件下的ACF_data_horizontal.csv和ACF_data_vertical.csv文件
    base_file = Path("./data/AFM")
    type = ["horizontal","vertical"]
    #遍历AFM文件夹下的所有子文件夹，找到其中的ACF_data_horizontal.csv和ACF_data_vertical.csv文件，并进行预处理
    for sample_dir in base_file.iterdir():
        if not sample_dir.is_dir():
            continue

        for t in type:
            for input_file in sample_dir.glob(f"*_data_{t}.csv"):
                if not input_file.exists():
                    print(f"未找到文件：{input_file}，跳过 {sample_dir.name}")
                    continue
                #acf_data = load_acf_excel(input_file)

        # print("左侧数据：")
        # print(acf_data["left"].head())

        # print("\n右侧数据：")
        # print(acf_data["right"].head())

                output_dir = input_file.parent / "preprocessed"
                save_preprocessed(input_file, output_dir)