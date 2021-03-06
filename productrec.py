import pandas as pd

def get_info(url, img):
    store_name = url.replace("https://", "")
    store_name = store_name[0:store_name.index(".com")]
    store_name = store_name.replace("www.", "").replace("-", " ").upper()

    product_name = url[url.index("products/"):].replace("products/", "").replace("-", " ")

    return (store_name, product_name, url, img)

def give_rec(type, num):
    sel = 0
    rec_list = []
    df = pd.read_csv(type+"_22.csv")
    del df['Unnamed: 0']

    prev = df["links"][0]
    prev_index = prev[0:prev.index(".")]

    for i in range(0, len(df), 1):
        line = df["links"][i]
        index = df["links"][i][0:line.index(".")]

        if i == 0:
            rec_list.append(get_info(df.iloc[i][0], df.iloc[i][1]))
            sel +=1
        elif index != prev_index and sel<num:
            rec_list.append(get_info(df.iloc[i][0], df.iloc[i][1]))
            sel += 1
        if sel==num:
            break
        prev = line
        prev_index = index
    return rec_list

#options for types: "dresses", "tops", "bottoms"
#give_rec("dresses", 3)