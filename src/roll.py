# src/roll.py
import random
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RollResult:
    dice_results: List[int]   # 振った生ダイス（逆凪時は空）
    raw_total: int            # 生ダイス合計（逆凪時は0）
    total: int                # ボーナス込み達成値（逆凪時は0）
    success: bool
    special: bool
    fumble: bool


def roll_d6(n: int) -> List[int]:
    if not (1 <= n <= 3):
        raise ValueError("d6は1～3個まで")
    return [random.randint(1, 6) for _ in range(n)]


def perform_roll(
    *,
    dice: int,
    bonus: int = 0,
    success_at: Optional[int] = None,
    plot_value: Optional[int] = None,
    inverted_wave: bool = False,
    choose_best_two: bool = False
) -> RollResult:
    """
    判定専用ロール関数

    dice            : 振るダイス数（1～3）
    bonus           : 達成値補正
    success_at      : 目標値
    plot_value      : 現在プロット値（ファンブル基準値）
    inverted_wave   : 逆凪状態かどうか
    choose_best_two : 3d6時に任意の2個を選ぶルール
    """

    # ① 逆凪チェック
    if inverted_wave:
        return RollResult(
            dice_results=[],
            raw_total=0,
            total=0,
            success=False,
            special=False,
            fumble=False
        )

    # ② ダイスロール
    dice_results = roll_d6(dice)

    # ③ 生出目合計（3d6特例）
    if dice == 3 and choose_best_two:
        sorted_dice = sorted(dice_results, reverse=True)
        raw_total = sorted_dice[0] + sorted_dice[1]
    else:
        raw_total = sum(dice_results)

    # ④ スペシャル／ファンブル判定（生出目のみ）
    special = (raw_total == 12)
    fumble = (raw_total == 2)

    # プロットによるファンブル基準
    if plot_value is not None and raw_total < plot_value:
        fumble = True
        special = False

    # ⑤ 達成値計算（スペシャル・ファンブルでも計算は行う）
    total = raw_total + bonus

    # ⑥ 成否判定
    if fumble:
        success = False
    elif special:
        success = True
    elif success_at is not None:
        success = total >= success_at
    else:
        success = True

    return RollResult(
        dice_results=dice_results,
        raw_total=raw_total,
        total=total,
        success=success,
        special=special,
        fumble=fumble
    )
