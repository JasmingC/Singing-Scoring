import textgrid


def parse_Interval(IntervalObject):
    start_time = str()
    end_time = str()
    P_name = str()

    ind = 0
    str_interval = str(IntervalObject)
    for ele in str_interval:
        if ele == "(":
            ind = 1
        if ele == " "and ind == 1:
            ind = 2
        if ele == ","and ind == 2:
            ind = 3
        if ele == " "and ind == 3:
            ind = 4

        if ind == 1:
            if ele != "("and ele != ",":
                start_time = start_time + ele
        if ind == 2:
            end_time = end_time + ele
        if ind == 4:
            if ele != " "and ele != ")":
                P_name = P_name + ele

    st = float(start_time)
    et = float(end_time)
    pn = P_name

    return {pn: (st, et)}


def parse_textgrid(filename):
    output_dict = dict()

    tg = textgrid.TextGrid.fromFile(filename)
    list_words = tg.getList("phones")
    words_list = list_words[0]

    for ele in words_list:
        d = parse_Interval(ele)
        output_dict.update(d)

    return output_dict
