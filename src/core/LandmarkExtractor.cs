using System.Drawing;

namespace MouthBreathMonitor.Core
{
    public class LandmarkExtractor
    {
        public struct MouthLandmarks
        {
            public PointF UpperLip;
            public PointF LowerLip;
        }

        public MouthLandmarks? Extract(Bitmap frame)
        {
            // TODO: 実装 - MediapipeやDlib等で顔ランドマーク抽出
            // return new MouthLandmarks { UpperLip = ..., LowerLip = ... };
            return null;
        }

        public float? CalculateMAR(MouthLandmarks landmarks)
        {
            // MAR = (LowerLip.Y - UpperLip.Y) / 顔サイズ等
            if (landmarks == null) return null;
            return Math.Abs(landmarks.LowerLip.Y - landmarks.UpperLip.Y);
        }
    }
}
