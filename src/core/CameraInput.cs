using System;
using System.Drawing;
using System.Threading.Tasks;

namespace MouthBreathMonitor.Core
{
    public class CameraInput
    {
        public event Action<Bitmap> OnFrameReceived;

        public void StartCapture(int deviceIndex = 0)
        {
            // TODO: 実装 - OpenCVSharp等でWebカメラからフレーム取得
            // OnFrameReceived?.Invoke(frame);
        }

        public void StopCapture()
        {
            // TODO: 実装 - カメラストリーム停止
        }
    }
}
