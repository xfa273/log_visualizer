#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Micromouse Log Visualizer
------------------------
カンマ区切りの高頻度ログデータを解析・表示するためのツール
時間(ms)を要素0とし、その他のパラメータ1-7をグラフ表示します
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import os
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class MicromouseLogVisualizer:
    """マイクロマウスのログデータを可視化するクラス"""
    
    def __init__(self):
        """初期化"""
        self.data = None
        self.columns = ['time_ms', 'param1', 'param2', 'param3', 
                       'param4', 'param5', 'param6', 'param7']
        
    def load_data_from_csv(self, file_path):
        """CSVファイルからデータをロード"""
        try:
            # データをロード（ヘッダーなしを想定）
            self.data = pd.read_csv(file_path, header=None, names=self.columns)
            print(f"読み込み完了: {len(self.data)} 行のデータ")
            return True
        except Exception as e:
            print(f"読み込みエラー: {e}")
            return False
            
    def load_data_from_string(self, data_string):
        """文字列からデータをロード"""
        try:
            # 文字列からデータフレームを作成
            string_io = io.StringIO(data_string)
            self.data = pd.read_csv(string_io, header=None, names=self.columns)
            print(f"読み込み完了: {len(self.data)} 行のデータ")
            return True
        except Exception as e:
            print(f"読み込みエラー: {e}")
            return False
    
    def plot_data(self):
        """データをプロット"""
        if self.data is None or len(self.data) == 0:
            print("プロットするデータがありません")
            return
        
        # プロット設定
        fig, axes = plt.subplots(7, 1, figsize=(10, 14), sharex=True)
        fig.suptitle('マイクロマウス ログデータ可視化')
        
        # 各パラメータをプロット
        for i in range(7):
            param_name = f'param{i+1}'
            axes[i].plot(self.data['time_ms'], self.data[param_name], 'b-')
            axes[i].set_ylabel(param_name)
            axes[i].grid(True)
        
        # X軸ラベルは最後のサブプロットのみに表示
        axes[6].set_xlabel('時間 (ms)')
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.95)
        return fig


class LogVisualizerGUI:
    """ログビジュアライザのGUIクラス"""
    
    def __init__(self, root):
        """初期化"""
        self.root = root
        self.root.title("マイクロマウス ログ可視化ツール")
        self.root.geometry("1024x768")
        
        self.visualizer = MicromouseLogVisualizer()
        
        # GUIコンポーネントのセットアップ
        self._setup_gui()
        
    def _setup_gui(self):
        """GUIのセットアップ"""
        # メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # コントロールフレーム（上部）
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # ファイル選択ボタン
        ttk.Button(control_frame, text="ファイルを開く", 
                   command=self._open_file).pack(side=tk.LEFT, padx=(0, 5))
        
        # テキスト入力フレーム（中央）
        text_frame = ttk.LabelFrame(main_frame, text="データ入力 (カンマ区切り)")
        text_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        # テキストエリア（スクロール付き）
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_area = tk.Text(text_frame, height=10)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text_scroll.config(command=self.text_area.yview)
        self.text_area.config(yscrollcommand=text_scroll.set)
        
        # テキスト入力用ボタンフレーム
        text_button_frame = ttk.Frame(main_frame)
        text_button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(text_button_frame, text="テキストデータをプロット", 
                   command=self._plot_from_text).pack(side=tk.LEFT)
        
        ttk.Button(text_button_frame, text="テキストをクリア", 
                   command=self._clear_text).pack(side=tk.LEFT, padx=(10, 0))
        
        # グラフ表示エリア（下部）
        self.graph_frame = ttk.Frame(main_frame)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # サンプルデータの表示
        self._show_sample_data()
        
    def _open_file(self):
        """ファイルを開く"""
        file_path = filedialog.askopenfilename(
            title="CSVファイルを選択",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.visualizer.load_data_from_csv(file_path):
                self._display_plot()
            else:
                messagebox.showerror("エラー", "ファイルの読み込みに失敗しました。")
    
    def _plot_from_text(self):
        """テキストエリアのデータをプロット"""
        data_string = self.text_area.get(1.0, tk.END)
        
        if data_string.strip():
            if self.visualizer.load_data_from_string(data_string):
                self._display_plot()
            else:
                messagebox.showerror("エラー", "入力データの解析に失敗しました。")
        else:
            messagebox.showinfo("情報", "データを入力してください。")
    
    def _clear_text(self):
        """テキストエリアをクリア"""
        self.text_area.delete(1.0, tk.END)
    
    def _display_plot(self):
        """プロットを表示"""
        # 既存のグラフをクリア
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # グラフを生成
        fig = self.visualizer.plot_data()
        
        if fig:
            # Matplotlibグラフを埋め込み
            canvas = FigureCanvasTkAgg(fig, self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _show_sample_data(self):
        """サンプルデータをテキストエリアに表示"""
        sample_data = """0,100,200,300,400,500,600,700
1,105,210,305,405,505,605,705
2,110,220,310,410,510,610,710
3,115,230,315,415,515,615,715
4,120,240,320,420,520,620,720"""
        
        self.text_area.insert(tk.END, sample_data)


def command_line_interface():
    """コマンドラインインターフェイス"""
    parser = argparse.ArgumentParser(description="マイクロマウス ログ可視化ツール")
    parser.add_argument('csv_file', nargs='?', help='CSVログファイル')
    parser.add_argument('--nogui', action='store_true', help='GUIを使用しない')
    
    args = parser.parse_args()
    
    visualizer = MicromouseLogVisualizer()
    
    # GUIモードかコマンドラインモードか判断
    if args.nogui and args.csv_file:
        # コマンドラインモード
        if visualizer.load_data_from_csv(args.csv_file):
            # プロットして表示
            visualizer.plot_data()
            plt.show()
    else:
        # GUIモード
        root = tk.Tk()
        app = LogVisualizerGUI(root)
        
        # コマンドライン引数でファイルが指定されていれば読み込む
        if args.csv_file and os.path.exists(args.csv_file):
            if visualizer.load_data_from_csv(args.csv_file):
                app._display_plot()
        
        root.mainloop()


if __name__ == "__main__":
    command_line_interface()
