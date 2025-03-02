using UnityEngine;

namespace Monsters
{
    public class HarmonicRotation : MonoBehaviour
    {
        public float Rotation;
        public float RotationTimeOffset;
        public Vector3 Motion;
        [Min(0)] public float Speed;

        private Vector3 _startPos;

        private void Start()
        {
            _startPos = transform.position;
        }

        private void FixedUpdate()
        {
            var currentRotation = transform.localRotation.eulerAngles;
            currentRotation.y = Mathf.Sin((Time.time + RotationTimeOffset) * Speed) * Rotation;
            transform.localRotation = Quaternion.Euler(currentRotation);
            
            var newPos = _startPos + Motion * Mathf.Sin(Time.time * Speed);
            var updatedPos = new Vector3(newPos.x, transform.position.y, newPos.z);
            transform.position = updatedPos;
        }
    }
}
