#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STM32ログデータをmicromouse_log_visualizer用CSV形式に変換するスクリプト
"""

import re
import sys
import os

def parse_stm32_log_entry(entry_text):
    """
    STM32ログエントリをパースしてCSV行に変換
    
    Entry形式:
    Entry 0:
      count: 0
      target_omega: 1.240 (raw: 1067366482)
      actual_omega: -0.183 (raw: -1103408852)
      p_term_omega: 3.362 (raw: 1079453853)
      i_term_omega: 0.000 (raw: 0)
      d_term_omega: -0.000 (raw: -2147483648)
      motor_out_r: 3.362 (raw: 1079453853)
      motor_out_l: 3.362 (raw: 1079453853)
      timestamp: 16053
    
    CSV形式: timestamp,target_omega,actual_omega,p_term_omega,i_term_omega,d_term_omega,motor_out_r,motor_out_l
    """
    
    # 各パラメータを抽出するための正規表現
    patterns = {
        'timestamp': r'timestamp:\s*(\d+)',
        'target_omega': r'target_omega:\s*([-+]?\d*\.?\d+)',
        'actual_omega': r'actual_omega:\s*([-+]?\d*\.?\d+)',
        'p_term_omega': r'p_term_omega:\s*([-+]?\d*\.?\d+)',
        'i_term_omega': r'i_term_omega:\s*([-+]?\d*\.?\d+)',
        'd_term_omega': r'd_term_omega:\s*([-+]?\d*\.?\d+)',
        'motor_out_r': r'motor_out_r:\s*([-+]?\d*\.?\d+)',
        'motor_out_l': r'motor_out_l:\s*([-+]?\d*\.?\d+)'
    }
    
    values = {}
    
    # 各パラメータを抽出
    for param, pattern in patterns.items():
        match = re.search(pattern, entry_text)
        if match:
            values[param] = float(match.group(1))
        else:
            values[param] = 0.0  # デフォルト値
    
    # CSV行を作成（time_ms, param1~param7の順序）
    csv_row = f"{values['timestamp']},{values['target_omega']},{values['actual_omega']},{values['p_term_omega']},{values['i_term_omega']},{values['d_term_omega']},{values['motor_out_r']},{values['motor_out_l']}"
    
    return csv_row

def convert_stm32_log_to_csv(log_text):
    """
    STM32ログテキスト全体をCSV形式に変換
    """
    # エントリごとに分割
    entries = re.split(r'Entry \d+:', log_text)
    
    csv_lines = []
    
    for entry in entries[1:]:  # 最初の空要素をスキップ
        if entry.strip():
            try:
                csv_line = parse_stm32_log_entry(entry)
                csv_lines.append(csv_line)
            except Exception as e:
                print(f"エントリの変換でエラー: {e}")
                continue
    
    return '\n'.join(csv_lines)

def main():
    """メイン関数"""
    if len(sys.argv) != 3:
        print("使用方法: python convert_log_to_csv.py <入力ログファイル> <出力CSVファイル>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"入力ファイルが見つかりません: {input_file}")
        sys.exit(1)
    
    try:
        # ログファイルを読み込み
        with open(input_file, 'r', encoding='utf-8') as f:
            log_text = f.read()
        
        # CSV形式に変換
        csv_data = convert_stm32_log_to_csv(log_text)
        
        # CSVファイルに出力
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        print(f"変換完了: {input_file} -> {output_file}")
        print(f"変換されたデータ行数: {len(csv_data.splitlines())}")
        
        # 最初の数行を表示
        lines = csv_data.splitlines()
        print("\n最初の5行:")
        for i, line in enumerate(lines[:5]):
            print(f"{i+1}: {line}")
            
    except Exception as e:
        print(f"変換エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
