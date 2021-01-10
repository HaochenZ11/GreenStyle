import pandas as pd

# db_file = '/Users/katarinac/Desktop/SheHacks/db.csv'
# store_file = '/Users/katarinac/Desktop/SheHacks/tops.csv'

db_file = 'db.csv'
store_file = 'tops.csv'

db_df = pd.read_csv(db_file)
store_df = pd.read_csv(store_file)
base = 'https://directory.goodonyou.eco'


def query(store_name):
    link_rec = []
    generic_name = store_name.lower().replace(' ', '-')
    store_info = db_df[db_df['store name'].str.contains(generic_name)]
    rate_num = store_info['rating'].item()
    name_rec = [store_info['r1'].item(), store_info['r2'].item(), store_info['r3'].item()]
    if rate_num < 4:
        for name in name_rec:
            tops_name = store_df[store_df['store name'].str.contains(name)]
            tops_link = tops_name['brand link'].item()
            link_rec.append(base + tops_link)
    return [rate_num, link_rec]

# print(query('girlfriend colLectIVe'))