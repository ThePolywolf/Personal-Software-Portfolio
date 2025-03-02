using UnityEngine;

public class RotationTowards : MonoBehaviour
{
    [SerializeField] private Transform target;
    [SerializeField] private Vector3 extraRotation;

    void Update()
    {
        transform.position = target.position;
        transform.rotation = target.rotation;
        transform.rotation *= Quaternion.Euler(extraRotation);
        
    }
}
