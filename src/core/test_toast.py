from win10toast import ToastNotifier

toaster = ToastNotifier()
toaster.show_toast("テスト通知", "これはテストです", duration=5, threaded=True)
