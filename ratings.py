import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.transforms import Bbox
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap

from bs4 import BeautifulSoup as bs
import requests

from ipypb import track


"""
Data Retrieval
"""
show_id_2_url = lambda show_id: f'https://www.imdb.com/title/{show_id}'

#def show_id_2_most_recent_season(show_id):
#    show_url = show_id_2_url(show_id)
#    r = requests.get(show_url)
#    assert r.status_code==200, f'Request failed with code: {r.status_code}'

#    soup = bs(r.content, features='lxml')
#    season_year_links = soup.find('div', attrs={'class':'seasons-and-year-nav'}).find_all('a')
#    most_recent_season = int([tag.text for tag in season_year_links][0])

#    return most_recent_season

season_2_url = lambda show_id, season: f'https://www.imdb.com/title/{show_id}/episodes/_ajax?year={season}'

def season_2_episode_ratings(show_id, year):
    season_url = season_2_url(show_id, year)
    r = requests.get(season_url)
    assert r.status_code==200, f'Request failed with code: {r.status_code}'

    soup = bs(r.content, features='lxml')
    episode_ratings = (soup
                       .find('div', attrs={'class', 'list detail eplist'})
                       .find_all('div', {'class':'ipl-rating-widget'}))
    ratings = [float(rating.find('span', attrs={'class':'ipl-rating-star__rating'}).text) 
               for rating in episode_ratings]

    return ratings

def show_id_2_ratings_df(show_id):
    df_ratings = pd.DataFrame(index=range(100))
    #most_recent_season = show_id_2_most_recent_season(show_id)
    most_recent_season = 2020

    for season in track(range(2000, most_recent_season+1)):
        ratings = season_2_episode_ratings(show_id, season)
        df_ratings[season] = pd.Series(ratings, dtype='float64')

    df_ratings = (df_ratings
                  .dropna(how='all', axis=0)
                  .dropna(how='all', axis=1)
                 ) 
    
    df_ratings.index += 1

    return df_ratings


"""
Plotting
"""
def hide_spines(ax, positions=['top', 'right']):
    """
    Pass a matplotlib axis and list of positions with spines to be removed
    
    args:
        ax:          Matplotlib axis object
        positions:   Python list e.g. ['top', 'bottom']
    """
    assert isinstance(positions, list), 'Position must be passed as a list '
    
    for position in positions:
        ax.spines[position].set_visible(False)
        
def colors_n_segments_2_pairs(colors, color_segment_starts):
    color_loc_pairs = []

    for idx, color in enumerate(colors):
        if idx == 0:
            color_loc_pairs += [(color_segment_starts[idx], color)]
        else:
            color_loc_pairs += [(color_segment_starts[idx], colors[idx-1])]
            color_loc_pairs += [(color_segment_starts[idx], color)]

    color_loc_pairs += [(1, colors[-1])]

    return color_loc_pairs

def create_cm(colors, color_segment_starts, name=''):
    color_loc_pairs = colors_n_segments_2_pairs(colors, color_segment_starts)
    cm = LinearSegmentedColormap.from_list(name, color_loc_pairs)

    return cm

def data_point_2_str(data_point):
    if isinstance(data_point, np.ma.core.MaskedConstant):
        s = ''
    else:
        s = str(data_point)
        
    return s

def data_point_2_font_dict(data_point, fontsize=8, color_threshold=6.5, colors=['white', 'black']):
    if data_point < color_threshold:
        font_dict = {'color': colors[0], 
                     'size' : fontsize,
                    }
    else:        
        font_dict = {'color': colors[1],
                     'size' : fontsize,
                    }
        
    return font_dict
 
def plot_ratings_ax(ax, df_ratings, cm, background, xlabel='Season', ylabel='Episode', grid_color='white', text_fontsize=10, label_fontsize=12, x_axis_top=True, text_color_threshold=6.5, xlabel_color='k', ylabel_color='k', value_colors=['white', 'black'], tick_color='k'):
    data = df_ratings.fillna(0).values
    data = np.ma.masked_equal(data, 0)

    ax.set_facecolor(background)

    heatmap = ax.pcolor(data, cmap=cm, edgecolors=grid_color, linewidths=1,
                        antialiased=True, vmin=0, vmax=10)

    for y in range(data.shape[0]):
        for x in range(data.shape[1]):
            ax.text(x + 0.5, y + 0.5, data_point_2_str(data[y, x]),
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontdict=data_point_2_font_dict(data[y, x], fontsize=text_fontsize, color_threshold=text_color_threshold, colors=value_colors),
                   )

    ## Cleaning axis positions and directions
    ax.invert_yaxis()
    
    if x_axis_top == True:
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top') 

    ## Adding axis labels
    label_font = {'weight': 'bold',
                  'size': label_fontsize,
                 }
    ax.set_xlabel(xlabel, labelpad=13, fontdict=label_font, color=xlabel_color)
    ax.set_ylabel(ylabel, labelpad=13, fontdict=label_font, color=ylabel_color)

    ax.set_xticks(np.arange(len(df_ratings.columns)) + 0.5)
    ax.set_xticklabels(df_ratings.columns, ha='center', fontdict={'size':text_fontsize}, color=tick_color)
    ax.set_yticks(np.arange(len(df_ratings.index)) + 0.5)
    ax.set_yticklabels(df_ratings.index, ha='center', fontdict={'size':text_fontsize}, color=tick_color)

    ax.tick_params(axis='both', which='major', labelsize=10, left=False, top=False, bottom=False)
    ax.tick_params(axis='y', pad=10)
    hide_spines(ax, positions=['top', 'bottom', 'left', 'right'])
    
def plot_info_panel(ax, background_img_path, rating_colors, rating_labels, lgnd_edge_color='white', label_fontsize=4.5, title_fontsize=5, bbox_to_anchor=[0.5, 0.15], label_color='k'):
    ## Plotting background image
    img = plt.imread(background_img_path)
    ax.imshow(img)

    ## Creating legend
    patches = [mpatches.Patch(facecolor=color, label=label, edgecolor=lgnd_edge_color, linewidth=0.5) 
               for color, label in zip(rating_colors, rating_labels)]

    leg = ax.legend(handles=patches, ncol=2, frameon=False, handlelength=0.7, bbox_to_anchor=bbox_to_anchor, 
                    loc='center', prop={'size':label_fontsize}, title=r'$\bf{Rating\ Category}$', title_fontsize=title_fontsize)
    
    for text in leg.get_texts():
        plt.setp(text, color=label_color)
        
    leg.set_title(r'$\bf{Rating\ Category}$', prop={'size':title_fontsize})

    ## Cleaning axis ticks
    ax.set_xticks([])
    ax.set_yticks([])
    hide_spines(ax, positions=['top', 'bottom', 'left', 'right'])