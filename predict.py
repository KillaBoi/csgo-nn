import scrape
import process
import database as db
import pickle
import trueskill
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier


def main():
    scrape.find_new_games()
    scrape.match_details()
    teams = process.process_totals()

    matches = scrape.upcoming_matches()
    mlp = pickle.load(open('model/mlp_model.pkl', 'rb'))

    X,y = db.get_training_csv()

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    for m in matches:
        try:
            a_ts, b_ts = trueskill.rate_1vs1(teams[m[0]]['stats']['ts'],teams[m[1]]['stats']['ts'])

            g = {
                'a_score': teams[m[0]]['stats']['score'],
                'b_score': teams[m[1]]['stats']['score'],
                'a_elo': teams[m[0]]['stats']['elo'],
                'b_elo': teams[m[1]]['stats']['elo'],
                'a_games': teams[m[0]]['stats']['games'],
                'b_games': teams[m[1]]['stats']['games'],
                'a_win': teams[m[0]]['stats']['wins'],
                'b_win': teams[m[1]]['stats']['wins'],
                'a_vs_record': teams[m[0]]['teams'][m[1]],
                'b_vs_record': teams[m[1]]['teams'][m[0]],
                'a_momentum': teams[m[0]]['stats']['momentum'],
                'b_momentum': teams[m[1]]['stats']['momentum'],
                'a_rating': teams[m[0]]['stats']['rating'],
                'b_rating': teams[m[1]]['stats']['rating'],
                'a_ts': process.win_probability(a_ts,b_ts),
                'b_ts': process.win_probability(b_ts,a_ts),
            }

            vs_games = g['a_vs_record'] + g['b_vs_record']

            match = [
                process.stat_avg_diff(g['a_win'], g['a_games'] ,g['b_win'], g['b_games']),
                round(g['a_elo'] - g['b_elo'],2),
                process.stat_avg_diff(g['a_score'], g['a_games'] ,g['b_score'], g['b_games']),
                g['a_momentum'] - g['b_momentum'],
                process.stat_avg_diff(g['a_vs_record'], vs_games ,g['b_vs_record'], vs_games), 
                process.stat_avg_diff(g['a_rating'], g['a_games'] ,g['b_rating'], g['b_games']),
                g['a_ts'],
            ]
           
            match = scaler.transform([match])

            outcome = mlp.predict_proba(match)
            a_pred = round(outcome[0][1],2)*100
            b_pred = round(outcome[0][0],2)*100
            print(m[0],'(',a_pred,')',' vs ',m[1],'(',b_pred,')')
        except Exception as e:
            pass
            #print("### Error ### " ,e)


if __name__ == "__main__":
    main()