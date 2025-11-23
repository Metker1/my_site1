import math

# Вводные данные о двух игроках и условиях
player1 = {
    'name': 'Игрок 1',
    'ranking': 49,  # мировой рейтинг
    'avg_aces': 10,  # среднее число эйсов за матч
    'win_pct': 78,  # процент выигранных очков на подаче
    'match_history': 21,  # победы / проигрыши за последний год
    'surface_pref': ['хард'],  # предпочтительная поверхность
}

player2 = {
    'name': 'Игрок 2',
    'ranking': 82,
    'avg_aces': 7,
    'win_pct': 54,
    'match_history': 9,
    'surface_pref': ['травяной', 'жёсткий'],
}

match_conditions = {
    'surface': 'жёсткий',  # текущая поверхность
}


# Простая модель оценки вероятности победы
def calculate_win_probability(p1, p2, conditions):
    # Рейтинг — более низкое число означает лучший рейтинг
    ranking_diff = p2['ranking'] - p1['ranking']

    # Учитываем предпочтения поверхности
    surface_advantage = 0
    if conditions['surface'] in p1['surface_pref']:
        surface_advantage += 0.05
    if conditions['surface'] in p2['surface_pref']:
        surface_advantage -= 0.05

    # Простейшая модель, основанная на рейтинге и статистике
    score = 0.5
    score += 0.02 * ranking_diff  # рейтинг
    score += 0.3 * (p1['win_pct'] - p2['win_pct'])  # процент выигранных очков
    score += 0.1 * (p1['avg_aces'] - p2['avg_aces'])  # среднее эйсов

    score += surface_advantage

    # Ограничение вероятности в диапазоне 0-1
    probability_p1 = max(0, min(1, score))
    return probability_p1


def main():
    prob_p1 = calculate_win_probability(player1, player2, match_conditions)
    print(f"Вероятность победы {player1['name']}: {prob_p1:.2%}")
    print(f"Вероятность победы {player2['name']}: {(1 - prob_p1):.2%}")

    if prob_p1 > 0.5:
        print(f"Модель предсказывает победу {player1['name']}.")
    else:
        print(f"Модель предсказывает победу {player2['name']}.")


if __name__ == "__main__":
    main()