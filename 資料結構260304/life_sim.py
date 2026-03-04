# -*- coding: utf-8 -*-
import random
from flask import Flask, render_template, request

app = Flask(__name__)

# 在 Jinja2 中添加 min 函數
app.jinja_env.globals.update(min=min)

MAX_DAYS = 30


def random_event(money, study, mood, health, log):
    """每天有機會觸發一個隨機事件，回傳更新後的狀態與日誌。"""
    if random.random() < 0.3:
        log.append("【隨機事件觸發】")
        event = random.choice(["中獎", "感冒", "朋友揪出去玩", "靈感爆發"])
        if event == "中獎":
            bonus = random.randint(100, 300)
            money += bonus
            mood += 5
            log.append(f"你刮刮樂中獎，多了 {bonus} 元，心情變好！")
        elif event == "感冒":
            health -= 10
            mood -= 5
            log.append("你不小心感冒了，健康下降，心情也變差。")
        elif event == "朋友揪出去玩":
            mood += 10
            money -= 50
            log.append("朋友揪你出去玩，花了點錢，但心情變超好！")
        elif event == "靈感爆發":
            study += 8
            log.append("今天思緒超清晰，讀書效率爆表，學習力大幅提升！")
    return money, study, mood, health, log


def limit_status(money, study, mood, health):
    """把各項數值限制在合理範圍內。"""
    mood = max(0, min(mood, 100))
    health = max(0, min(health, 100))
    study = max(0, study)
    money = max(-9999, money)
    return money, study, mood, health


def ending_text(money, study, mood, health):
    """根據最終狀態給出結局文字。"""
    if health <= 20:
        return "結局：身體累壞了。你太拚命，最後只好住院休養。"
    elif study >= 80 and mood >= 60:
        return "結局：人生勝利組。你兼顧讀書與生活，考上理想學校又不失快樂。"
    elif money >= 2000 and mood >= 40:
        return "結局：小小財富自由。雖然不是頂尖學霸，但你存到一筆不小的錢，生活還算愜意。"
    elif study >= 80 and mood < 40:
        return "結局：高分低樂。你成績很好，但長期壓力過大，常常覺得空虛。"
    elif mood >= 80:
        return "結局：開心就好派。雖然錢不多、成績普通，但你每天都活得超開心。"
    else:
        return "結局：平凡人生。沒有特別耀眼，也沒有太慘，這或許就是大多數人的日常。"


@app.route("/", methods=["GET", "POST"])
def index():
    # 第一次進來，建立初始狀態
    if request.method == "GET":
        state = {
            "day": 1,
            "money": 500,
            "study": 0,
            "mood": 60,
            "health": 80,
            "logs": ["遊戲開始！你有 30 天時間決定每天要做什麼。"],
            "game_over": False,
            "ending": ""
        }
        return render_template("life.html", **state)

    # 之後每次按按鈕會送出 POST，把狀態帶回來
    try:
        day = int(request.form.get("day", "1"))
        money = int(request.form.get("money", "500"))
        study = int(request.form.get("study", "0"))
        mood = int(request.form.get("mood", "60"))
        health = int(request.form.get("health", "80"))
    except ValueError:
        # 萬一表單被亂改，重新開始遊戲，避免程式當掉
        day, money, study, mood, health = 1, 500, 0, 60, 80

    raw_logs = request.form.get("logs", "")
    logs = raw_logs.split("\n") if raw_logs else []
    choice = request.form.get("choice", "")
    restart = request.form.get("restart", "")

    # 檢查是否要重新開始
    if restart:
        state = {
            "day": 1,
            "money": 500,
            "study": 0,
            "mood": 60,
            "health": 80,
            "logs": ["遊戲開始！你有 30 天時間決定每天要做什麼。"],
            "game_over": False,
            "ending": ""
        }
        return render_template("life.html", **state)

    # 只要還沒超過天數而且有選動作，就模擬一天
    if choice and day <= MAX_DAYS:
        logs.append(f"=== 第 {day} 天，你選擇了動作 {choice} ===")
        if choice == "1":
            gain = random.randint(5, 12)
            study += gain
            mood -= random.randint(3, 8)
            health -= random.randint(2, 6)
            logs.append(f"你認真讀了一整天書，學習力 +{gain}，但心情與健康稍微下降。")
        elif choice == "2":
            earn = random.randint(150, 300)
            money += earn
            mood -= random.randint(2, 6)
            health -= random.randint(3, 7)
            logs.append(f"你去打工賺了 {earn} 元，但有點累、心情也稍微下降。")
        elif choice == "3":
            mood += random.randint(4, 10)
            health += random.randint(6, 12)
            logs.append("你決定好好休息，心情與健康恢復不少。")
        elif choice == "4":
            cost = random.randint(80, 200)
            money -= cost
            mood += random.randint(10, 20)
            health -= random.randint(0, 4)
            logs.append(f"你和朋友出去玩，花了 {cost} 元，但玩得超開心！")
        else:
            logs.append("你猶豫了一整天，什麼也沒做，時間就這樣過去了……")

        money, study, mood, health, logs = random_event(money, study, mood, health, logs)
        money, study, mood, health = limit_status(money, study, mood, health)
        day += 1

    game_over = False
    ending = ""

    # 檢查是否結束
    if health <= 0:
        logs.append("你的健康歸零，被送去醫院住院，只好提早結束這 30 天的人生計畫。")
        game_over = True
    elif mood <= 0:
        logs.append("你的心情崩潰到谷底，需要長時間休養，只好提早結束這 30 天的人生計畫。")
        game_over = True
    elif day > MAX_DAYS:
        logs.append("30 天結束。來看看你的人生總結吧！")
        game_over = True

    if game_over:
        ending = ending_text(money, study, mood, health)

    state = {
        "day": day if not game_over else MAX_DAYS,
        "money": money,
        "study": study,
        "mood": mood,
        "health": health,
        "logs": logs,
        "game_over": game_over,
        "ending": ending
    }
    return render_template("life.html", **state)


if __name__ == "__main__":
    # 用 5000 port，不會和 XAMPP 的 80 port 衝突
    app.run(debug=True, host="127.0.0.1", port=5000)
