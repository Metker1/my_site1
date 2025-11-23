team_home = {
    'name': 'Команда Хозяев',
    'rating': 21,  # рейтинг команды
    'avg_points': 82.8,  # среднее очков за игру
    'win_pct_last10': 33.33,  # процент побед за последние 10 игр
    'home_advantage': True,  # домашняя игра
}

team_away = {
    'name': 'Команда Гостей',
    'rating': 28,
    'avg_points': 87.4,
    'win_pct_last10': 50,
    'home_advantage': False,
}

match_conditions = {
    'location': 'home',  # или 'away'
}


# Простая модель оценки вероятности победы
def calculate_win_probability(team1, team2, conditions):
    # Базовая оценка на основе рейтинга
    rating_diff = team1['rating'] - team2['rating']

    # Учитываем домашний статус
    home_advantage = 0
    if conditions['location'] == 'home':
        if team1['home_advantage']:
            home_advantage += 0.05
        if team2['home_advantage']:
            home_advantage -= 0.05
    elif conditions['location'] == 'away':
        if team2['home_advantage']:
            home_advantage += 0.05
        if team1['home_advantage']:
            home_advantage -= 0.05

    # Учитываем среднее очков
    points_diff = (team1['avg_points'] - team2['avg_points']) * 0.2

    # Учитываем последние 10 игр
    recent_win_diff = (team1['win_pct_last10'] - team2['win_pct_last10']) * 0.3

    # Итоговая оценка вероятности
    score = 0.5 + 0.02 * rating_diff + home_advantage + points_diff + recent_win_diff

    # Ограничиваем значение
    probability_team1_win = max(0, min(1, score))
    return probability_team1_win


def main():
    prob_team1 = calculate_win_probability(team_home, team_away, match_conditions)
    print(f"Вероятность победы {team_home['name']}: {prob_team1:.2%}")
    print(f"Вероятность победы {team_away['name']}: {(1 - prob_team1):.2%}")

    if prob_team1 > 0.5:
        print(f"Модель предсказывает победу {team_home['name']}.")
    else:
        print(f"Модель предсказывает победу {team_away['name']}.")


if __name__ == "__main__":
    main()