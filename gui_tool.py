#!/usr/bin/env python3
"""
高精度顔モザイク処理GUI版
OpenCV YuNetによる高精度検出
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
from face_detector import AdvancedImageProcessor, get_system_info


class AdvancedFaceMosaicGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("高精度顔モザイク処理ツール")
        self.root.geometry("700x600")
        
        # 処理用オブジェクト
        self.processor = None
        self.processing = False
        
        self.setup_ui()
        self.show_system_info()
        
    def setup_ui(self):
        """UI要素の設定"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 入力ディレクトリ選択
        ttk.Label(main_frame, text="入力ディレクトリ:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var, width=60)
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(input_frame, text="参照", 
                  command=self.select_input_dir).grid(row=0, column=1)
        
        # 出力ディレクトリ選択
        ttk.Label(main_frame, text="出力ディレクトリ:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=60)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(output_frame, text="参照", 
                  command=self.select_output_dir).grid(row=0, column=1)
        
        # 設定フレーム
        settings_frame = ttk.LabelFrame(main_frame, text="設定", padding="10")
        settings_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # 検出手法選択
        ttk.Label(settings_frame, text="検出手法:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.method_var = tk.StringVar(value="yunet")
        method_combo = ttk.Combobox(settings_frame, textvariable=self.method_var, 
                                   values=["yunet"],
                                   state="readonly", width=15)
        method_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # 検出手法の説明
        method_info = ttk.Label(settings_frame, text="auto: 利用可能な全手法を精度順に試行（推奨）", 
                               font=("", 9), foreground="gray")
        method_info.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        
        # モザイク設定
        ttk.Label(settings_frame, text="モザイクの粗さ:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.ratio_var = tk.DoubleVar(value=0.1)
        ratio_scale = ttk.Scale(settings_frame, from_=0.01, to=1.0, 
                               variable=self.ratio_var, orient=tk.HORIZONTAL, length=200)
        ratio_scale.grid(row=1, column=1, padx=10, pady=5)
        
        self.ratio_label = ttk.Label(settings_frame, text="0.10")
        self.ratio_label.grid(row=1, column=2, sticky=tk.W, padx=10, pady=5)
        
        # スケール値の更新
        ratio_scale.configure(command=self.update_ratio_label)
        
        # 検出手法変更時のコールバック
        method_combo.bind('<<ComboboxSelected>>', self.on_method_changed)
        
        # 進捗バー
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=500)
        self.progress_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # ステータスラベル
        self.status_var = tk.StringVar(value="準備完了")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=6, column=0, columnspan=2, pady=5)
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        self.process_button = ttk.Button(button_frame, text="処理開始", 
                                        command=self.start_processing)
        self.process_button.grid(row=0, column=0, padx=5)
        
        self.cancel_button = ttk.Button(button_frame, text="キャンセル", 
                                       command=self.cancel_processing, state=tk.DISABLED)
        self.cancel_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="システム情報", 
                  command=self.show_detailed_system_info).grid(row=0, column=2, padx=5)
        
        ttk.Button(button_frame, text="Proxy情報", 
                  command=self.show_proxy_info).grid(row=0, column=3, padx=5)
        
        ttk.Button(button_frame, text="終了", 
                  command=self.root.quit).grid(row=0, column=4, padx=5)
        
        # ログ表示エリア
        log_frame = ttk.LabelFrame(main_frame, text="ログ", padding="5")
        log_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # グリッドの重み設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
        input_frame.columnconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def show_system_info(self):
        """システム情報をログに表示"""
        info = get_system_info()
        self.log("=== システム情報 ===")
        for key, value in info.items():
            self.log(f"{key}: {value}")
        
        self.log("\n=== 検出手法 ===")
        if info['yunet_supported']:
            self.log("✓ OpenCV YuNet (唯一の十分な精度を持つ手法)")
        else:
            self.log("✗ OpenCV YuNet (OpenCV 4.5.4以上が必要)")
            self.log("  エラー: 高精度な顔検出手法が利用できません")
        
        self.log("")
        self.log("注意: YuNetのみが実用的な精度を提供します。")
        self.log("他の手法は検証により精度不十分と判明したため削除されました。")
        self.log("")
        
    def show_detailed_system_info(self):
        """詳細システム情報をダイアログで表示"""
        info = get_system_info()
        
        info_window = tk.Toplevel(self.root)
        info_window.title("詳細システム情報")
        info_window.geometry("500x400")
        
        text_widget = scrolledtext.ScrolledText(info_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, "=== 詳細システム情報 ===\n\n")
        for key, value in info.items():
            text_widget.insert(tk.END, f"{key}: {value}\n")
        
        text_widget.insert(tk.END, "\n=== 検出手法 ===\n")
        if info['yunet_supported']:
            text_widget.insert(tk.END, "✓ OpenCV YuNet Face Detection\n")
            text_widget.insert(tk.END, "  - 検証により唯一十分な精度を持つ手法\n")
            text_widget.insert(tk.END, "  - 軽量・高精度な最新モデル\n")
            text_widget.insert(tk.END, "  - OpenCV標準搭載、追加インストール不要\n")
        else:
            text_widget.insert(tk.END, "✗ OpenCV YuNet Face Detection\n")
            text_widget.insert(tk.END, "  要件: OpenCV 4.5.4以上\n")
            text_widget.insert(tk.END, "  エラー: 高精度な顔検出手法が利用できません\n")
        
        text_widget.insert(tk.END, "\n=== 削除された手法 ===\n")
        text_widget.insert(tk.END, "✗ MediaPipe Face Detection (精度不十分により削除)\n")
        text_widget.insert(tk.END, "✗ Dlib Face Detection (精度不十分により削除)\n")
        text_widget.insert(tk.END, "✗ OpenCV DNN/Haar (低精度により以前に削除)\n")
        text_widget.insert(tk.END, "\n注意: 検証の結果、YuNetのみが実用的な精度を提供します。\n")
        
        text_widget.config(state=tk.DISABLED)
        
    def show_proxy_info(self):
        """Proxy情報をダイアログで表示"""
        try:
            from proxy_utils import get_proxy_manager
            
            proxy_window = tk.Toplevel(self.root)
            proxy_window.title("Proxy設定情報")
            proxy_window.geometry("600x400")
            
            text_widget = scrolledtext.ScrolledText(proxy_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            proxy_manager = get_proxy_manager()
            
            text_widget.insert(tk.END, "=== Proxy設定情報 ===\n\n")
            
            if proxy_manager.is_proxy_enabled():
                text_widget.insert(tk.END, "Proxy設定: 有効\n\n")
                
                proxy_info = proxy_manager.get_proxy_info()
                text_widget.insert(tk.END, f"HTTP Proxy: {proxy_info.get('http_proxy', 'なし')}\n")
                text_widget.insert(tk.END, f"HTTPS Proxy: {proxy_info.get('https_proxy', 'なし')}\n")
                text_widget.insert(tk.END, f"No Proxy: {proxy_info.get('no_proxy', 'なし')}\n")
                
                if proxy_info.get('proxy_auth'):
                    text_widget.insert(tk.END, "Proxy認証: 有効\n")
                else:
                    text_widget.insert(tk.END, "Proxy認証: 無効\n")
                
                # 接続テスト
                text_widget.insert(tk.END, "\n=== 接続テスト ===\n")
                text_widget.insert(tk.END, "テスト中...\n")
                text_widget.update()
                
                if proxy_manager.test_connection():
                    text_widget.insert(tk.END, "✓ Proxy経由での接続に成功しました\n")
                else:
                    text_widget.insert(tk.END, "✗ Proxy経由での接続に失敗しました\n")
            else:
                text_widget.insert(tk.END, "Proxy設定: 無効\n\n")
                text_widget.insert(tk.END, "環境変数でProxy設定が検出されませんでした。\n")
                text_widget.insert(tk.END, "企業環境等でProxyが必要な場合は、以下の環境変数を設定してください:\n\n")
                text_widget.insert(tk.END, "HTTP_PROXY=http://proxy.company.com:8080\n")
                text_widget.insert(tk.END, "HTTPS_PROXY=http://proxy.company.com:8080\n")
                text_widget.insert(tk.END, "NO_PROXY=localhost,127.0.0.1\n")
            
            text_widget.config(state=tk.DISABLED)
            
        except ImportError:
            messagebox.showwarning("警告", "Proxy対応モジュールが見つかりません")
        except Exception as e:
            messagebox.showerror("エラー", f"Proxy情報の取得に失敗しました:\n{e}")
        
    def update_ratio_label(self, value):
        """モザイク比率ラベルの更新"""
        self.ratio_label.config(text=f"{float(value):.2f}")
        
    def on_method_changed(self, event):
        """検出手法変更時の処理"""
        method = self.method_var.get()
        self.log(f"検出手法を '{method}' に変更しました")
        
        # プロセッサを再初期化
        if hasattr(self, 'processor') and self.processor:
            self.processor = AdvancedImageProcessor(detection_method=method)
        
    def select_input_dir(self):
        """入力ディレクトリ選択"""
        directory = filedialog.askdirectory(title="入力ディレクトリを選択")
        if directory:
            self.input_var.set(directory)
            
    def select_output_dir(self):
        """出力ディレクトリ選択"""
        directory = filedialog.askdirectory(title="出力ディレクトリを選択")
        if directory:
            self.output_var.set(directory)
            
    def log(self, message):
        """ログメッセージの追加"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def validate_inputs(self):
        """入力値の検証"""
        input_dir = self.input_var.get().strip()
        output_dir = self.output_var.get().strip()
        
        if not input_dir:
            messagebox.showerror("エラー", "入力ディレクトリを選択してください")
            return False
            
        if not output_dir:
            messagebox.showerror("エラー", "出力ディレクトリを選択してください")
            return False
            
        if not os.path.exists(input_dir):
            messagebox.showerror("エラー", f"入力ディレクトリが存在しません:\n{input_dir}")
            return False
            
        if not os.path.isdir(input_dir):
            messagebox.showerror("エラー", f"入力パスがディレクトリではありません:\n{input_dir}")
            return False
            
        return True
        
    def start_processing(self):
        """処理開始"""
        if not self.validate_inputs():
            return
            
        if self.processing:
            return
        
        # プロセッサ初期化
        method = self.method_var.get()
        self.processor = AdvancedImageProcessor(detection_method=method)
        
        # 確認ダイアログ
        message = f"処理を開始しますか？\n\n検出手法: {method}\nモザイク比率: {self.ratio_var.get():.2f}"
        if not messagebox.askyesno("確認", message):
            return
            
        self.processing = True
        self.process_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        
        # 別スレッドで処理実行
        thread = threading.Thread(target=self.process_images)
        thread.daemon = True
        thread.start()
        
    def cancel_processing(self):
        """処理キャンセル"""
        self.processing = False
        self.status_var.set("キャンセル中...")
        
    def process_images(self):
        """画像処理メイン処理"""
        try:
            input_dir = self.input_var.get().strip()
            output_dir = self.output_var.get().strip()
            ratio = self.ratio_var.get()
            method = self.method_var.get()
            
            self.status_var.set("対象ファイルを検索中...")
            self.progress_var.set(0)
            
            # 対象ファイル取得
            image_files = self.processor.get_image_files(input_dir)
            
            if not image_files:
                self.log("処理対象の画像ファイルが見つかりません")
                self.log("対応形式: .jpg, .jpeg, .png, .bmp, .tiff, .tif")
                messagebox.showwarning("警告", "処理対象の画像ファイルが見つかりません")
                return
                
            total_files = len(image_files)
            self.log(f"処理対象ファイル数: {total_files}")
            self.log(f"使用する検出手法: {method}")
            
            success_count = 0
            error_count = 0
            face_detected_count = 0
            
            import time
            start_time = time.time()
            
            for i, image_path in enumerate(image_files):
                if not self.processing:
                    self.log("処理がキャンセルされました")
                    break
                    
                try:
                    # 相対パスを計算
                    rel_path = os.path.relpath(image_path, input_dir)
                    output_path = os.path.join(output_dir, rel_path)
                    
                    self.status_var.set(f"処理中: {rel_path}")
                    
                    # 画像処理
                    if self.processor.detector.process_image(image_path, output_path, ratio):
                        success_count += 1
                        
                        # 顔検出数をカウント（ログから推定）
                        # 実際の実装では、process_imageから顔数を返すように修正することを推奨
                        
                        self.log(f"処理完了: {rel_path}")
                    else:
                        error_count += 1
                        self.log(f"処理失敗: {rel_path}")
                    
                    # 進捗更新
                    progress = ((i + 1) / total_files) * 100
                    self.progress_var.set(progress)
                    
                except Exception as e:
                    error_count += 1
                    self.log(f"処理エラー ({rel_path}): {e}")
            
            # 結果表示
            if self.processing:
                elapsed_time = time.time() - start_time
                
                self.log(f"\n=== 処理結果 ===")
                self.log(f"成功: {success_count} ファイル")
                self.log(f"失敗: {error_count} ファイル")
                self.log(f"処理時間: {elapsed_time:.2f} 秒")
                
                if success_count > 0:
                    avg_time = elapsed_time / success_count
                    self.log(f"平均処理時間: {avg_time:.2f} 秒/ファイル")
                
                if error_count > 0:
                    messagebox.showwarning("完了", 
                                         f"処理が完了しました\n成功: {success_count}\n失敗: {error_count}")
                else:
                    messagebox.showinfo("完了", 
                                       f"全ての処理が正常に完了しました\n処理ファイル数: {success_count}")
                
                self.status_var.set("処理完了")
            else:
                self.status_var.set("処理キャンセル")
                
        except Exception as e:
            self.log(f"処理中にエラーが発生しました: {e}")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{e}")
            self.status_var.set("エラー")
            
        finally:
            self.processing = False
            self.process_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)


def main():
    # macOSでのtkinter問題対応
    if sys.platform == "darwin":
        try:
            # macOSでのフォーカス問題を回避
            os.system("osascript -e 'tell application \"System Events\" to set frontmost of every process whose unix id is {} to true'".format(os.getpid()))
        except:
            pass
    
    root = tk.Tk()
    
    # Windows/macOSでの見た目調整
    if sys.platform == "win32":
        try:
            root.wm_state('zoomed')  # Windows最大化
        except:
            pass
    elif sys.platform == "darwin":
        try:
            root.attributes('-zoomed', True)  # macOS最大化
        except:
            pass
    
    app = AdvancedFaceMosaicGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.quit()


if __name__ == "__main__":
    main()
