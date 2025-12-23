#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple Micromouse Log Visualizer
--------------------------------
標準ライブラリのみを使用したシンプルなログデータ可視化ツール
"""

import sys
import os
import csv
import argparse
from collections import defaultdict


class SimpleLogVisualizer:
    """シンプルなログビジュアライザ"""
    
    def __init__(self):
        """初期化"""
        self.data = []  # データを格納するリスト
        self.columns = ['time_ms', 'param1', 'param2', 'param3', 
                       'param4', 'param5', 'param6', 'param7']
    
    def load_from_file(self, file_path):
        """ファイルからデータを読み込む"""
        try:
            with open(file_path, 'r') as file:
                return self.load_from_string(file.read())
        except Exception as e:
            print(f"ファイル読み込みエラー: {e}")
            return False
    
    def load_from_string(self, data_string):
        """文字列からデータを読み込む"""
        try:
            self.data = []
            lines = data_string.strip().split('\n')
            
            for line in lines:
                # 空行をスキップ
                if not line.strip():
                    continue
                
                # カンマ区切りの値をパース
                values = line.split(',')
                
                # 少なくとも1つの値があることを確認
                if len(values) < 1:
                    continue
                
                # データが8つない場合は必要な分だけ0で埋める
                while len(values) < 8:
                    values.append('0')
                
                # 数値に変換
                try:
                    time_ms = int(values[0])
                    params = [float(v) for v in values[1:8]]
                    
                    # データを追加
                    row = [time_ms] + params
                    self.data.append(row)
                except ValueError:
                    print(f"無効なデータ行をスキップ: {line}")
            
            print(f"データ読み込み完了: {len(self.data)} 行")
            return True
        except Exception as e:
            print(f"データ解析エラー: {e}")
            return False
    
    def print_statistics(self):
        """データの統計情報を表示"""
        if not self.data:
            print("データがありません")
            return
        
        # 時間範囲
        start_time = self.data[0][0]
        end_time = self.data[-1][0]
        duration = end_time - start_time
        
        print("\n===== データ統計 =====")
        print(f"データ点数: {len(self.data)}")
        print(f"時間範囲: {start_time} ms ～ {end_time} ms (期間: {duration} ms)")
        print(f"サンプリング周波数: 約 {len(self.data) * 1000 / duration if duration > 0 else 'N/A'} Hz")
        
        # 各パラメータの統計
        param_min = [float('inf')] * 7
        param_max = [float('-inf')] * 7
        param_sum = [0] * 7
        
        for row in self.data:
            for i in range(7):
                val = row[i+1]  # パラメータは1から始まる
                param_min[i] = min(param_min[i], val)
                param_max[i] = max(param_max[i], val)
                param_sum[i] += val
        
        param_avg = [param_sum[i] / len(self.data) for i in range(7)]
        
        # パラメータの統計を表示
        print("\n各パラメータの統計:")
        print("パラメータ  |  最小値  |  最大値  |  平均値  |  範囲")
        print("-" * 60)
        
        for i in range(7):
            print(f"パラメータ{i+1} | {param_min[i]:8.2f} | {param_max[i]:8.2f} | {param_avg[i]:8.2f} | {param_max[i] - param_min[i]:8.2f}")
    
    def print_ascii_chart(self, param_index, width=80, height=20):
        """指定されたパラメータのASCIIチャートを表示"""
        if not self.data or param_index < 1 or param_index > 7:
            print("有効なパラメータが指定されていません")
            return
        
        # パラメータデータを取得
        times = [row[0] for row in self.data]
        values = [row[param_index] for row in self.data]
        
        if not values:
            print("データがありません")
            return
        
        # データの範囲を計算
        min_val = min(values)
        max_val = max(values)
        val_range = max_val - min_val
        
        if val_range == 0:  # 全て同じ値
            val_range = 1  # ゼロ除算を避ける
        
        # チャートを初期化
        chart = [[' ' for _ in range(width)] for _ in range(height)]
        
        # データ点の数
        n_points = len(values)
        
        # データ点をチャートにマッピング
        for i in range(min(width, n_points)):
            # 表示するデータポイントのインデックス
            data_idx = int(i * n_points / width) if n_points > width else i
            
            # Y座標に変換（正規化して反転）
            val = values[data_idx]
            y_pos = height - 1 - int((val - min_val) / val_range * (height - 1))
            
            # 範囲内に収める
            y_pos = max(0, min(height - 1, y_pos))
            
            # 点をプロット
            chart[y_pos][i] = '*'
        
        # チャートを出力
        print(f"\nパラメータ{param_index} のASCIIチャート (時間範囲: {times[0]}ms～{times[-1]}ms):")
        print(f"値の範囲: {min_val:.2f} ～ {max_val:.2f}")
        print('-' * width)
        
        for row in chart:
            print(''.join(row))
        
        print('-' * width)
    
    def export_filtered_data(self, output_path, filter_ratio=1):
        """データをフィルタリングしてエクスポート"""
        if not self.data:
            print("エクスポートするデータがありません")
            return False
        
        try:
            # フィルタリング（間引き）
            step = max(1, int(filter_ratio))
            filtered_data = self.data[::step]
            
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                for row in filtered_data:
                    writer.writerow(row)
            
            print(f"データを {output_path} にエクスポートしました（{len(filtered_data)}行）")
            return True
        except Exception as e:
            print(f"エクスポートエラー: {e}")
            return False


def print_help():
    """ヘルプメッセージを表示"""
    print("マイクロマウス ログ可視化ツール - シンプル版")
    print("\n使用方法:")
    print("  python simple_visualizer.py [コマンド] [オプション]\n")
    
    print("コマンド:")
    print("  load <file.csv>      CSVファイルからデータをロード")
    print("  stats               ロードされたデータの統計情報を表示")
    print("  chart <param_idx>   指定したパラメータのASCIIチャートを表示")
    print("  export <file.csv>   データをCSVファイルにエクスポート")
    print("  help                このヘルプメッセージを表示")
    print("  exit                プログラムを終了")
    print("\n例:")
    print("  load data.csv")
    print("  stats")
    print("  chart 1    # パラメータ1のチャートを表示")


def interactive_mode():
    """インタラクティブモード"""
    visualizer = SimpleLogVisualizer()
    print("マイクロマウス ログ可視化ツール - シンプル版")
    print("コマンドを入力してください（'help'でヘルプ表示、'exit'で終了）")
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if not command:
                continue
                
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == 'exit':
                break
            elif cmd == 'help':
                print_help()
            elif cmd == 'load':
                if len(parts) < 2:
                    print("ファイル名を指定してください: load <file.csv>")
                else:
                    visualizer.load_from_file(parts[1])
            elif cmd == 'stats':
                visualizer.print_statistics()
            elif cmd == 'chart':
                if len(parts) < 2:
                    print("パラメータ番号を指定してください: chart <param_idx>")
                else:
                    try:
                        param_idx = int(parts[1])
                        visualizer.print_ascii_chart(param_idx)
                    except ValueError:
                        print("パラメータ番号は1～7の整数で指定してください")
            elif cmd == 'export':
                if len(parts) < 2:
                    print("出力ファイル名を指定してください: export <file.csv>")
                else:
                    filter_ratio = 1
                    if len(parts) > 2:
                        try:
                            filter_ratio = int(parts[2])
                        except ValueError:
                            pass
                    visualizer.export_filtered_data(parts[1], filter_ratio)
            elif cmd == 'input':
                print("データを直接入力してください（入力終了は空行+Enterで）:")
                lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    lines.append(line)
                data_str = '\n'.join(lines)
                visualizer.load_from_string(data_str)
            else:
                print(f"不明なコマンド: {cmd}")
                print("'help'と入力するとコマンド一覧を表示します")
                
        except KeyboardInterrupt:
            print("\nプログラムを終了します")
            break
        except Exception as e:
            print(f"エラー: {e}")


def process_command_line():
    """コマンドライン引数を処理"""
    parser = argparse.ArgumentParser(description="マイクロマウス ログ可視化ツール - シンプル版")
    parser.add_argument('file', nargs='?', help='CSVファイルパス（省略時はインタラクティブモード）')
    parser.add_argument('--stats', action='store_true', help='統計情報を表示')
    parser.add_argument('--chart', type=int, choices=range(1, 8), help='ASCIIチャートを表示するパラメータ番号（1-7）')
    
    args = parser.parse_args()
    
    if not args.file:
        interactive_mode()
        return
    
    visualizer = SimpleLogVisualizer()
    if visualizer.load_from_file(args.file):
        if args.stats:
            visualizer.print_statistics()
        if args.chart:
            visualizer.print_ascii_chart(args.chart)


if __name__ == "__main__":
    process_command_line()
