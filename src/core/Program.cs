using System;
using System.Threading;
using MouthBreathMonitor.Core;

namespace MouthBreathMonitor.PoC
{
    class Program
    {
        static void Main(string[] args)
        {
            var camera = new CameraInput();
            var landmark = new LandmarkExtractor();
            var scorer = new MouthStateScorer();
            var movAvg = new MovingAverage(20); // 2秒分（例: 10fps）

            camera.OnFrameReceived += frame =>
            {
                var mouthLandmarks = landmark.Extract(frame);
                if (mouthLandmarks != null)
                {
                    var mar = landmark.CalculateMAR(mouthLandmarks.Value);
                    var avg = movAvg.Update(mar ?? 0);
                    var state = scorer.GetState(mar ?? 0, avg);
                    Console.WriteLine($"MAR: {mar:F3}, Avg: {avg:F3}, State: {state}");
                }
            };

            camera.StartCapture();
            Console.WriteLine("Press Enter to stop...");
            Console.ReadLine();
            camera.StopCapture();
        }
    }
}
