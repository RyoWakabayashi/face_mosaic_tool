"""
GUI版メインモジュール
グラフィカル ユーザー インターフェース
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
from typing import Optional

from ..core.application import FaceMosaicApplication
from ..config.settings import AppConfig
from ..core.exceptions import FaceMosaicError


class GUIApplication:
    """GUI版アプリケーション"""

    def __init__(self, root: tk.Tk):
        """
        初期化

        Args:
            root: Tkinterルートウィンドウ
        """
        self.root = root
        self.app: Optional[FaceMosaicApplication] = None
        self.processing = False

        self.setup_window()
        self.create_widgets()
        self.initialize_application()

    def setup_window(self) -> None:
        """ウィンドウ設定"""
        self.root.title("Face Mosaic Tool v2.0 - YuNet専用高精度顔モザイク処理")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # アイコン設定（オプション）
        try:
            # self.root.iconbitmap("icon.ico")  # アイコンファイルがある場合
            pass
        except:
            pass

    def create_widgets(self) -> None:
        """ウィジェット作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # グリッド設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # ファイル選択セクション
        self.create_file_selection_section(main_frame, 0)

        # 設定セクション
        self.create_settings_section(main_frame, 1)

        # 実行ボタンセクション
        self.create_execution_section(main_frame, 2)

        # 進捗セクション
        self.create_progress_section(main_frame, 3)

        # ログセクション
        self.create_log_section(main_frame, 4)

        # ステータスバー
        self.create_status_bar()

    def create_file_selection_section(self, parent: ttk.Frame, row: int) -> None:
        """ファイル選択セクション作成"""
        # セクションフレーム
        section_frame = ttk.LabelFrame(parent, text="ファイル選択", padding="5")
        section_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        section_frame.columnconfigure(1, weight=1)

        # 入力ディレクトリ
        ttk.Label(section_frame, text="入力:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )
        self.input_var = tk.StringVar()
        ttk.Entry(section_frame, textvariable=self.input_var, state="readonly").grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5)
        )
        ttk.Button(
            section_frame, text="参照", command=self.select_input_directory
        ).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(section_frame, text="ファイル", command=self.select_input_file).grid(
            row=0, column=3
        )

        # 出力ディレクトリ
        ttk.Label(section_frame, text="出力:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0)
        )
        self.output_var = tk.StringVar()
        ttk.Entry(section_frame, textvariable=self.output_var, state="readonly").grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0)
        )
        ttk.Button(
            section_frame, text="参照", command=self.select_output_directory
        ).grid(row=1, column=2, columnspan=2, pady=(5, 0))

    def create_settings_section(self, parent: ttk.Frame, row: int) -> None:
        """設定セクション作成"""
        # セクションフレーム
        section_frame = ttk.LabelFrame(parent, text="処理設定", padding="5")
        section_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        section_frame.columnconfigure(1, weight=1)

        # モザイク比率
        ttk.Label(section_frame, text="モザイク比率:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )
        self.ratio_var = tk.DoubleVar(value=0.1)
        ratio_frame = ttk.Frame(section_frame)
        ratio_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ratio_frame.columnconfigure(0, weight=1)

        self.ratio_scale = ttk.Scale(
            ratio_frame,
            from_=0.01,
            to=1.0,
            variable=self.ratio_var,
            orient=tk.HORIZONTAL,
            command=self.on_ratio_change,
        )
        self.ratio_scale.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        self.ratio_label = ttk.Label(ratio_frame, text="0.10")
        self.ratio_label.grid(row=0, column=1)

        # 信頼度閾値
        ttk.Label(section_frame, text="信頼度閾値:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0)
        )
        self.confidence_var = tk.DoubleVar(value=0.6)
        confidence_frame = ttk.Frame(section_frame)
        confidence_frame.grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0)
        )
        confidence_frame.columnconfigure(0, weight=1)

        self.confidence_scale = ttk.Scale(
            confidence_frame,
            from_=0.1,
            to=1.0,
            variable=self.confidence_var,
            orient=tk.HORIZONTAL,
            command=self.on_confidence_change,
        )
        self.confidence_scale.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        self.confidence_label = ttk.Label(confidence_frame, text="0.60")
        self.confidence_label.grid(row=0, column=1)

        # モザイク方式
        ttk.Label(section_frame, text="モザイク方式:").grid(
            row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0)
        )
        self.mosaic_type_var = tk.StringVar(value="pixelate")
        mosaic_frame = ttk.Frame(section_frame)
        mosaic_frame.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))

        ttk.Radiobutton(
            mosaic_frame,
            text="ピクセル化",
            variable=self.mosaic_type_var,
            value="pixelate",
        ).grid(row=0, column=0, padx=(0, 10))
        ttk.Radiobutton(
            mosaic_frame, text="ブラー", variable=self.mosaic_type_var, value="blur"
        ).grid(row=0, column=1)

        # 物体検出オプション
        self.use_object_detection_var = tk.BooleanVar(value=False)
        self.object_labels_var = tk.StringVar(value="person,car")
        ttk.Checkbutton(
            section_frame,
            text="物体検出 (PyTorch FasterRCNN)",
            variable=self.use_object_detection_var,
            command=self.update_settings,
        ).grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        ttk.Label(section_frame, text="物体ラベル(カンマ区切り):").grid(
            row=3, column=1, sticky=tk.W, padx=(0, 5), pady=(5, 0)
        )
        ttk.Entry(section_frame, textvariable=self.object_labels_var, width=30).grid(
            row=3, column=2, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0)
        )

    def create_execution_section(self, parent: ttk.Frame, row: int) -> None:
        """実行ボタンセクション作成"""
        # セクションフレーム
        section_frame = ttk.Frame(parent)
        section_frame.grid(row=row, column=0, columnspan=2, pady=10)

        # ボタン
        self.process_button = ttk.Button(
            section_frame,
            text="処理開始",
            command=self.start_processing,
            style="Accent.TButton",
        )
        self.process_button.grid(row=0, column=0, padx=(0, 10))

        self.preview_button = ttk.Button(
            section_frame, text="プレビュー", command=self.preview_processing
        )
        self.preview_button.grid(row=0, column=1, padx=(0, 10))

        self.estimate_button = ttk.Button(
            section_frame, text="時間推定", command=self.estimate_processing_time
        )
        self.estimate_button.grid(row=0, column=2, padx=(0, 10))

        self.stop_button = ttk.Button(
            section_frame, text="停止", command=self.stop_processing, state="disabled"
        )
        self.stop_button.grid(row=0, column=3)

    def create_progress_section(self, parent: ttk.Frame, row: int) -> None:
        """進捗セクション作成"""
        # セクションフレーム
        section_frame = ttk.LabelFrame(parent, text="進捗", padding="5")
        section_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        section_frame.columnconfigure(0, weight=1)

        # 進捗バー
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            section_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # 進捗ラベル
        self.progress_label = ttk.Label(section_frame, text="待機中...")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)

    def create_log_section(self, parent: ttk.Frame, row: int) -> None:
        """ログセクション作成"""
        # セクションフレーム
        section_frame = ttk.LabelFrame(parent, text="ログ", padding="5")
        section_frame.grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5
        )
        section_frame.columnconfigure(0, weight=1)
        section_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(row, weight=1)

        # ログテキスト
        self.log_text = scrolledtext.ScrolledText(
            section_frame, height=10, state="disabled", wrap=tk.WORD
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # ログクリアボタン
        ttk.Button(section_frame, text="ログクリア", command=self.clear_log).grid(
            row=1, column=0, sticky=tk.E, pady=(5, 0)
        )

    def create_status_bar(self) -> None:
        """ステータスバー作成"""
        self.status_var = tk.StringVar(value="準備完了")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN
        )
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def initialize_application(self) -> None:
        """アプリケーション初期化"""
        try:
            config = AppConfig()
            self.app = FaceMosaicApplication(config)

            if self.app.is_ready():
                self.log("アプリケーションが正常に初期化されました")
                self.status_var.set("準備完了")
            else:
                self.log("警告: システム要件を満たしていない可能性があります")
                self.status_var.set("警告: 要件未満")

        except Exception as e:
            self.log(f"エラー: アプリケーションの初期化に失敗しました: {e}")
            self.status_var.set("初期化失敗")

    def log(self, message: str) -> None:
        """ログメッセージを追加"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update_idletasks()

    def clear_log(self) -> None:
        """ログをクリア"""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

    def on_ratio_change(self, value: str) -> None:
        """モザイク比率変更時のコールバック"""
        ratio = float(value)
        self.ratio_label.config(text=f"{ratio:.2f}")
        if self.app:
            try:
                self.app.update_mosaic_ratio(ratio)
            except ValueError as e:
                self.log(f"警告: {e}")

    def on_confidence_change(self, value: str) -> None:
        """信頼度閾値変更時のコールバック"""
        confidence = float(value)
        self.confidence_label.config(text=f"{confidence:.2f}")
        if self.app:
            try:
                self.app.update_confidence_threshold(confidence)
            except ValueError as e:
                self.log(f"警告: {e}")

    def select_input_directory(self) -> None:
        """入力ディレクトリ選択"""
        directory = filedialog.askdirectory(title="入力ディレクトリを選択")
        if directory:
            self.input_var.set(directory)
            self.log(f"入力ディレクトリを選択: {directory}")

    def select_input_file(self) -> None:
        """入力ファイル選択"""
        filetypes = [
            ("画像ファイル", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
            ("すべてのファイル", "*.*"),
        ]
        filename = filedialog.askopenfilename(
            title="入力ファイルを選択", filetypes=filetypes
        )
        if filename:
            self.input_var.set(filename)
            self.log(f"入力ファイルを選択: {filename}")

    def select_output_directory(self) -> None:
        """出力ディレクトリ選択"""
        directory = filedialog.askdirectory(title="出力ディレクトリを選択")
        if directory:
            self.output_var.set(directory)
            self.log(f"出力ディレクトリを選択: {directory}")

    def validate_inputs(self) -> bool:
        """入力値を検証"""
        if not self.input_var.get():
            messagebox.showerror("エラー", "入力パスを選択してください")
            return False

        if not self.output_var.get():
            messagebox.showerror("エラー", "出力パスを選択してください")
            return False

        input_path = Path(self.input_var.get())
        if not input_path.exists():
            messagebox.showerror("エラー", f"入力パスが見つかりません: {input_path}")
            return False

        return True

    def update_settings(self) -> None:
        """設定を更新"""
        if not self.app:
            return
        try:
            # モザイク設定更新
            self.app.config.mosaic.pixelate = self.mosaic_type_var.get() == "pixelate"
            # 物体検出設定更新
            use_obj = self.use_object_detection_var.get()
            labels = [
                s.strip() for s in self.object_labels_var.get().split(",") if s.strip()
            ]
            if use_obj:
                from ..core.object_detector import ObjectDetector

                if (
                    not hasattr(self.app.image_processor, "object_detector")
                    or self.app.image_processor.object_detector is None
                ):
                    self.app.image_processor.object_detector = ObjectDetector()
                self.app.image_processor.use_object_detection = True
                self.app.image_processor.object_labels = labels
            else:
                self.app.image_processor.use_object_detection = False
                self.app.image_processor.object_labels = []
        except Exception as e:
            self.log(f"設定更新エラー: {e}")

    def start_processing(self) -> None:
        """処理開始"""
        if not self.validate_inputs():
            return

        if self.processing:
            messagebox.showwarning("警告", "処理が既に実行中です")
            return

        # 確認ダイアログ
        if not messagebox.askyesno("確認", "処理を開始しますか？"):
            return

        # 設定更新
        self.update_settings()

        # UI状態更新
        self.processing = True
        self.process_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_var.set(0)
        self.progress_label.config(text="処理中...")
        self.status_var.set("処理中")

        # バックグラウンドで処理実行
        thread = threading.Thread(target=self._process_files, daemon=True)
        thread.start()

    def _process_files(self) -> None:
        """ファイル処理（バックグラウンド）"""
        try:
            input_path = Path(self.input_var.get())
            output_path = Path(self.output_var.get())

            def progress_callback(current: int, total: int):
                progress = (current / total) * 100
                self.root.after(0, lambda: self.progress_var.set(progress))
                self.root.after(
                    0,
                    lambda: self.progress_label.config(
                        text=f"処理中... {current}/{total}"
                    ),
                )

            if input_path.is_file():
                # 単一ファイル処理
                self.root.after(0, lambda: self.log("単一ファイル処理を開始"))
                result = self.app.process_single_image(input_path, output_path)
                self.root.after(0, lambda: self._show_single_result(result))
            else:
                # ディレクトリ処理
                self.root.after(0, lambda: self.log("ディレクトリ処理を開始"))
                stats = self.app.process_directory(
                    input_path, output_path, progress_callback
                )
                self.root.after(0, lambda: self._show_batch_results(stats))

        except FaceMosaicError as e:
            self.root.after(0, lambda: self.log(f"処理エラー: {e}"))
            self.root.after(0, lambda: messagebox.showerror("処理エラー", str(e)))
        except Exception as e:
            self.root.after(0, lambda: self.log(f"予期しないエラー: {e}"))
            self.root.after(
                0, lambda: messagebox.showerror("エラー", f"予期しないエラー: {e}")
            )
        finally:
            self.root.after(0, self._processing_finished)

    def _show_single_result(self, result: dict) -> None:
        """単一ファイル処理結果を表示"""
        if result["success"]:
            self.log(f"✓ 処理成功: {result['faces_detected']} 個の顔を検出")
            self.log(f"出力ファイル: {result['output_path']}")
            messagebox.showinfo("完了", "処理が正常に完了しました")
        else:
            self.log(f"✗ 処理失敗: {result['error']}")
            messagebox.showerror("エラー", f"処理に失敗しました: {result['error']}")

    def _show_batch_results(self, stats: dict) -> None:
        """バッチ処理結果を表示"""
        self.log(f"=== 処理結果 ===")
        self.log(f"対象ファイル数: {stats['total']}")
        self.log(f"成功: {stats['success']} ファイル")
        self.log(f"失敗: {stats['failed']} ファイル")
        self.log(f"検出された顔: {stats['faces_detected']} 個")
        self.log(f"処理時間: {stats['processing_time']:.2f} 秒")

        if stats["failed"] > 0:
            messagebox.showwarning(
                "完了（一部失敗）",
                f"処理が完了しましたが、{stats['failed']} 個のファイルで失敗しました",
            )
        else:
            messagebox.showinfo("完了", "全ての処理が正常に完了しました")

    def _processing_finished(self) -> None:
        """処理完了時の処理"""
        self.processing = False
        self.process_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_var.set(100)
        self.progress_label.config(text="完了")
        self.status_var.set("準備完了")

    def stop_processing(self) -> None:
        """処理停止"""
        # 注意: 実際の停止機能は複雑なため、ここでは基本的な実装のみ
        if messagebox.askyesno("確認", "処理を停止しますか？"):
            self.log("処理停止が要求されました")
            # 実際の停止処理はより複雑な実装が必要

    def preview_processing(self) -> None:
        """処理プレビュー"""
        if not self.validate_inputs():
            return

        input_path = Path(self.input_var.get())
        if input_path.is_dir():
            files = self.app.get_file_list(input_path)
            file_list = "\n".join([f"  {f.name}" for f in files[:10]])
            if len(files) > 10:
                file_list += f"\n  ... 他 {len(files) - 10} ファイル"

            messagebox.showinfo(
                "プレビュー",
                f"処理対象ファイル数: {len(files)}\n\n最初の10ファイル:\n{file_list}",
            )
        else:
            messagebox.showinfo("プレビュー", f"処理対象ファイル: {input_path.name}")

    def estimate_processing_time(self) -> None:
        """処理時間推定"""
        if not self.validate_inputs():
            return

        input_path = Path(self.input_var.get())
        if not input_path.is_dir():
            messagebox.showinfo(
                "情報", "処理時間推定はディレクトリに対してのみ実行できます"
            )
            return

        self.log("処理時間を推定中...")
        self.status_var.set("推定中...")

        def estimate_thread():
            try:
                estimation = self.app.estimate_processing_time(input_path)

                def show_result():
                    self.log(
                        f"推定結果: {estimation['total_files']} ファイル, "
                        f"{estimation['estimated_time']:.1f} 秒"
                    )

                    time_text = f"{estimation['estimated_time']:.1f} 秒"
                    if estimation["estimated_time"] > 60:
                        minutes = estimation["estimated_time"] / 60
                        time_text += f" ({minutes:.1f} 分)"

                    messagebox.showinfo(
                        "処理時間推定",
                        f"対象ファイル数: {estimation['total_files']}\n"
                        f"推定処理時間: {time_text}",
                    )
                    self.status_var.set("準備完了")

                self.root.after(0, show_result)

            except Exception as e:
                self.root.after(0, lambda: self.log(f"推定エラー: {e}"))
                self.root.after(0, lambda: self.status_var.set("準備完了"))

        thread = threading.Thread(target=estimate_thread, daemon=True)
        thread.start()


def main():
    """GUI版メイン関数"""
    root = tk.Tk()
    app = GUIApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()
