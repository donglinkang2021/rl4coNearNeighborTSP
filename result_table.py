import json

def result2table(result_dir:str):
    with open(f'{result_dir}/avg_time.json', 'r') as f:
        avg_time_dict = json.load(f)

    with open(f'{result_dir}/config.json', 'r') as f:
        settings = json.load(f)

    table0 = f"""| setting | avg_time |\n| ------- | -------- |"""
    for setting, avg_time in avg_time_dict.items():
        table0 += f'\n| {settings[setting]} | {avg_time:.3f} |'
    table0 += '\n'

    table1 = f"""
| avg_time | "n_UGVs": 1,</br>"n_UAVs": 5 | "n_UGVs": 1,</br>"n_UAVs": 10 | "n_UGVs": 2,</br>"n_UAVs": 10 | "n_UGVs": 2,</br>"n_UAVs": 20 |
| -------- | ---------------------------- | ----------------------------- | ----------------------------- | ----------------------------- |
| "n_poi": 100, </br>"n_depots": 20 |  {avg_time_dict["setting1"]:.3f}  |  {avg_time_dict["setting2"]:.3f}  |   {avg_time_dict["setting3"]:.3f}   |   {avg_time_dict["setting4"]:.3f}   |
| "n_poi": 200, </br>"n_depots": 20 |  {avg_time_dict["setting9"]:.3f}  |  {avg_time_dict["setting10"]:.3f}  |   {avg_time_dict["setting11"]:.3f}   |   {avg_time_dict["setting12"]:.3f}   |
    """

    table2 = f"""
| avg_time | "n_depots": 10 | "n_depots": 20 | "n_depots": 30 | "n_depots": 40 |
| -------- | ---------------------------- | ----------------------------- | ----------------------------- | ----------------------------- |
| "n_poi": 100, </br>"n_UGVs": 1, </br>"n_UAVs": 10 |  {avg_time_dict["setting5"]:.3f}  |  {avg_time_dict["setting6"]:.3f}  |   {avg_time_dict["setting7"]:.3f}   |   {avg_time_dict["setting8"]:.3f}   |
| "n_poi": 200, </br>"n_UGVs": 2, </br>"n_UAVs": 20 |  {avg_time_dict["setting13"]:.3f}  |  {avg_time_dict["setting14"]:.3f}  |   {avg_time_dict["setting15"]:.3f}   |   {avg_time_dict["setting16"]:.3f}   |
    """

    with open(f'{result_dir}/result_table.md', 'w') as f:
        f.write('# Result Table\n\n')
        f.write(table0)
        f.write(table1)
        f.write(table2)

    print(f'{result_dir}/result_table.md saved')

result2table('result/20240714-102404')