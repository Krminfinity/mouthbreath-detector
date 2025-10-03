namespace MouthBreathMonitor.Core
{
    public class MouthStateScorer
    {
        // MARしきい値（仮）
        public float ThresholdHigh { get; set; } = 0.62f;
        public float ThresholdLow { get; set; } = 0.45f;
        public int WindowSec { get; set; } = 2;

        public enum MouthState { Nasal, Mouth, Unknown }

        public MouthState GetState(float mar, float movingAvg)
        {
            if (movingAvg >= ThresholdHigh) return MouthState.Mouth;
            if (movingAvg <= ThresholdLow) return MouthState.Nasal;
            return MouthState.Unknown;
        }
    }
}
