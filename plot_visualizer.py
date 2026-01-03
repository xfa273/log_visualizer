#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Micromouse Log Graphic Visualizer
--------------------------------
マイクロマウスの高頻度ログデータをグラフィカルに可視化するツール
"""

import os
import sys
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# フォント設定は無効化して英字のみ使用


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from datetime import datetime


def _add_venv_site_packages_to_syspath() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = glob.glob(os.path.join(script_dir, 'venv', 'lib', 'python*', 'site-packages'))
    for p in sorted(candidates):
        if os.path.isdir(p) and p not in sys.path:
            sys.path.insert(0, p)


_add_venv_site_packages_to_syspath()

class LogVisualizer:
    """ログデータのグラフィカル可視化クラス"""
    
    def __init__(self):
        """初期化"""
        self.data = None
        self.default_columns = ['time_ms', 'param1', 'param2', 'param3', 
                               'param4', 'param5', 'param6', 'param7']
        self.user_columns = None
    
    def load_data(self, file_path):
        """ファイルからデータをロード"""
        try:
            # データをロード（ヘッダーなしを想定）
            self.data = pd.read_csv(file_path, header=None)
            
            # カラム数が8でない場合の処理
            if len(self.data.columns) != 8:
                print(f"警告: データには {len(self.data.columns)} 列あります（想定は8列）")
                # 不足している列を0で埋める
                for i in range(len(self.data.columns), 8):
                    self.data[i] = 0
                # 余分な列を無視
                self.data = self.data.iloc[:, :8]
            
            # カラム名を設定
            if self.user_columns:
                self.data.columns = self.user_columns
            else:
                self.data.columns = self.default_columns
                
            print(f"データ読み込み完了: {len(self.data)} 行")
            return True
        except Exception as e:
            print(f"データ読み込みエラー: {e}")
            return False
    
    def set_column_names(self, names):
        """カラム名を設定"""
        if len(names) == 8:
            self.user_columns = names
            if self.data is not None:
                self.data.columns = names
            return True
        return False

    def plot_data(self, ax=None, params_to_plot=None):
        """データをプロット
        
        Args:
            ax: プロット対象のaxes（Noneならば新しいFigureを作成）
            params_to_plot: プロットするパラメータのリスト（Noneならすべてプロット）
        """
        if self.data is None:
            print("プロット対象のデータがありません")
            return None
        
        # プロットするパラメータの選択（デフォルトはパラメータ1～7）
        if params_to_plot is None:
            params_to_plot = self.data.columns[1:] # 時間以外の全パラメータ
            
        # 新しいFigureを作成するかどうか
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        else:
            fig = ax.figure
            
        # 各パラメータをプロット
        for param in params_to_plot:
            ax.plot(self.data['time_ms'], self.data[param], '-', label=param)
            
        # グラフの設定
        ax.set_xlabel('時間 (ms)')
        ax.set_ylabel('値')
        ax.grid(True)
        ax.legend()
        
        return fig


class LogVisualizerApp:
    """ログビジュアライザのGUIアプリケーション"""
    
    def __init__(self, root):
        """初期化"""
        self.root = root
        self.root.title("Micromouse Log Visualizer")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        self.visualizer = LogVisualizer()
        
        # 表示するパラメータの設定
        self.params_to_plot = []
        
        # 現在開いているファイル
        self.current_file = None
        
        # 最近ファイル一覧の基準フォルダ（既定はツール内 logs、なければWS内 logs）
        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_dir = os.environ.get('MICROMOUSE_LOG_DIR')
        candidates = []
        if env_dir:
            candidates.append(os.path.expanduser(env_dir))
        if sys.platform == 'darwin':
            candidates.append(os.path.expanduser('~/Documents/micromouse_logs'))
        candidates.append(os.path.join(script_dir, 'logs'))

        self.recent_dir = None
        for d in candidates:
            if os.path.isdir(d):
                self.recent_dir = d
                break
        if self.recent_dir is None:
            self.recent_dir = candidates[0] if candidates else os.path.expanduser('~')

        try:
            os.makedirs(self.recent_dir, exist_ok=True)
        except Exception:
            pass
        
        # GUIの初期化
        self._setup_gui()
    
    def _setup_gui(self):
        """GUIの初期化"""
        # メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左サイドパネル（コントロール用）
        self.side_panel = ttk.Frame(main_frame, width=250)
        self.side_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # ファイル操作フレーム
        file_frame = ttk.LabelFrame(self.side_panel, text="File Operations")
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(file_frame, text="Open File", command=self._open_file).pack(fill=tk.X, padx=5, pady=5)
        
        # 最近ファイル表示
        recent_frame = ttk.LabelFrame(self.side_panel, text="Recent CSVs")
        recent_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        
        folder_row = ttk.Frame(recent_frame)
        folder_row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(folder_row, text="Folder:").pack(side=tk.LEFT)
        self.recent_dir_var = tk.StringVar(value=self.recent_dir)
        ttk.Entry(folder_row, textvariable=self.recent_dir_var, width=22).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(folder_row, text="Change", command=self._choose_recent_dir).pack(side=tk.LEFT, padx=2)
        ttk.Button(folder_row, text="Refresh", command=self._populate_recent_files).pack(side=tk.LEFT, padx=2)
        
        cols = ("name", "modified", "size")
        self.recent_tree = ttk.Treeview(recent_frame, columns=cols, show="headings", height=8)
        self.recent_tree.heading("name", text="Name")
        self.recent_tree.heading("modified", text="Modified")
        self.recent_tree.heading("size", text="Size")
        self.recent_tree.column("name", width=140, anchor=tk.W)
        self.recent_tree.column("modified", width=140, anchor=tk.W)
        self.recent_tree.column("size", width=70, anchor=tk.E)
        self.recent_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.recent_tree.bind("<Double-1>", lambda e: self._open_selected_recent())
        
        ttk.Button(recent_frame, text="Open Selected", command=self._open_selected_recent).pack(fill=tk.X, padx=5, pady=5)
        
        # 現在のファイル表示ラベル
        self.file_label = ttk.Label(file_frame, text="File: None", wraplength=220)
        self.file_label.pack(fill=tk.X, padx=5, pady=5)
        
        # データ表示範囲設定
        range_frame = ttk.LabelFrame(self.side_panel, text="Display Range")
        range_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # X軸範囲
        ttk.Label(range_frame, text="X-axis range (time[ms]):").pack(anchor=tk.W, padx=5, pady=(5, 0))
        x_range_frame = ttk.Frame(range_frame)
        x_range_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(x_range_frame, text="Start:").pack(side=tk.LEFT)
        self.x_min_var = tk.StringVar(value="")
        ttk.Entry(x_range_frame, textvariable=self.x_min_var, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(x_range_frame, text="End:").pack(side=tk.LEFT, padx=(10, 0))
        self.x_max_var = tk.StringVar(value="")
        ttk.Entry(x_range_frame, textvariable=self.x_max_var, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(range_frame, text="Reset Range", command=self._reset_range).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(range_frame, text="Apply Range", command=self._apply_range).pack(fill=tk.X, padx=5, pady=5)
        
        # パラメータ表示設定
        param_frame = ttk.LabelFrame(self.side_panel, text="Parameter Settings")
        param_frame.pack(fill=tk.X, padx=5, pady=5, expand=True)
        
        # パラメータ名と選択チェックボックス
        self.param_vars = []
        self.param_entries = []
        param_box = ttk.Frame(param_frame)
        param_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # スクロール可能なキャンバスを作成
        canvas = tk.Canvas(param_box)
        scrollbar = ttk.Scrollbar(param_box, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # パラメータ設定（7つのパラメータ）
        for i in range(7):
            param_frame = ttk.Frame(scrollable_frame)
            param_frame.pack(fill=tk.X, pady=2)
            
            var = tk.BooleanVar(value=True)  # 初期値はTrue（すべて表示）
            self.param_vars.append(var)
            
            ttk.Checkbutton(param_frame, variable=var, command=self._update_plot).pack(side=tk.LEFT)
            
            ttk.Label(param_frame, text=f"Param{i+1}:").pack(side=tk.LEFT, padx=(2, 5))
            
            entry_var = tk.StringVar(value=f"param{i+1}")
            entry = ttk.Entry(param_frame, textvariable=entry_var, width=15)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.param_entries.append(entry_var)
        
        # パラメータ名適用ボタンをスクロール領域の下に配置
        ttk.Button(param_frame, text="Apply Names", command=self._apply_names).pack(fill=tk.X, padx=5, pady=5)
        
        # グラフ表示エリア
        self.graph_frame = ttk.Frame(main_frame)
        self.graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # スプリッター
        ttk.Separator(main_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=2, before=self.graph_frame)
        
        # ステータスバー
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 初回の最近ファイル一覧を構築
        self._populate_recent_files()
        
    def _open_file(self):
        """ファイルを開く"""
        file_path = filedialog.askopenfilename(
            title="Select Log Data File",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=self.recent_dir if os.path.isdir(self.recent_dir) else os.path.expanduser('~')
        )
        
        if not file_path:
            return
        
        self._load_file(file_path)

    def _load_file(self, file_path):
        """指定ファイルを読み込んで表示更新"""
        # ステータス更新
        self.status_var.set(f"Loading file: {os.path.basename(file_path)}")
        self.root.update()
        if self.visualizer.load_data(file_path):
            self.current_file = file_path
            self.file_label.config(text=f"File: {os.path.basename(file_path)}")
            self._apply_default_names()
            self._update_plot()
            self.status_var.set(f"File loaded: {os.path.basename(file_path)}")
        else:
            messagebox.showerror("Error", "Failed to load file.")
            self.status_var.set("File loading error")

    def _choose_recent_dir(self):
        """最近ファイル一覧のフォルダを選択"""
        d = filedialog.askdirectory(initialdir=self.recent_dir if os.path.isdir(self.recent_dir) else os.path.expanduser('~'),
                                    title="Select folder for Recent CSVs")
        if not d:
            return
        self.recent_dir = d
        self.recent_dir_var.set(self.recent_dir)
        self._populate_recent_files()

    def _populate_recent_files(self):
        """recent_dir からCSVを新しい順で一覧化"""
        try:
            if not hasattr(self, 'recent_tree'):
                return
            for iid in self.recent_tree.get_children():
                self.recent_tree.delete(iid)
            entries = []
            if os.path.isdir(self.recent_dir):
                with os.scandir(self.recent_dir) as it:
                    for e in it:
                        if e.is_file() and e.name.lower().endswith('.csv'):
                            try:
                                st = e.stat()
                            except Exception:
                                continue
                            entries.append((e.name, st.st_mtime, st.st_size))
            # 新しい順にソート
            entries.sort(key=lambda x: x[1], reverse=True)
            # 先頭が左上に来る
            for name, mtime, size in entries[:200]:
                mod = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                size_kb = f"{size/1024:.1f} KB"
                self.recent_tree.insert('', 'end', values=(name, mod, size_kb))
        except Exception as ex:
            # エラーはステータスバーに表示
            self.status_var.set(f"Recent list error: {ex}")

    def _open_selected_recent(self):
        """最近一覧から選択中のファイルを開く"""
        sel = self.recent_tree.selection()
        if not sel:
            return
        values = self.recent_tree.item(sel[0], 'values')
        if not values:
            return
        name = values[0]
        file_path = os.path.join(self.recent_dir, name)
        if os.path.exists(file_path):
            self._load_file(file_path)
    
    def _apply_default_names(self):
        """デフォルトのパラメータ名を設定"""
        # interrupt.cから読み取った情報に基づく
        default_names = [
            'time_ms',  # タイムスタンプ
            'target_distance',  # 目標距離
            'real_distance',    # 実際の距離
            'PD_distance',      # KP_DISTANCE * distance_error
            'PI_distance',      # KI_DISTANCE * distance_integral 
            'PD_distance_d',    # KD_DISTANCE * distance_error_error
            'param6',           # 未使用
            'param7'            # 未使用
        ]
        
        # Entryに値を設定
        for i, name in enumerate(default_names[1:]):
            self.param_entries[i].set(name)
    
    def _apply_names(self):
        """パラメータ名を適用"""
        # カラム名のリスト作成
        column_names = ['time_ms']  # 時間は固定
        for entry_var in self.param_entries:
            name = entry_var.get()
            if not name:  # 空の場合はデフォルト名
                name = f"param{len(column_names)}"
            column_names.append(name)
        
        # ビジュアライザにカラム名を設定
        if self.visualizer.set_column_names(column_names):
            self._update_plot()
            self.status_var.set("Parameter names updated")
        else:
            self.status_var.set("Failed to update parameter names")
    
    def _update_plot(self):
        """プロットを更新"""
        if self.visualizer.data is None:
            return
        
        # 既存のグラフをクリア
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # 表示するパラメータを決定
        self.params_to_plot = []
        column_names = list(self.visualizer.data.columns[1:])  # 0はtime_ms
        
        for i, var in enumerate(self.param_vars):
            if var.get() and i < len(column_names):
                self.params_to_plot.append(column_names[i])
        
        # データが選択されていない場合
        if not self.params_to_plot:
            ttk.Label(self.graph_frame, text="Please select parameters to display").pack(expand=True)
            return
        
        # プロットを作成
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        
        # 各パラメータをプロット
        for param in self.params_to_plot:
            ax.plot(self.visualizer.data['time_ms'], self.visualizer.data[param], '-', label=param)
            
        # 表示範囲の設定
        self._apply_current_range(ax)
        
        # グラフの設定
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Value')
        ax.set_title('Micromouse Log Data')
        ax.grid(True)
        ax.legend()
        
        # グラフをGUIに埋め込み
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        
        # ツールバー追加
        toolbar_frame = ttk.Frame(self.graph_frame)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        
        # キャンバス配置
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def _reset_range(self):
        """表示範囲をリセット"""
        self.x_min_var.set("")
        self.x_max_var.set("")
        self._update_plot()
        self.status_var.set("Display range reset")
    
    def _apply_range(self):
        """表示範囲を適用"""
        self._update_plot()
        self.status_var.set("Display range updated")
    
    def _apply_current_range(self, ax):
        """現在の範囲設定をaxに適用"""
        # X軸範囲の設定
        try:
            x_min = self.x_min_var.get()
            if x_min:
                x_min = float(x_min)
            else:
                x_min = None
                
            x_max = self.x_max_var.get()
            if x_max:
                x_max = float(x_max)
            else:
                x_max = None
                
            if x_min is not None or x_max is not None:
                ax.set_xlim(left=x_min, right=x_max)
        except ValueError:
            # 数値に変換できない場合は無視
            pass


def main():
    """メイン関数"""
    root = tk.Tk()
    app = LogVisualizerApp(root)
    
    # コマンドライン引数の処理
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        app.visualizer.load_data(sys.argv[1])
        app.current_file = sys.argv[1]
        app.file_label.config(text=f"ファイル: {os.path.basename(sys.argv[1])}")
        app._apply_default_names()
        app._update_plot()
    
    root.mainloop()


if __name__ == "__main__":
    main()
