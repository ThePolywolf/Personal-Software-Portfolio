using UnityEngine;

namespace Monsters
{
    public class TargetMouseController : MonoBehaviour
    {
        [SerializeField] private float speed;
        [SerializeField] private float rotationSpeed;
        [SerializeField] [Range(-1,1)] private float directionMovement;
    
        private void FixedUpdate()
        {
            var input = new Vector3(Input.GetAxis("Horizontal"), 0, Input.GetAxis("Vertical"));

            if (Mathf.Abs(input.magnitude) <= 0.1f)
            {
                return;
            }
        
            var lookDirection = Quaternion.LookRotation(Quaternion.Euler(0, 45, 0) * input.normalized);
            transform.rotation = Quaternion.Slerp(transform.rotation, lookDirection, Time.fixedDeltaTime * rotationSpeed);
        
            var movement = transform.rotation * Vector3.forward * (speed * Time.fixedDeltaTime);
            movement.y = 0;

            // var inputFacingDot = Vector3.Dot(input.normalized, movement.normalized);
            // if (inputFacingDot < directionMovement)
            // {
            //     return;
            // }
            //
            // movement = movement.normalized * ((inputFacingDot - directionMovement) / (directionMovement + 1));
        
            transform.position += movement;
        }
    }
}
