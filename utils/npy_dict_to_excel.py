from pathlib import Path

import numpy as np
import pandas as pd


def convert_npy_dict_to_xlsx(file_path):
    data_dict = np.load(file_path, allow_pickle=True).item()

    df = pd.DataFrame(list(data_dict.values()), index=data_dict.keys())
    df.reset_index(inplace=True)
    df.columns = ['Key'] + [f'Value {i + 1}' for i in range(df.shape[1] - 1)]

    # Сохранение DataFrame в файл Excel
    excel_path = file_path.replace('.npy', '.xlsx')
    df.to_excel(excel_path, index=False)
    print(f'[INFO] Excel файл создан в {Path(excel_path).absolute()}')
