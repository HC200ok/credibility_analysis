import unittest
import numpy as np
import sys
sys.path.append("..")
import align
from nltk.corpus import stopwords
import MeCab


class TestAlign(unittest.TestCase):
    def test_align_1(self):
        base_sentence = "京都市 洪水 被害".split(" ")
        target_sentence = "洪水 3人 死亡 京都市".split(" ")
        aligned = align.align(base_sentence, target_sentence)
        true_align = ["京都市", "洪水", None]
        self.assertEqual(aligned, true_align)

    def test_align_2(self):
        base_sentence = "アメリカ 保護貿易 蔓延 関税 引き上げ".split(" ")
        target_sentence = "関税 問題 米国 保護貿易 推進".split(" ")
        aligned = align.align(base_sentence, target_sentence)
        true_align = ["米国", "保護貿易", None, "関税", None]
        self.assertEqual(aligned, true_align)

    def test_aligns(self):
        base_sentence = "アメリカ 保護貿易 蔓延 関税 引き上げ".split(" ")
        targets =[
            "関税 問題 米国 保護貿易 推進".split(),
            "アメリカ 主導 世界 経済".split(),
            "保護貿易 自由貿易 比較".split()
        ]
        aligns = align.aligns(base_sentence, targets, threshold=0.50)
        true_aligns = [
            ["米国", "保護貿易", None, "関税", None],
            ["アメリカ", None, None, None, None],
            [None, "保護貿易", None, None, None]
        ]

        for aligned, true_aligns in zip(aligns, true_aligns):
            self.assertListEqual(aligned, true_aligns)
        
    def test_aligns2Bs(self):
        base_sentence = "アメリカ 保護貿易 蔓延 関税 引き上げ".split(" ")
        targets =[
            "関税 問題 米国 保護貿易 推進".split(),
            "アメリカ 主導 世界 経済".split(),
            "保護貿易 自由貿易 比較".split()
        ]
        aligns = align.aligns(base_sentence, targets, threshold=0.50)
        Bs = align.aligns2Bs(aligns)
        true_Bs = [
            [True, True, False, True, False],
            [True, False, False, False, False],
            [False, True, False, False, False]
        ]

        for B, true_B in zip(Bs, true_Bs):
            self.assertListEqual(B, true_B)

    def test_sum_aligns(self):
        base_sentence = "アメリカ 保護貿易 蔓延 関税 引き上げ".split(" ")
        targets =[
            "関税 問題 米国 保護貿易 推進".split(),
            "アメリカ 主導 世界 経済".split(),
            "保護貿易 自由貿易 比較".split()
        ]
        aligns = align.aligns(base_sentence, targets, threshold=0.50)
        Bs = align.aligns2Bs(aligns)
        A = align.sum_aligns(Bs).tolist()
        true_A = [2,2,0,1,0]

        self.assertListEqual(A, true_A)

    def test_W(self):
        base_sentence = "アメリカ 保護貿易 蔓延 関税 引き上げ".split(" ")
        targets =[
            "関税 問題 米国 保護貿易 推進".split(),
            "アメリカ 主導 世界 経済".split(),
            "保護貿易 自由貿易 比較".split()
        ]
        aligns = align.aligns(base_sentence, targets, threshold=0.50)
        Bs = align.aligns2Bs(aligns)
        A = align.sum_aligns(Bs)
        Ws = align.W(A, Bs).tolist()
        true_Ws = [
            [2,2,0,1,0],
            [2,0,0,0,0],
            [0,2,0,0,0]
        ]
        for W, true_W in zip(Ws, true_Ws):
            self.assertListEqual(W, true_W)

    def test_fmt_sentence(self):
        tagger = MeCab.Tagger("-Owakati")
        tokenize = tagger.parse
        stps = stopwords.words("japanese")        
        test_sentence = "アメリカが主導する世界の経済の行方は！？"
        sent_fmt = align.fmt_sentence(test_sentence, tokenize, stps)
        true_fmt = ["アメリカ", "主導", "世界", "経済", "行方"]
        self.assertListEqual(sent_fmt, true_fmt)

    def test_score(self):
        Ws = [
            [2,2,0,1,0],
            [2,0,0,0,0],
            [0,2,0,0,0]
        ]
        score = align.score(Ws).tolist()
        true_score = [5, 2, 2]
        self.assertListEqual(score, true_score)

    def test_execute(self):
        tagger = MeCab.Tagger("-Owakati")
        tokenize = tagger.parse
        stps = stopwords.words("japanese")        
        base_sentence = "アメリカ、保護貿易蔓延、関税引き上げか"
        targets =[
            "関税問題で米国、保護貿易を推進",
            "アメリカ主導の世界経済",
            "保護貿易と自由貿易を比較"
        ]
        ss = align.execute(base_sentence, targets, tokenize, stps, threshold=0.5).tolist()
        self.assertListEqual([9, 5, 7], ss)


if __name__ == "__main__":
    unittest.main()
