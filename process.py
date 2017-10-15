from __future__ import division
import math
import re
import os
import csv
import progressbar
from math import sqrt
import trueskill
from trueskill import BETA
from trueskill.backends import cdf
import database as db

MAX_VS_MATCHES = 40
MIN_GAMES = 5
WIN_RATING_SCORE = 5
LOSS_MOMENTUM = 2


def elo(winner_elo, loser_elo):
    k = 50
    r1 = math.pow(10, float(winner_elo / 400))
    r2 = math.pow(10, float(loser_elo / 400))
    r1_coe = r1 / float(r1 + r2)
    r2_coe = 1 - r1_coe
    e1 = round(winner_elo + k * (1 - r1_coe))
    e2 = round(loser_elo + k * (0 - r2_coe))
    return e1, e2


def win_probability(player_rating, opponent_rating):
    delta_mu = player_rating.mu - opponent_rating.mu
    denom = sqrt(2 * (BETA * BETA) + pow(player_rating.sigma, 2) + pow(opponent_rating.sigma, 2))
    return cdf(delta_mu / denom)


def process_totals():
    db.clear_table('processed')
    teams = setup_teams()
    games = db.get_all('raw','id','DESC')
    match = {}
    ts = trueskill.TrueSkill(draw_probability=0)
    add_list = []

    bar = progressbar.ProgressBar(max_value=len(games))
    print("\nProcessing Team Totals:")
    cnt=0
    for g in games:
        try:
            
            bar.update(cnt)
            cnt+=1
            if g['a_score'] != g['b_score']:
                if teams[g['team_a']]['stats']['games'] > MIN_GAMES and teams[g['team_b']]['stats']['games'] > MIN_GAMES:
                    match = {
                        'team_a': g['team_a'],
                        'team_b': g['team_b'],
                        'a_score': teams[g['team_a']]['stats']['score'],
                        'b_score': teams[g['team_b']]['stats']['score'],
                        'a_elo': teams[g['team_a']]['stats']['elo'],
                        'b_elo': teams[g['team_b']]['stats']['elo'],
                        'a_games': teams[g['team_a']]['stats']['games'],
                        'b_games': teams[g['team_b']]['stats']['games'],
                        'a_win': teams[g['team_a']]['stats']['wins'],
                        'b_win': teams[g['team_b']]['stats']['wins'],
                        'a_map_win': teams[g['team_a']]['map_wins'][g['map']],
                        'b_map_win': teams[g['team_b']]['map_wins'][g['map']],
                        'a_map_played': teams[g['team_a']]['map_games'][g['map']],
                        'b_map_played': teams[g['team_b']]['map_games'][g['map']],
                        'a_vs_record': teams[g['team_a']]['teams'][g['team_b']],
                        'b_vs_record': teams[g['team_b']]['teams'][g['team_a']],
                        'a_momentum': teams[g['team_a']]['stats']['momentum'],
                        'b_momentum': teams[g['team_b']]['stats']['momentum'],
                        'a_adr': teams[g['team_a']]['stats']['adr'],
                        'b_adr': teams[g['team_b']]['stats']['adr'],
                        'a_kast': teams[g['team_a']]['stats']['kast'],
                        'b_kast': teams[g['team_b']]['stats']['kast'],
                        'a_kd': round(teams[g['team_a']]['stats']['kills'] / teams[g['team_a']]['stats']['deaths'],4) ,
                        'b_kd': round(teams[g['team_b']]['stats']['kills'] / teams[g['team_b']]['stats']['deaths'],4) ,
                        'a_rating': teams[g['team_a']]['stats']['rating'],
                        'b_rating': teams[g['team_b']]['stats']['rating'],
                        'a_trueskill': win_probability(teams[g['team_a']]['stats']['ts'], teams[g['team_b']]['stats']['ts']),
                        'b_trueskill': win_probability(teams[g['team_b']]['stats']['ts'], teams[g['team_a']]['stats']['ts']),
                        'outcome': g['outcome'],
                        'date': g['date']
                    }

                    db.insert_game('processed', match)

                teams[g['team_a']]['stats']['games'] += 1
                teams[g['team_b']]['stats']['games'] += 1

                teams[g['team_a']]['stats']['score'] += g['a_score']
                teams[g['team_b']]['stats']['score'] += g['b_score']

                teams[g['team_a']]['map_games'][g['map']] += 1
                teams[g['team_b']]['map_games'][g['map']] += 1

                teams[g['team_a']]['stats']['adr'] += g['a_adr']
                teams[g['team_b']]['stats']['adr'] += g['b_adr']

                teams[g['team_a']]['stats']['rating'] += g['a_rating']
                teams[g['team_b']]['stats']['rating'] += g['b_rating']

                teams[g['team_a']]['stats']['kills'] += g['a_kills']
                teams[g['team_b']]['stats']['kills'] += g['b_kills']

                teams[g['team_a']]['stats']['deaths'] += g['a_deaths']
                teams[g['team_b']]['stats']['deaths'] += g['b_deaths']

                teams[g['team_a']]['stats']['kast'] += g['a_kast']
                teams[g['team_b']]['stats']['kast'] += g['b_kast']

                if g['outcome'] == 1:
                    winner, loser = 'team_a','team_b'
                    win_score, lose_score = g['a_score'],g['b_score']
                else:
                    winner, loser = 'team_b','team_a'
                    win_score, lose_score = g['b_score'],g['a_score']

                
                teams[g[winner]]['stats']['ts'], teams[g[loser]]['stats']['ts'] = trueskill.rate_1vs1(teams[g[winner]]['stats']['ts'],teams[g[loser]]['stats']['ts'])
                teams[g[winner]]['stats']['elo'], teams[g[loser]]['stats']['elo'] = elo(teams[g[winner]]['stats']['elo'], teams[g[loser]]['stats']['elo'])
                teams[g[winner]]['stats']['wins'] += (1 + math.log(win_score - lose_score))
                teams[g[loser]]['teams'][g[winner]] -= 1
                
                if teams[g[loser]]['teams'][g[winner]] < 0:
                    teams[g[loser]]['teams'][g[winner]] = 0
                
                if teams[g[winner]]['teams'][g[loser]] > MAX_VS_MATCHES:
                    teams[g[winner]]['teams'][g[loser]] = MAX_VS_MATCHES
                
                teams[g[winner]]['teams'][g['team_a']] += 1
                teams[g[winner]]['map_wins'][g['map']] += (1 + math.log(win_score - lose_score))
                teams[g[winner]]['stats']['rating']+=WIN_RATING_SCORE
                teams[g[loser]]['stats']['momentum'] = round(teams[g[loser]]['stats']['momentum']/LOSS_MOMENTUM,4)
                teams[g[winner]]['stats']['momentum'] += 1 
                
        except Exception as e:
            print("### Error:",e)
            pass
 
    return teams


def make_training_set():
    print("\n\nCreating Training Set") 
    db.clear_table('games')
    games = db.get_all('processed', 'id')
    bar = progressbar.ProgressBar(max_value=len(games))
    cnt=0
    for g in games:
        bar.update(cnt)
        cnt+=1
        vs_games = g['a_vs_record'] + g['b_vs_record']
        match = {
            'wins': stat_avg_diff(g['a_win'], g['a_games'] ,g['b_win'], g['b_games']),
            'map_score': stat_avg_diff(g['a_map_win'], g['a_map_played'] ,g['b_map_win'], g['b_map_played']),
            'elo': round(g['a_elo'] - g['b_elo'],2),
            'vs': stat_avg_diff(g['a_vs_record'], vs_games ,g['b_vs_record'], vs_games), 
            'score': stat_avg_diff(g['a_score'], g['a_games'] ,g['b_score'], g['b_games']),
            'momentum': g['a_momentum'] - g['b_momentum'],
            'kd': stat_avg_diff(g['a_kd'], g['a_games'] ,g['b_kd'], g['b_games']),
            'kast': stat_avg_diff(g['a_kast'], g['a_games'] ,g['b_kast'], g['b_games']),
            'rating': stat_avg_diff(g['a_rating'], g['a_games'] ,g['b_rating'], g['b_games']),
            'adr': stat_avg_diff(g['a_adr'], g['a_games'] ,g['b_adr'], g['b_games']),
            'ts': g['a_trueskill'],
            'outcome':g['outcome'],
            'date':g['date']
        }

        db.insert_game('games',match)


def stat_avg_diff(a_stat, a_games ,b_stat, b_games):
    if a_games == 0:
        a_avg = 0
    else:
        a_avg = a_stat/a_games

    if b_games == 0:
        b_avg = 0
    else:
        b_avg = b_stat/b_games

    diff = a_avg - b_avg
    return round(diff,4)


def setup_teams():
    teams = {}
    vs_teams = {}
    maps ={'cbl': 0, 'cch': 0, 'd2': 0, 'inf': 0,'mrg': 0, 'nuke': 0, 'ovp': 0, 'tcn': 0, 'trn': 0, 'season': 0}
    games = db.get_all('teams', 'id')
    for g in games:
        teams[g['team']] = MAX_VS_MATCHES / 2
        vs_teams[g['team']] = {'teams': 0, 'stats': 0, 'map_wins': 0, 'map_games': 0}

    for t in teams:
        vs_teams[t]['teams'] = teams
        vs_teams[t]['stats'] = {'elo': 1000, 'games': 0, 'wins': 0, 'score': 0,'momentum':0,'adr':0,'rating':0,'kills':0,'deaths':0,'kast':0,'ts':trueskill.Rating()}
        vs_teams[t]['map_wins'] = maps
        vs_teams[t]['map_games'] = maps

    return vs_teams


def export_training_set():
    os.unlink('data/training.csv')
    csv_columns = ['wins','elo','score','momentum','vs','rating','ts','outcome']
    games = db.get_all('games','id','desc')
    with open('data/training.csv', 'a', newline='') as c:
        full_write = csv.DictWriter(c, fieldnames=csv_columns)
        for g in games:
            del g['Id']
            del g['date']
            del g['kd']
            del g['kast']
            del g['adr']
            del g['map_score']
            full_write.writerow(g)


def main():
    process_totals()
    make_training_set()
    export_training_set()


if __name__ == "__main__":
    main()