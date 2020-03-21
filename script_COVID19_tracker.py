#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 09:47:30 2020

@author: vbokharaie
"""
def save_mat(filename, var):
    folder = filename.parent
    folder.mkdir(parents=True, exist_ok=True)
    my_dict = {'var_name': var}
    from scipy.io import savemat
    savemat(filename, my_dict)

def make_beamer_slide_type1(title, filename, subfolder):
    str_out = str("""

    \\frame{
 	\\frametitle{"""+title+"""}
     \\begin{figure}
	\\centering
	\\includegraphics[width=1.0\\linewidth]{"""+subfolder+"""/"""+filename+"""}

    \\end{figure}

    }

    """)
    return str_out

def get_covid19_stat_df(stat_type, dir_save_csv):
    import wget
    import pandas as pd
    if stat_type == 'c':
        url = 'https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_19-covid-Confirmed.csv'
    if stat_type == 'd':
        url = 'https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_19-covid-Deaths.csv'
    if stat_type == 'r':
        url = 'https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_19-covid-Recovered.csv'

    file_csv = wget.download(url, out=dir_save_csv.as_posix())
    df_out = pd.read_csv(file_csv)
    return df_out

def date_convert(list_in):
    """
    Convert data structure to make them more convient for plots.

    Parameters
    ----------
    list_in : list of str
        list of dates in 'mm/dd/yy' format.

    Returns
    -------
    list_out : list of str
        list of dates in 'Mon dd' format.

    """
    import numpy as np
    import datetime
    list_out = list_in.copy()
    for cc in np.arange(len(list_out)):
        date_time_str = list_out[cc]
        date_time_obj = datetime.datetime.strptime(date_time_str, '%m/%d/%y')
        month = date_time_obj.strftime("%b")
        day = date_time_obj.strftime("%d")
        list_out[cc] = month + '  ' + day
    return list_out


#%% this is where most things are done
    # click used to handle input arguments from command line.
import click
@click.command()
@click.option('--x_ax', default='cumsum', help='cumsum or diff (to show daily growth)')
@click.option('--y_ax', default='linear', help='linear or semilogy')
def main(x_ax, y_ax):
    """
    Simply the whole code. Added in a separate functio to use click.

    Parameters
    ----------
    x_ax : str, default 'cumsum'
        'cumsum' plot OR 'diff' for daily growth plot.
    y_ax : str, default 'linear'
        'linear' or 'semilogy'.

    Returns
    -------
    None.

    """
    import numpy as np
    import matplotlib.pyplot as plt
    from pathlib import Path
    import matplotlib

    #%% define folders
    dir_file = Path(__file__).resolve().parent

    dir_save_csv = Path(dir_file, 'COVID19_csv_files')
    dir_save_csv.mkdir(parents=True, exist_ok=True)

    dir_save_tex = Path(dir_file, 'output')
    dir_save_tex.mkdir(parents=True, exist_ok=True)

    #%% load data
    df_c = get_covid19_stat_df('c', dir_save_csv)
    df_r = get_covid19_stat_df('r', dir_save_csv)
    df_d = get_covid19_stat_df('d', dir_save_csv)

    list_col_nondata = ['Province/State', 'Country/Region', 'Lat', 'Long']
    list_col_data = [x for x in df_r.columns if not x in list_col_nondata]
    last_date = list_col_data[-1]
    # correct date format
    list_col_data_cor = date_convert(list_col_data)

    # sort all df based on last date values (descending)
    list_last_date_c = df_c.loc[:, last_date].tolist()
    indices_last_date_sorted = np.argsort(-1*np.array(list_last_date_c))
    df_c = df_c.loc[indices_last_date_sorted, :]
    df_r = df_r.loc[indices_last_date_sorted, :]
    df_d = df_d.loc[indices_last_date_sorted, :]


    # subset of dataset only for country/region with at least 100 confrimed cases
    df_c_subset = df_c.loc[df_c[last_date]>100]
    indices_df_c_subset = df_c_subset.index
    df_r_subset = df_r.loc[indices_df_c_subset]
    df_d_subset = df_d.loc[indices_df_c_subset]

    #%% sepcifiy type of output plots
    # y_ax = 'linear'  # linear or semilogy
    # x_ax = 'cumsum'  # cumsum or diff

    if x_ax == 'cumsum':
        str_dir = 'plots_cumsum_'
        file_tex_post = '_cumsum_'
    elif x_ax == 'diff':
        str_dir = 'plots_diff_'
        file_tex_post = '_diff_'

    if y_ax == 'linear':
        dir_save_plots = Path(dir_save_tex, str_dir + 'linear')
        file_tex_post = file_tex_post + 'linear.tex'
    elif y_ax == 'semilogy':
        dir_save_plots = Path(dir_save_tex, str_dir + 'semilogy')
        file_tex_post = file_tex_post + 'semilogy.tex'

    file_tex_template = Path(dir_save_tex, 'COVID19_tracker_template'+ file_tex_post)
    file_tex = Path(dir_save_tex, 'COVID19_tracker' + file_tex_post)
    dir_save_plots.mkdir(parents=True, exist_ok=True)

    import shutil
    shutil.copyfile(file_tex_template, file_tex)
    with open(file_tex, 'a') as my_tex:
        my_tex.write('')

    #%% define lists for world data (sum of all local data)
    list_r_sum = np.zeros(len(list_col_data))
    list_c_sum = np.zeros(len(list_col_data))
    list_d_sum =np.zeros(len(list_col_data))

    #%% matplotlib style
    plt.style.use('seaborn-darkgrid')
    font = {'family' : 'DejaVu Sans',
            'sans-serif' : 'Tahoma',
            'weight' : 'regular',
            'size'   : 22}
    # matplotlib.rc('grid', color='#316931', linewidth=1, linestyle='dotted')
    matplotlib.rc('font', **font)
    matplotlib.rc('lines', lw=3,)
    matplotlib.rc('xtick', labelsize=10)
    matplotlib.rc('ytick', labelsize=16)
    plt.style.use('seaborn-darkgrid')

    #%% loop over all selected rows
    for ind in indices_df_c_subset:
        list_r = [None] * len(list_col_data)
        list_c = [None] * len(list_col_data)
        list_d = [None] * len(list_col_data)
        list_c = [None] * len(list_col_data)

        for idx, col in enumerate(list_col_data):
            list_r[idx] = df_r_subset.loc[ind, col]
            list_c[idx] = df_c_subset.loc[ind, col]
            list_d[idx] = df_d_subset.loc[ind, col]


        figsize = (13,8)
        fig, ax = plt.subplots(figsize=figsize)
        fig.subplots_adjust(bottom=0.15, top=0.90, left=0.1, right = 0.9)

        if x_ax == 'cumsum':
            tt = np.arange(len(list_c))
            xticklabels = list_col_data_cor
            list_c_plot = list_c
            list_r_plot = list_r
            list_d_plot = list_d
            str_dir = 'plots_cumsum_'
        elif x_ax == 'diff':
            tt = np.arange(len(list_c)-1)+1
            xticklabels = list_col_data_cor[1:]
            list_c_plot = np.diff(list_c)
            list_r_plot = np.diff(list_r)
            list_d_plot = np.diff(list_d)
            str_dir = 'plots_diff_'

        if y_ax == 'linear':
            ax.plot(tt, list_c_plot, label='Confimed')
            ax.plot(tt, list_r_plot, label='Recovered')
            ax.plot(tt, list_d_plot, label='Death')
            dir_save_plots = Path(dir_save_tex, str_dir + 'linear')
        elif y_ax == 'semilogy':
            ax.semilogy(tt, list_c_plot, label='Confimed')
            ax.semilogy(tt, list_r_plot, label='Recovered')
            ax.semilogy(tt, list_d_plot, label='Death')
            dir_save_plots = Path(dir_save_tex, str_dir + 'semilogy')
        dir_save_plots.mkdir(parents=True, exist_ok=True)
        # plt.plot(list_c, label='All Confrimed')
        ax.legend()
        # ax.grid()
        file_str1 = str(df_c_subset.loc[ind, 'Country/Region'])
        file_str2 = str(df_c_subset.loc[ind, 'Province/State'])
        if file_str1 == 'Iran (Islamic Republic of)':
            file_str1 = 'Iran'   #  Let's get rid of Islamic Republic.
        else:  # exclude Iran from world data, casue official stat is not reliable
            list_r_sum = list_r_sum + np.array(list_r)
            list_c_sum = list_c_sum + np.array(list_c)
            list_d_sum = list_d_sum + np.array(list_d)
        file_str1_title = file_str1

        if (file_str2) == 'nan':  # no region for a country
            file_str2 = ''
            file_str2_title = ''
        else:
            file_str2_title = ' --- ' + file_str2
            file_str2 = '_' + file_str2


        file_str1 = file_str1.replace(" ", "")
        file_str1 = file_str1.replace(",", "_")
        file_str2 = file_str2.replace(" ", "")
        file_str2 = file_str2.replace(",", "_")
        print('-------------------------------')
        print(file_str1_title + file_str2_title)

        beamer_title = file_str1_title + file_str2_title
        title_tex1 = 'Confirmed: '+ str(int(list_c_plot[-1]))
        title_tex2 = 'Recovered: '+ str(int(list_r_plot[-1]))
        title_tex3 = 'Death: '+ str(int(list_d_plot[-1]))

        if x_ax == 'cumsum':
            if list_d[-1] == 0:
                title_tex4 = ''
            else:
                title_tex4 = '\nDeath/Confirmed: '+ "{:2.2f}".format(list_d[-1]*100/list_c[-1])+'%'
        else:
           title_tex4 = '\nAbove mentioned numbers show the difference between today and yesterday.'

        title_tex = title_tex1 + ' --- ' + title_tex2 + ' --- ' + title_tex3 \
                    + title_tex4
        if file_str1 == 'Iran':
            beamer_title = 'Iran: \nThe official data coming from Iran is unreliable.'
        ax.set_title(title_tex, fontsize=20)
        ax.set_xticks(tt)
        ax.set_xticklabels(xticklabels, rotation=90)
        filesave = Path(file_str1 + file_str2 + '.png')

        beamer_frame = make_beamer_slide_type1(beamer_title, filesave.stem, dir_save_plots.stem)
        with open(file_tex, 'a') as my_tex:
            my_tex.write(beamer_frame)

        if file_str1 == 'Iran':
            file_str1_title = file_str1 + \
            '\nThe official data coming from Iran are completely unreliable \n(as detailed in a seperate file)'

        filesave1 = Path(dir_save_plots, filesave)
        fig.savefig(filesave1, figsize=figsize)

        plt.close('all')

    #%% plot for world population

    figsize = (13,8)
    fig, ax = plt.subplots(figsize=figsize)
    fig.subplots_adjust(bottom=0.15, top=0.90, left=0.1, right = 0.9)
    # fig.tight_layout()
    if x_ax == 'cumsum':
        tt = np.arange(len(list_c))
        xticklabels = list_col_data_cor
        list_c_plot = list_c_sum
        list_r_plot = list_r_sum
        list_d_plot = list_d_sum
    elif x_ax == 'diff':
        tt = np.arange(len(list_c)-1)+1
        xticklabels = list_col_data_cor[1:]
        list_c_plot = np.diff(list_c_sum)
        list_r_plot = np.diff(list_r_sum)
        list_d_plot = np.diff(list_d_sum)

    if y_ax == 'linear':
        ax.plot(tt, list_c_plot, label='Confimed')
        ax.plot(tt, list_r_plot, label='Recovered')
        ax.plot(tt, list_d_plot, label='Death')
    elif y_ax == 'semilogy':
        ax.semilogy(tt, list_c_plot, label='Confimed')
        ax.semilogy(tt, list_r_plot, label='Recovered')
        ax.semilogy(tt, list_d_plot, label='Death')

    ax.legend()

    title_tex1 = 'Confirmed: '+ str(int(list_c_plot[-1]))
    title_tex2 = 'Recovered: '+ str(int(list_r_plot[-1]))
    title_tex3 = 'Death: '+ str(int(list_d_plot[-1]))

    if x_ax == 'cumsum':
        title_tex4 = '\nDeath/Confirmed: '+ "{:2.2f}".format(list_d_sum[-1]*100/list_c_sum[-1])+'%'
    else:
        title_tex4 = '\nLast day data'

    title_tex = title_tex1 + ' --- ' + title_tex2 + ' --- ' + title_tex3 \
                + title_tex4
    beamer_title = 'World Aggregate (Excluding Iran)'
    ax.set_title(title_tex, fontsize=20)
    ax.set_xticks(tt)
    # correct date format
    list_col_data_cor = date_convert(list_col_data)
    ax.set_xticklabels(list_col_data_cor, rotation=90)
    my_file = '00_World' + '.png'
    filesave1 = Path(dir_save_plots, my_file)
    beamer_frame = make_beamer_slide_type1(beamer_title, filesave1.stem, dir_save_plots.stem)
    with open(file_tex, 'a') as my_tex:
        my_tex.write(beamer_frame)

    fig.savefig(filesave1, figsize=figsize)
    plt.close('all')
    #%% completing latex file
    with open(file_tex, 'a') as my_tex:
        my_tex.write('\\end{document}')

if __name__ == '__main__':
    main()