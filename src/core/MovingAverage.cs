using System.Collections.Generic;

namespace MouthBreathMonitor.Core
{
    public class MovingAverage
    {
        private readonly Queue<float> _window = new();
        private readonly int _size;
        private float _sum = 0;

        public MovingAverage(int windowSize)
        {
            _size = windowSize;
        }

        public float Update(float value)
        {
            _window.Enqueue(value);
            _sum += value;
            if (_window.Count > _size)
            {
                _sum -= _window.Dequeue();
            }
            return _sum / _window.Count;
        }
    }
}
