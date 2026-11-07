# ==========================================
# にじなな 汎用エフェクト・データベース (card_effects.py)
# ==========================================

CARD_EFFECTS_DEF = {
    # -------------------------
    # スターターデッキ1 (ソル)
    # -------------------------
    "NJ-SD01-001": [  # 月ノ美兎 (CHANNEL)
        {
            "trigger": "on_battle_win",
            "condition_per_turn": 1,
            "type": "open_opp_color",
            "target": "opp_color_zone_select",
            "message": "相手のカラーカードを1枚選んで表にしてください",
        }
    ],
    "NJ-SD01-002": [  # 静凛 (ブロッカー)
        {"trigger": "on_attacked", "type": "blocker"}
    ],
    "NJ-SD01-004": [  # 静凛
        {
            "trigger": "on_play",
            "type": "spawn_from_hand",
            "target": "my_hand_select",
            "condition_max_level": 1,
            "condition_tag": "#JK",
            "bonus_condition": "my_color_zone_5_plus",
            "bonus_max_level": 2,
            "message": "【任意】手札から対象の「#JK」を選んで登場させてください",
        }
    ],
    "NJ-SD01-008": [  # 月ノ美兎
        {
            "trigger": "on_play",
            "type": "modify_power_conditional",
            "target": "my_liver_select",
            "exclude_self": True,
            "value": 3000,
            "bonus_threshold": 7000,
            "bonus_value": 5000,
            "message": "パワーを上げる自分のライバーを1枚選んでください",
        }
    ],
    "NJ-SD01-009": [  # 月ノ美兎
        {
            "trigger": "on_battle_win",
            "type": "spawn_from_log",
            "target": "my_log_select",
            "condition_level_exact": 0,
            "condition_tag": "#JK",
            "spawn_state": "rest",
            "message": "【任意】ログからLv0の「#JK」を選んでヨコで登場させてください",
        }
    ],
    "NJ-SD01-010": [  # 樋口楓
        {
            "trigger": "on_play",
            "type": "freeze_stand",
            "target": "opp_liver_select",
            "condition_state": "rest",
            "condition_max_level": 2,
            "message": "次のターンにタテにならない相手のヨコのライバー(Lv2以下)を選んでください",
        }
    ],
    "NJ-SD01-011": [  # 樋口楓
        {
            "trigger": "on_battle_win",
            "type": "sp_call",
            "target": "self",
            "message": "SPコール発動！(自動処理)",
        }
    ],
    "NJ-SD01-013": [  # 樋口楓
        {
            "trigger": "on_play",
            "type": "freeze_stand",
            "target": "opp_liver_select",
            "condition_state": "rest",
            "message": "次のターンにタテにならない相手のヨコのライバーを選んでください",
        }
    ],
    "NJ-SD01-014": [  # 筋肉愛
        {
            "trigger": "on_play",
            "type": "modify_power",
            "target": "my_liver_select",
            "value": 5000,
            "message": "パワー+5000する自分のライバーを選んでください",
        }
    ],
    "NJ-SD01-015": [  # 圧
        {
            "trigger": "on_play",
            "type": "send_to_log",
            "target": "opp_liver_select",
            "condition_state": "rest",
            "condition_max_level": 6,
            "message": "ログに置くLv6以下の相手のヨコのライバーを選んでください",
        }
    ],
    "NJ-SD01-016": [  # NEVER GLOW UP
        {
            "trigger": "on_activate_main",
            "condition_per_turn": 1,
            "condition_field_tag": "#JK",
            "condition_field_count": 3,
            "type": "modify_power",
            "target": "my_liver_select",
            "value": 1000,
            "message": "パワー+1000する自分のライバーを選んでください",
        }
    ],
    # -------------------------
    # スターターデッキ2 (ルナ)
    # -------------------------
    "NJ-SD02-001": [  # 葛葉 (CHANNEL)
        {
            "trigger": "on_activate_main",
            "condition_per_turn": 1,
            "type": "deck_to_log",
            "amount": 1,
            "message": "デッキの上から1枚をログに置きました",
        }
    ],
    "NJ-SD02-002": [  # イブラヒム (ブロッカー)
        {"trigger": "on_attacked", "type": "blocker"}
    ],
    "NJ-SD02-004": [  # イブラヒム
        {
            "trigger": "on_play",
            "type": "modify_power_conditional",
            "target": "my_liver_select",
            "exclude_self": True,
            "value": 3000,
            "bonus_threshold": 7000,
            "bonus_value": 5000,
            "message": "パワーを上げる自分のライバーを1枚選んでください",
        }
    ],
    "NJ-SD02-005": [  # イブラヒム
        {
            "trigger": "on_play",
            "type": "reveal_deck_top",
            "amount": 3,
            "action": "modify_power_by_revealed_sum_and_bottom",
            "message": "公開されたカードのパワー分アップし、デッキ下へ送りました",
        }
    ],
    "NJ-SD02-006": [  # エクス・アルビオ
        {
            "trigger": "on_other_attacked",
            "exclude_attacked_name": "エクス・アルビオ",
            "type": "sacrifice_self_to_cancel_attack",
            "condition_state": "rest",
            "message": "【任意】このカードをログに置いて攻撃を無効にしますか？",
        }
    ],
    "NJ-SD02-007": [  # エクス・アルビオ
        {
            "trigger": "on_battle_win",
            "type": "sp_call",
            "target": "self",
            "message": "SPコール発動！(自動処理)",
        }
    ],
    "NJ-SD02-009": [  # エクス・アルビオ
        {
            "trigger": "on_battle_win",
            "condition_per_turn": 1,
            "condition_played_this_turn": True,
            "type": "discard_to_stand",
            "target": "my_hand_select",
            "message": "【任意】手札を1枚捨てて、このカードをタテにしますか？",
        }
    ],
    "NJ-SD02-011": [  # 葛葉
        {
            "trigger": "on_destroyed_in_battle_in_opp_turn",
            "type": "spawn_from_log",
            "target": "my_log_select",
            "condition_level_exact": 0,
            "condition_name": "葛葉",
            "message": "ログからLv0の「葛葉」を選んで登場させてください",
        }
    ],
    "NJ-SD02-013": [  # 葛葉
        {
            "trigger": "on_play",
            "condition_my_log_20_plus": True,
            "type": "modify_power",
            "target": "opp_liver_select",
            "value": -4000,
            "message": "パワーを-4000する相手のライバーを選んでください",
        },
        {
            "trigger": "on_play",
            "condition_my_log_20_plus": True,
            "type": "log_to_deck_bottom",
            "target": "my_log_select",
            "amount": 2,
            "condition_max_level": 2,
            "message": "【任意】デッキの下に戻すLv2以下のライバーを2枚まで選んでください",
        },
    ],
    "NJ-SD02-014": [  # 遊戯開始
        {
            "trigger": "on_play",
            "type": "modify_power_and_destroy_if_zero",
            "target": "opp_liver_select",
            "condition_max_level": 5,
            "value": -10000,
            "message": "パワーを-10000するLv5以下の相手ライバーを選んでください",
        }
    ],
    "NJ-SD02-015": [  # 英雄の一撃
        {
            "trigger": "on_play",
            "type": "modify_power",
            "target": "opp_liver_select",
            "value": -3000,
            "message": "パワーを-3000する相手のライバーを選んでください",
        },
        {
            "trigger": "on_play",
            "type": "spawn_from_log",
            "target": "my_log_select",
            "condition_max_level": 2,
            "condition_name": "エクス・アルビオ",
            "spawn_state": "stand",
            "message": "【任意】ログからLv2以下の「エクス・アルビオ」を選んで登場させてください",
        },
    ],
    "NJ-SD02-016": [  # 吸血鬼の夜
        {
            "trigger": "on_activate_main",
            "condition_per_turn": 1,
            "type": "absorb_deck_top",
            "amount": 1,
            "message": "デッキからカードを下に置きました",
        },
        {
            "trigger": "on_activate_main",
            "condition_under_cards_count": 3,
            "type": "send_self_and_under_to_deck_bottom_and_spawn",
            "target": "my_log_select",
            "condition_max_level": 4,
            "condition_name": "葛葉",
            "message": "【任意】ログからLv4以下の「葛葉」を選んで登場させてください",
        },
    ],
    # -------------------------
    # スターターデッキ3 (コメット)
    # -------------------------
    "NJ-SD03-001": [  # 笹木咲 (CHANNEL)
        {
            "trigger": "on_my_liver_destroyed_in_opp_turn",
            "condition_per_turn": 1,
            "type": "absorb_destroyed_liver",
            "message": "破壊されたライバーをこのカードの下に置きました",
        },
        {
            "trigger": "on_my_liver_destroyed_in_opp_turn",
            "condition_under_cards_count": 3,
            "type": "send_under_to_deck_bottom_and_draw_to_5",
            "message": "下のカードをデッキに戻し、手札が5枚になるようドローしました",
        },
    ],
    "NJ-SD03-003": [  # 笹木咲 (ブロッカー)
        {"trigger": "on_attacked", "type": "blocker"}
    ],
    "NJ-SD03-004": [  # 笹木咲
        {
            "trigger": "on_play",
            "type": "modify_power_conditional",
            "target": "my_liver_select",
            "exclude_self": True,
            "value": 3000,
            "bonus_threshold": 7000,
            "bonus_value": 5000,
            "message": "パワーを上げる自分のライバーを1枚選んでください",
        }
    ],
    "NJ-SD03-005": [  # 笹木咲
        {
            "trigger": "on_play",
            "type": "spawn_from_log",
            "target": "my_log_select",
            "condition_same_tags_as_self": True,
            "condition_max_level": 1,
            "bonus_condition": "my_color_zone_5_plus",
            "base_spawn_state": "rest",
            "bonus_spawn_state": "stand",
            "message": "【任意】ログから対象のライバーを選んで登場させてください",
        }
    ],
    "NJ-SD03-006": [  # 本間ひまわり
        {
            "trigger": "on_stand",
            "type": "draw",
            "amount": 1,
            "message": "カードを1枚引きました",
        }
    ],
    "NJ-SD03-007": [  # 本間ひまわり
        {
            "trigger": "on_play",
            "condition_my_color_zone_5_plus": True,
            "type": "draw",
            "amount": 1,
            "message": "カラーが5枚以上なのでカードを1枚引きました",
        }
    ],
    "NJ-SD03-009": [  # 本間ひまわり
        {
            "trigger": "on_battle_win",
            "condition_played_this_turn": True,
            "type": "stand_self",
            "message": "登場したターンなのでタテになります",
        }
    ],
    "NJ-SD03-011": [  # 魔界ノりりむ
        {
            "trigger": "on_battle_win",
            "type": "sp_call",
            "target": "self",
            "message": "SPコール発動！(自動処理)",
        }
    ],
    "NJ-SD03-013": [  # 魔界ノりりむ
        {
            "trigger": "on_battle_win",
            "type": "spawn_from_log",
            "target": "my_log_select",
            "condition_level_exact": 0,
            "condition_tag": "#ゲーマー",
            "spawn_state": "rest",
            "message": "【任意】ログからLv0の「#ゲーマー」を選んでヨコで登場させてください",
        }
    ],
    "NJ-SD03-014": [  # ばぁっ！
        {
            "trigger": "on_play",
            "type": "send_to_set_or_log",
            "target": "opp_liver_select",
            "condition_max_level": 5,
            "message": "セットまたはログに置くLv5以下の相手ライバーを選んでください",
        }
    ],
    "NJ-SD03-015": [  # 怒りの台パン
        {
            "trigger": "on_play",
            "type": "destroy_all_livers",
            "message": "すべてのライバーをログに置きました！",
        }
    ],
    "NJ-SD03-016": [  # リロードポイント
        {
            "trigger": "on_activate_main",
            "condition_per_turn": 1,
            "type": "discard_to_under_and_draw",
            "target": "my_hand_select",
            "message": "手札を1枚選んで下に置き、1枚引いてください",
        },
        {
            "trigger": "on_activate_main",
            "condition_under_cards_count": 3,
            "type": "send_self_and_under_to_deck_bottom_and_draw",
            "message": "自身と下のカードを戻し、カードを1枚引きました",
        },
    ],
    # -------------------------
    # スターターデッキ4 (ステラ)
    # -------------------------
    "NJ-SD04-001": [  # 加賀美ハヤト (CHANNEL)
        {
            "trigger": "on_my_turn_end",
            "type": "opp_open_my_color_to_stand_my_liver",
            "target": "my_liver_select",
            "condition_max_level": 1,
            "message": "相手はあなたの裏のカラーを表にします。タテにする自分のLv1以下のライバーを選んでください",
        }
    ],
    "NJ-SD04-002": [  # 加賀美ハヤト (ブロッカー)
        {"trigger": "on_attacked", "type": "blocker"}
    ],
    "NJ-SD04-005": [  # 加賀美ハヤト
        {
            "trigger": "on_color_call_success",
            "condition_per_turn": 1,
            "condition_opp_all_color_open": True,
            "type": "stand_target",
            "target": "my_liver_select",
            "exclude_name": "加賀美ハヤト",
            "condition_same_tags_as_self": True,
            "message": "【任意】タテにする対象のライバーを選んでください",
        }
    ],
    "NJ-SD04-007": [  # 葉加瀬冬雪
        {
            "trigger": "on_play",
            "type": "modify_power_conditional",
            "target": "my_liver_select",
            "exclude_self": True,
            "value": 3000,
            "bonus_threshold": 7000,
            "bonus_value": 5000,
            "message": "パワーを上げる自分のライバーを1枚選んでください",
        }
    ],
    "NJ-SD04-008": [  # 葉加瀬冬雪
        {
            "trigger": "on_battle_win",
            "type": "sp_call",
            "target": "self",
            "message": "SPコール発動！(自動処理)",
        }
    ],
    "NJ-SD04-009": [  # 葉加瀬冬雪
        {
            "trigger": "on_color_call_success",
            "condition_per_turn": 1,
            "type": "cast_event_from_log_then_bottom",
            "target": "my_log_select",
            "condition_max_level": 2,
            "condition_tag": "#エンカウンター",
            "condition_card_type": "EVENT",
            "message": "【任意】ログから発動するLv2以下の「#エンカウンター」イベントを選んでください",
        }
    ],
    "NJ-SD04-011": [  # 夜見れな
        {
            "trigger": "on_stand",
            "type": "open_opp_color",
            "target": "opp_color_zone_select",
            "message": "相手のカラーカードを1枚選んで表にしてください",
        }
    ],
    "NJ-SD04-012": [  # 夜見れな
        {
            "trigger": "on_play",
            "type": "open_both_color",
            "message": "お互いのカラーを1枚ずつ表にします",
        }
    ],
    "NJ-SD04-013": [  # 夜見れな
        {
            "trigger": "on_destroyed_in_battle_in_opp_turn",
            "type": "reveal_deck_top_to_spawn",
            "amount": 3,
            "condition_same_tags_as_self": True,
            "condition_max_level": 2,
            "spawn_state": "rest",
            "message": "デッキから対象のライバーを選んでヨコで登場させてください",
        }
    ],
    "NJ-SD04-014": [  # スリープ交換
        {
            "trigger": "on_play",
            "type": "open_opp_color",
            "target": "opp_color_zone_select",
            "message": "相手のカラーカードを1枚選んで表にしてください",
        },
        {
            "trigger": "on_play",
            "condition_opp_all_color_open": True,
            "type": "spawn_from_log",
            "target": "my_log_select",
            "condition_same_tags_as_self": True,
            "condition_max_level": 1,
            "spawn_state": "rest",
            "message": "【任意】ログから対象のライバーを選んでヨコで登場させてください",
        },
    ],
    "NJ-SD04-015": [  # 大爆発
        {
            "trigger": "on_play",
            "type": "return_to_hand",
            "target": "opp_liver_select",
            "condition_max_level": 5,
            "message": "手札に戻すLv5以下の相手ライバーを選んでください",
        }
    ],
    "NJ-SD04-016": [  # アンコールステージ
        {
            "trigger": "on_my_liver_color_call_success",
            "condition_field_tag": "#エンカウンター",
            "condition_opp_all_color_open": True,
            "type": "sacrifice_self_to_spawn_from_log",
            "target": "my_log_select",
            "condition_max_level": 3,
            "condition_tag": "#エンカウンター",
            "message": "【任意】このステージを破棄して、ログから対象のライバーを登場させますか？",
        }
    ],
    # -------------------------
    # ブースターパック1
    # -------------------------
    "NJ-BP01-001": [  # 剣持刀也 (CHANNEL)
        {
            "trigger": "on_activate_main",
            "condition_per_turn": 1,
            "type": "rest_my_liver_to_buff_and_open_opp_color",
            "target_cost": "my_liver_select",
            "condition_cost_tag": "#弾丸",
            "exclude_cost_name": "剣持刀也",
            "target_buff": "my_liver_select",
            "condition_buff_name": "剣持刀也",
            "message": "ヨコにする味方と、強化する「剣持刀也」を順に選んでください",
        }
    ],
    "NJ-BP01-003": [  # 家長むぎ
        {
            "trigger": "on_play",
            "type": "reveal_deck_top_to_hand",
            "amount": 3,
            "condition_tag": "#弾丸",
            "message": "デッキから「#弾丸」を持つカードを選んで手札に加えてください",
        }
    ],
    "NJ-BP01-006": [  # 剣持刀也
        {
            "trigger": "on_other_attacked",
            "exclude_attacked_name": "剣持刀也",
            "type": "sacrifice_self_to_cancel_attack",
            "condition_state": "rest",
            "message": "【任意】このカードをログに置いて攻撃を無効にしますか？",
        }
    ],
    "NJ-BP01-007": [  # 剣持刀也
        {
            "trigger": "on_destroyed_in_battle_in_opp_turn",
            "condition_my_log_tag_count": {"tag": "#弾丸", "count": 4},
            "type": "open_opp_color",
            "target": "opp_color_zone_select",
            "message": "相手のカラーカードを1枚選んで表にしてください",
        }
    ],
    "NJ-BP01-009": [  # 剣持刀也
        {
            "trigger": "on_play",
            "condition_my_log_has_names": ["家長むぎ", "伏見ガク", "夕陽リリ"],
            "type": "gain_all_colors_this_turn",
            "target": "self",
            "message": "条件を満たしたため、すべての色を得ました！",
        }
    ],
    "NJ-BP01-016": [  # 月ノ美兎
        {
            "trigger": "on_stand",
            "type": "opp_must_rest_own_liver",
            "target": "opp_liver_select",
            "condition_state": "stand",
            "message": "ヨコにする相手のタテのライバーを1枚選んでください",
        }
    ],
    "NJ-BP01-021": [  # 伏見ガク
        {
            "trigger": "on_my_liver_battle_win",
            "exclude_win_name": "伏見ガク",
            "condition_win_tag": "#弾丸",
            "type": "sacrifice_self_and_discard_to_spawn_from_log",
            "target_cost": "my_hand_select",
            "target_spawn": "my_log_select",
            "condition_max_level": 4,
            "condition_name": "剣持刀也",
            "message": "【任意】自身と手札1枚を破棄して、ログからLv4以下の「剣持刀也」を登場させますか？",
        }
    ],
    "NJ-BP01-023": [  # 夕陽リリ
        {
            "trigger": "on_my_liver_battle_win",
            "condition_per_turn": 1,
            "exclude_win_name": "夕陽リリ",
            "condition_win_tag": "#弾丸",
            "type": "open_opp_color",
            "target": "opp_color_zone_select",
            "message": "相手のカラーカードを1枚選んで表にしてください",
        }
    ],
    "NJ-BP01-030": [  # 4発の弾丸
        {
            "trigger": "on_my_liver_battle_win",
            "condition_per_turn": 1,
            "condition_win_tag": "#弾丸",
            "type": "sp_call_to_hidden_color",
            "target": "win_liver",
            "message": "SPコール発動！(自動処理)",
        }
    ],
    "NJ-BP01-032": [  # 椎名唯華 (CHANNEL)
        # ※CHANNELのトリガー効果は裏側の処理（エンジン）で対応します
    ],
    "NJ-BP01-033": [  # 赤羽葉子
        {
            "trigger": "on_play",
            "type": "send_log_to_deck_bottom_and_draw",
            "target": "my_log_select",
            "condition_tag": "#ゲーマー",
            "condition_card_type": "EVENT",
            "message": "【任意】ログから「#ゲーマー」のイベントをデッキ下に戻して1枚引きますか？",
        }
    ],
    "NJ-BP01-043": [  # 椎名唯華
        {
            "trigger": "on_play",
            "type": "deck_to_log_and_check_event",
            "condition_tag": "#ゲーマー",
            "condition_card_type": "EVENT",
            "alternative_action": "search_log_for_spirit_event",
            "message": "デッキの上のカードをログに置きました",
        }
    ],
    "NJ-BP01-054": [  # 憑依バトル
        {
            "trigger": "on_play",
            "type": "destroy_lower_power_of_two",
            "target": "any_liver_select",
            "select_count": 2,
            "condition_different_power": True,
            "message": "パワーが異なるライバーを2体選んでください(低い方がログへ)",
        }
    ],
    "NJ-BP01-059": [  # 必中必殺
        {
            "trigger": "on_play",
            "type": "send_to_log",
            "target": "opp_liver_select",
            "select_count": 3,
            "message": "ログに置く相手のライバーを3体選んでください",
        }
    ],
    "NJ-BP01-123": [  # 剣持刀也
        {
            "trigger": "on_play",
            "type": "destroy_lower_power_of_two",
            "target": "any_liver_select",
            "select_count": 2,
            "condition_different_power": True,
            "message": "パワーが異なるライバーを2体選んでください(低い方がログへ)",
        }
    ],
}
