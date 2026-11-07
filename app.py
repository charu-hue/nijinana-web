import os
import json
import random  # シャッフル用に必須です！
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import db, User, Card, Deck

# ★作成した効果データベースを読み込む
from card_effects import CARD_EFFECTS_DEF

rooms_data = {}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "nijinana_secret_key")

# クラウド環境のURLを取得（未設定ならローカルのsqliteを使用）
db_uri = os.environ.get("DATABASE_URL", "sqlite:///cards.db")
# SQLAlchemyの仕様に合わせてURLの先頭を修正
if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==========================================
# 画面ルーティング
# ==========================================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if "login" in request.form:
            username = request.form.get("username")
            password = request.form.get("password")
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for("index"))
            flash("ユーザー名かパスワードが間違っています。", "error")
        elif "register" in request.form:
            username = request.form.get("reg_username")
            password = request.form.get("reg_password")
            if User.query.filter_by(username=username).first():
                flash("そのユーザー名は既に使用されています。", "error")
            else:
                hashed_pw = generate_password_hash(password)
                new_user = User(username=username, password_hash=hashed_pw)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/decks")
@login_required
def decks_view():
    return render_template("decks.html")


@app.route("/deckbuilder")
@login_required
def deckbuilder():
    return render_template("deckbuilder.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/play")
@login_required
def play():
    return render_template("playroom.html")


# ==========================================
# APIエンドポイント
# ==========================================
@app.route("/api/cards", methods=["GET"])
def get_cards():
    cards = Card.query.all()
    return jsonify([c.to_dict() for c in cards])


@app.route("/api/decks", methods=["GET", "POST"])
@login_required
def handle_decks():
    if request.method == "POST":
        data = request.json
        new_deck = Deck(
            name=data["name"], cards=json.dumps(data["cards"]), user_id=current_user.id
        )
        db.session.add(new_deck)
        db.session.commit()
        return jsonify({"status": "success", "deck_id": new_deck.id}), 201

    if request.method == "GET":
        decks = Deck.query.filter_by(user_id=current_user.id).all()
        return jsonify([d.to_dict() for d in decks])


@app.route("/api/decks/<int:deck_id>", methods=["PUT", "DELETE"])
@login_required
def handle_single_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return jsonify({"error": "権限がありません"}), 403

    if request.method == "DELETE":
        db.session.delete(deck)
        db.session.commit()
        return jsonify({"status": "success"})

    if request.method == "PUT":
        data = request.json
        deck.name = data["name"]
        deck.cards = json.dumps(data["cards"])
        db.session.commit()
        return jsonify({"status": "success"})


# ==========================================
# ★完全版：エフェクト・チェーン処理エンジン
# ==========================================
def process_pending_effects(room_id):
    if room_id not in rooms_data or "game" not in rooms_data[room_id]:
        return
    game = rooms_data[room_id]["game"]
    pending = game.get("pending_action")

    if (
        not pending
        or "effects_queue" not in pending
        or len(pending["effects_queue"]) == 0
    ):
        game["pending_action"] = None
        return

    sid = pending["player_sid"]
    opp_sid = [s for s in rooms_data[room_id]["players"].keys() if s != sid][0]
    next_effect = pending["effects_queue"].pop(0)

    target = next_effect.get("target")
    eff_type = next_effect.get("type")

    # --- 1. 即時処理（対象選択を必要としない全自動処理） ---
    if not target or target == "self" or target == "win_liver":
        if eff_type == "draw":
            amount = next_effect.get("amount", 1)
            for _ in range(amount):
                if len(game["board"][sid]["deck"]) > 0:
                    game["board"][sid]["hand"].append(game["board"][sid]["deck"].pop(0))
        elif eff_type == "open_both_color":
            for s in [sid, opp_sid]:
                for c in game["board"][s]["color_zone"]:
                    if not c["is_open"] and not c["is_rainbow"]:
                        c["is_open"] = True
                        break
        elif eff_type == "destroy_all_livers":
            for s in [sid, opp_sid]:
                for liver in game["board"][s]["livers"]:
                    game["board"][s]["log"].append(liver["id"])
                game["board"][s]["livers"] = []
        elif eff_type == "deck_to_log":
            amount = next_effect.get("amount", 1)
            for _ in range(amount):
                if len(game["board"][sid]["deck"]) > 0:
                    game["board"][sid]["log"].append(game["board"][sid]["deck"].pop(0))
        elif eff_type == "stand_self":
            if pending.get("source_liver_idx") is not None:
                idx = pending["source_liver_idx"]
                if 0 <= idx < len(game["board"][sid]["livers"]):
                    game["board"][sid]["livers"][idx]["state"] = "stand"

        process_pending_effects(room_id)
        return

    # --- 2. 対象選択処理（画面にメッセージを出して入力を待つ） ---
    if target in ["my_log_select", "my_hand_select"] and "spawn" in eff_type:
        if len(game["board"][sid]["livers"]) >= 5:
            process_pending_effects(room_id)
            return

    game["pending_action"].update(
        {
            "type": target,
            "effect_type": eff_type,
            "value": next_effect.get("value", 0),
            "message": next_effect.get("message", "対象を選んでください"),
            "conditions": next_effect,
        }
    )


def check_game_end(room_id):
    if room_id not in rooms_data or "game" not in rooms_data[room_id]:
        return False
    game = rooms_data[room_id]["game"]
    players_sids = list(rooms_data[room_id]["players"].keys())
    if len(players_sids) != 2:
        return False

    p1_sid, p2_sid = players_sids[0], players_sids[1]
    p1_board, p2_board = game["board"][p1_sid], game["board"][p2_sid]

    p1_rainbow = sum(1 for c in p1_board["color_zone"] if c["is_rainbow"])
    p2_rainbow = sum(1 for c in p2_board["color_zone"] if c["is_rainbow"])

    winner_sid = None
    end_message = ""

    if p1_rainbow >= 7:
        winner_sid = p2_sid
        end_message = "勝負あり！(虹エリアが7色揃いました)"
    elif p2_rainbow >= 7:
        winner_sid = p1_sid
        end_message = "勝負あり！(虹エリアが7色揃いました)"
    elif len(p1_board["deck"]) == 0 or len(p2_board["deck"]) == 0:
        if len(p1_board["deck"]) == 0 and len(p2_board["deck"]) > 0:
            if p1_rainbow < p2_rainbow:
                winner_sid = p1_sid
            elif p2_rainbow < p1_rainbow:
                winner_sid = p2_sid
            else:
                winner_sid = p2_sid
        elif len(p2_board["deck"]) == 0 and len(p1_board["deck"]) > 0:
            if p2_rainbow < p1_rainbow:
                winner_sid = p2_sid
            elif p1_rainbow < p2_rainbow:
                winner_sid = p1_sid
            else:
                winner_sid = p1_sid
        if winner_sid:
            end_message = "デッキが0枚になりました！判定に入ります..."

    if winner_sid:
        emit("game_state_updated", game, to=room_id)
        for p in rooms_data[room_id]["players"].values():
            p["ready"] = False
        del rooms_data[room_id]["game"]
        emit(
            "match_ended",
            {"message": end_message, "winner_sid": winner_sid},
            to=room_id,
        )
        emit("room_updated", rooms_data[room_id]["players"], to=room_id)
        return True
    return False


# ==========================================
# Socket.IO イベント
# ==========================================
@socketio.on("connect")
def handle_connect():
    if current_user.is_authenticated:
        print(f"ユーザー接続: {current_user.username} (SID: {request.sid})")


@socketio.on("disconnect")
def handle_disconnect():
    for room_id, data in list(rooms_data.items()):
        if request.sid in data["players"]:
            del data["players"][request.sid]
            if len(data["players"]) == 0:
                del rooms_data[room_id]
            else:
                emit("room_updated", data["players"], to=room_id)
            break


@socketio.on("join_match_room")
def on_join_match_room(data):
    room_id = data.get("room_id")
    deck_id = data.get("deck_id")
    username = current_user.username
    if not room_id or not deck_id:
        emit("join_error", {"message": "ルームIDまたはデッキが選択されていません"})
        return
    if room_id not in rooms_data:
        rooms_data[room_id] = {"players": {}}
    if (
        len(rooms_data[room_id]["players"]) >= 2
        and request.sid not in rooms_data[room_id]["players"]
    ):
        emit("join_error", {"message": "ルームが満員です"})
        return

    join_room(room_id)
    rooms_data[room_id]["players"][request.sid] = {
        "username": username,
        "deck_id": deck_id,
        "ready": False,
    }
    emit("join_success", {"room_id": room_id})
    emit("room_updated", rooms_data[room_id]["players"], to=room_id)


@socketio.on("update_deck")
def on_update_deck(data):
    room_id = data.get("room_id")
    deck_id = data.get("deck_id")
    if room_id in rooms_data and request.sid in rooms_data[room_id]["players"]:
        rooms_data[room_id]["players"][request.sid]["deck_id"] = deck_id
        emit("room_updated", rooms_data[room_id]["players"], to=room_id)


@socketio.on("toggle_ready")
def on_toggle_ready(data):
    room_id = data.get("room_id")
    if room_id in rooms_data and request.sid in rooms_data[room_id]["players"]:
        rooms_data[room_id]["players"][request.sid]["ready"] = not rooms_data[room_id][
            "players"
        ][request.sid]["ready"]
        emit("room_updated", rooms_data[room_id]["players"], to=room_id)

        players_sids = list(rooms_data[room_id]["players"].keys())
        if len(players_sids) == 2 and all(
            p["ready"] for p in rooms_data[room_id]["players"].values()
        ):
            board = {}
            for sid in players_sids:
                deck_id = rooms_data[room_id]["players"][sid]["deck_id"]
                deck_data = Deck.query.get(deck_id)
                cards_json = json.loads(deck_data.cards)
                main_deck = cards_json.get("main", [])
                random.shuffle(main_deck)

                colors = [
                    "RED",
                    "ORANGE",
                    "YELLOW",
                    "GREEN",
                    "LIGHTBLUE",
                    "BLUE",
                    "PURPLE",
                ]
                random.shuffle(colors)
                color_zone = [
                    {"color": c, "is_open": False, "is_rainbow": False} for c in colors
                ]

                board[sid] = {
                    "channel": cards_json.get("channel"),
                    "deck": main_deck,
                    "hand": [],
                    "livers": [],
                    "stages": [],
                    "log": [],
                    "set_zone": [],
                    "color_zone": color_zone,
                    "mulligan_done": False,
                    "has_set_this_turn": False,
                }

            p1_sid, p2_sid = players_sids[0], players_sids[1]
            board[p1_sid]["hand"], board[p1_sid]["deck"] = (
                board[p1_sid]["deck"][:5],
                board[p1_sid]["deck"][5:],
            )
            board[p2_sid]["hand"], board[p2_sid]["deck"] = (
                board[p2_sid]["deck"][:7],
                board[p2_sid]["deck"][7:],
            )

            rooms_data[room_id]["game"] = {
                "turn_player_sid": p1_sid,
                "phase": "main",
                "turn_count": 1,
                "board": board,
            }
            emit(
                "match_start",
                {"message": "対戦開始！", "game": rooms_data[room_id]["game"]},
                to=room_id,
            )


@socketio.on("declare_action")
def on_declare_action(data):
    room_id = data.get("room_id")
    action_type = data.get("action_type")
    attacker_idx = data.get("attacker_idx")
    target_idx = data.get("target_idx")
    sid = request.sid

    if room_id in rooms_data and "game" in rooms_data[room_id]:
        game = rooms_data[room_id]["game"]
        if game["turn_player_sid"] == sid and game["phase"] == "action":
            my_board = game["board"][sid]
            opp_sid = [s for s in rooms_data[room_id]["players"].keys() if s != sid][0]
            opp_board = game["board"][opp_sid]

            attacker = my_board["livers"][attacker_idx]
            attacker["state"] = "rest"
            attacker_card = Card.query.get(attacker["id"])
            atk_power = (attacker_card.power or 0) + attacker.get("temp_power", 0)

            if action_type == "attack":
                target = opp_board["livers"][target_idx]
                target_card = Card.query.get(target["id"])
                def_power = (target_card.power or 0) + target.get("temp_power", 0)

                if atk_power > def_power:
                    removed = opp_board["livers"].pop(target_idx)
                    opp_board["log"].append(removed["id"])

                    if attacker_card.id in CARD_EFFECTS_DEF:
                        win_effects = [
                            e
                            for e in CARD_EFFECTS_DEF[attacker_card.id]
                            if e.get("trigger") == "on_battle_win"
                        ]
                        if win_effects:
                            game["pending_action"] = {
                                "player_sid": sid,
                                "card_name": attacker_card.name,
                                "effects_queue": win_effects.copy(),
                                "source_liver_idx": attacker_idx,
                            }
                            process_pending_effects(room_id)
                elif atk_power < def_power:
                    removed = my_board["livers"].pop(attacker_idx)
                    my_board["log"].append(removed["id"])

            elif action_type == "color_call":
                target_color = opp_board["color_zone"][target_idx]
                target_color["is_open"] = True
                attacker_colors = (
                    attacker_card.color.replace(" ", "").split(",")
                    if attacker_card.color
                    else []
                )
                if target_color["color"] in attacker_colors:
                    target_color["is_rainbow"] = True
                    if attacker_card.id in CARD_EFFECTS_DEF:
                        color_effects = [
                            e
                            for e in CARD_EFFECTS_DEF[attacker_card.id]
                            if e.get("trigger") == "on_color_call_success"
                        ]
                        if color_effects:
                            game["pending_action"] = {
                                "player_sid": sid,
                                "card_name": attacker_card.name,
                                "effects_queue": color_effects.copy(),
                                "source_liver_idx": attacker_idx,
                            }
                            process_pending_effects(room_id)

        if check_game_end(room_id):
            return
        emit("game_state_updated", game, to=room_id)


@socketio.on("set_card")
def on_set_card(data):
    room_id = data.get("room_id")
    card_index = data.get("card_index")
    sid = request.sid

    if room_id in rooms_data and "game" in rooms_data[room_id]:
        game = rooms_data[room_id]["game"]
        if game["turn_player_sid"] == sid and game["phase"] == "set":
            player_board = game["board"][sid]
            if not player_board.get("has_set_this_turn"):
                if 0 <= card_index < len(player_board["hand"]):
                    card_id = player_board["hand"].pop(card_index)
                    if len(player_board["set_zone"]) > 0:
                        old_card = player_board["set_zone"].pop(0)
                        player_board["log"].append(old_card)
                    player_board["set_zone"].append(card_id)
                    player_board["has_set_this_turn"] = True
                    emit("game_state_updated", game, to=room_id)
            else:
                emit(
                    "play_error",
                    {"message": "セットフェイズに置けるカードは1ターンに1枚までです。"},
                    to=sid,
                )


@socketio.on("play_card")
def on_play_card(data):
    room_id = data.get("room_id")
    card_index = data.get("card_index")
    cost_hand = data.get("cost_hand", [])
    cost_field = data.get("cost_field", [])
    from_zone = data.get("from_zone", "hand")
    sid = request.sid

    if room_id in rooms_data and "game" in rooms_data[room_id]:
        game = rooms_data[room_id]["game"]
        if game["turn_player_sid"] == sid and game["phase"] == "main":
            player_board = game["board"][sid]
            target_zone = (
                player_board["hand"]
                if from_zone == "hand"
                else player_board["set_zone"]
            )

            if 0 <= card_index < len(target_zone):
                card_id = target_zone[card_index]
                card_data = Card.query.get(card_id)
                cost = card_data.level if card_data.level else 0

                for f_idx in sorted(cost_field, reverse=True):
                    removed_liver = player_board["livers"].pop(f_idx)
                    player_board["log"].append(removed_liver["id"])

                played_card_id = None
                if from_zone == "hand":
                    indices_to_remove = sorted(
                        list(set(cost_hand + [card_index])), reverse=True
                    )
                    for h_idx in indices_to_remove:
                        popped_id = player_board["hand"].pop(h_idx)
                        if h_idx == card_index:
                            played_card_id = popped_id
                        else:
                            player_board["log"].append(popped_id)
                else:
                    played_card_id = player_board["set_zone"].pop(card_index)
                    for h_idx in sorted(cost_hand, reverse=True):
                        popped_id = player_board["hand"].pop(h_idx)
                        player_board["log"].append(popped_id)

                if card_data.type == "LIVER":
                    player_board["livers"].append(
                        {"id": played_card_id, "state": "stand", "temp_power": 0}
                    )
                elif card_data.type == "STAGE":
                    player_board["stages"].append(played_card_id)
                else:
                    player_board["log"].append(played_card_id)

                game["pending_action"] = None
                if card_data.id in CARD_EFFECTS_DEF:
                    effects = [
                        e
                        for e in CARD_EFFECTS_DEF[card_data.id]
                        if e.get("trigger") == "on_play"
                    ]
                    if effects:
                        game["pending_action"] = {
                            "player_sid": sid,
                            "card_name": card_data.name,
                            "effects_queue": effects.copy(),
                        }
                        process_pending_effects(room_id)

                if check_game_end(room_id):
                    return
                emit("game_state_updated", game, to=room_id)


@socketio.on("do_mulligan")
def on_do_mulligan(data):
    room_id = data.get("room_id")
    sid = request.sid
    if room_id in rooms_data and "game" in rooms_data[room_id]:
        game = rooms_data[room_id]["game"]
        player_board = game["board"][sid]
        if not player_board["mulligan_done"]:
            current_hand_count = len(player_board["hand"])
            player_board["deck"].extend(player_board["hand"])
            player_board["hand"] = []
            random.shuffle(player_board["deck"])
            player_board["hand"] = player_board["deck"][:current_hand_count]
            del player_board["deck"][:current_hand_count]
            player_board["mulligan_done"] = True
            emit("game_state_updated", game, to=room_id)


@socketio.on("next_phase")
def on_next_phase(data):
    room_id = data.get("room_id")
    if room_id in rooms_data and "game" in rooms_data[room_id]:
        game = rooms_data[room_id]["game"]
        phases = ["start", "main", "action", "set", "end"]
        current_idx = phases.index(game["phase"])

        if current_idx < 4:
            next_phase = phases[current_idx + 1]
            if next_phase == "action" and game["turn_count"] == 1:
                next_phase = "set"
            game["phase"] = next_phase
        else:
            game["turn_count"] += 1
            players_sids = list(rooms_data[room_id]["players"].keys())
            game["turn_player_sid"] = (
                players_sids[1]
                if game["turn_player_sid"] == players_sids[0]
                else players_sids[0]
            )
            game["phase"] = "main" if game["turn_count"] <= 2 else "start"

        if game["phase"] == "start":
            active_sid = game["turn_player_sid"]
            opp_sid = [
                s for s in rooms_data[room_id]["players"].keys() if s != active_sid
            ][0]
            board, opp_board = game["board"][active_sid], game["board"][opp_sid]

            board["has_set_this_turn"] = False
            for liver in board["livers"]:
                if liver.get("frozen"):
                    liver["frozen"] = False
                else:
                    liver["state"] = "stand"
                liver["temp_power"] = 0
            for liver in opp_board["livers"]:
                liver["temp_power"] = 0

            draw_amount = 1 if len(board["hand"]) >= 5 else 5 - len(board["hand"])
            if draw_amount > len(board["deck"]):
                draw_amount = len(board["deck"])
            if draw_amount > 0:
                drawn = board["deck"][:draw_amount]
                board["hand"].extend(drawn)
                del board["deck"][:draw_amount]

        if check_game_end(room_id):
            return
        emit("game_state_updated", game, to=room_id)


@socketio.on("end_match")
def on_end_match(data):
    room_id = data.get("room_id")
    if room_id in rooms_data:
        for p in rooms_data[room_id]["players"].values():
            p["ready"] = False
        if "game" in rooms_data[room_id]:
            del rooms_data[room_id]["game"]
        emit(
            "match_ended",
            {"message": "対戦が終了しました。ロビーに戻ります。"},
            to=room_id,
        )
        emit("room_updated", rooms_data[room_id]["players"], to=room_id)


@socketio.on("resolve_target")
def on_resolve_target(data):
    room_id = data.get("room_id")
    target_idx = data.get("target_idx")
    sid = request.sid

    if room_id in rooms_data and "game" in rooms_data[room_id]:
        game = rooms_data[room_id]["game"]
        pending = game.get("pending_action")

        if pending and pending["player_sid"] == sid:
            my_board = game["board"][sid]
            opp_sid = [s for s in rooms_data[room_id]["players"].keys() if s != sid][0]
            opp_board = game["board"][opp_sid]

            target_type = pending.get("type")
            eff_type = pending.get("effect_type")
            val = pending.get("value", 0)
            conds = pending.get("conditions", {})
            is_valid = False

            if target_type == "opp_liver_select" and 0 <= target_idx < len(
                opp_board["livers"]
            ):
                t_liver = opp_board["livers"][target_idx]
                if eff_type == "modify_power":
                    t_liver["temp_power"] = t_liver.get("temp_power", 0) + val
                elif eff_type == "modify_power_and_destroy_if_zero":
                    t_liver["temp_power"] = t_liver.get("temp_power", 0) + val
                    c_data = Card.query.get(t_liver["id"])
                    if (c_data.power or 0) + t_liver["temp_power"] <= 0:
                        opp_board["log"].append(
                            opp_board["livers"].pop(target_idx)["id"]
                        )
                elif eff_type == "send_to_log":
                    opp_board["log"].append(opp_board["livers"].pop(target_idx)["id"])
                elif eff_type == "return_to_hand":
                    opp_board["hand"].append(opp_board["livers"].pop(target_idx)["id"])
                elif eff_type == "send_to_set_or_log":
                    popped = opp_board["livers"].pop(target_idx)["id"]
                    if len(opp_board["set_zone"]) == 0:
                        opp_board["set_zone"].append(popped)
                    else:
                        opp_board["log"].append(popped)
                elif eff_type == "freeze_stand":
                    t_liver["frozen"] = True
                is_valid = True

            elif target_type == "my_liver_select" and 0 <= target_idx < len(
                my_board["livers"]
            ):
                t_liver = my_board["livers"][target_idx]
                if eff_type == "modify_power":
                    t_liver["temp_power"] = t_liver.get("temp_power", 0) + val
                elif eff_type == "modify_power_conditional":
                    c_data = Card.query.get(t_liver["id"])
                    if (c_data.power or 0) >= conds.get("bonus_threshold", 99999):
                        t_liver["temp_power"] += conds.get("bonus_value", val)
                    else:
                        t_liver["temp_power"] += val
                elif eff_type == "stand_target":
                    t_liver["state"] = "stand"
                is_valid = True

            elif target_type == "opp_color_zone_select" and 0 <= target_idx < len(
                opp_board["color_zone"]
            ):
                c_card = opp_board["color_zone"][target_idx]
                if eff_type == "open_opp_color" and not c_card["is_rainbow"]:
                    c_card["is_open"] = True
                is_valid = True

            elif target_type == "my_log_select" and 0 <= target_idx < len(
                my_board["log"]
            ):
                if eff_type == "spawn_from_log":
                    my_board["livers"].append(
                        {
                            "id": my_board["log"].pop(target_idx),
                            "state": conds.get("spawn_state", "stand"),
                            "temp_power": 0,
                        }
                    )
                elif eff_type == "log_to_deck_bottom":
                    my_board["deck"].append(my_board["log"].pop(target_idx))
                elif eff_type == "send_log_to_deck_bottom_and_draw":
                    my_board["deck"].append(my_board["log"].pop(target_idx))
                    if len(my_board["deck"]) > 0:
                        my_board["hand"].append(my_board["deck"].pop(0))
                is_valid = True

            elif target_type == "my_hand_select" and 0 <= target_idx < len(
                my_board["hand"]
            ):
                if eff_type == "spawn_from_hand":
                    my_board["livers"].append(
                        {
                            "id": my_board["hand"].pop(target_idx),
                            "state": "stand",
                            "temp_power": 0,
                        }
                    )
                elif eff_type == "discard_to_stand":
                    my_board["log"].append(my_board["hand"].pop(target_idx))
                    if pending.get("source_liver_idx") is not None:
                        idx = pending["source_liver_idx"]
                        if 0 <= idx < len(my_board["livers"]):
                            my_board["livers"][idx]["state"] = "stand"
                is_valid = True

            if is_valid:
                process_pending_effects(room_id)
            else:
                emit(
                    "play_error",
                    {
                        "message": "条件に合致しない対象です。選び直すかキャンセルしてください。"
                    },
                    to=sid,
                )
                return

        if check_game_end(room_id):
            return
        emit("game_state_updated", game, to=room_id)


@socketio.on("cancel_pending_action")
def on_cancel_pending_action(data):
    room_id = data.get("room_id")
    sid = request.sid
    if room_id in rooms_data and "game" in rooms_data[room_id]:
        game = rooms_data[room_id]["game"]
        pending = game.get("pending_action")
        if pending and pending["player_sid"] == sid:
            process_pending_effects(room_id)
            if check_game_end(room_id):
                return
            emit("game_state_updated", game, to=room_id)


def init_db():
    with app.app_context():
        db.create_all()
        if os.path.exists("cards.json") and Card.query.count() == 0:
            with open("cards.json", "r", encoding="utf-8") as f:
                cards_data = json.load(f)
                for c in cards_data:
                    card = Card(
                        id=c.get("id"),
                        name=c.get("name"),
                        type=c.get("type"),
                        card_class=c.get("class"),
                        level=c.get("level"),
                        power=c.get("power"),
                        color=c.get("color"),
                        text=c.get("text"),
                        image_url=c.get("image_url"),
                        is_iris_one=c.get("is_iris_one", False),  # ★ここを追加！
                    )
                    db.session.add(card)
            db.session.commit()


if __name__ == "__main__":
    init_db()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
