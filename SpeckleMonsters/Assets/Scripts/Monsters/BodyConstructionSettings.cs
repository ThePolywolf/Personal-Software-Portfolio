using UnityEngine;
using UnityEngine.Serialization;

[CreateAssetMenu(menuName = "Settings / Body Construction", fileName = "New Body Construction", order = 4)]
public class BodyConstructionSettings : ScriptableObject
{
    [Min(5)] public int ringVertexCount;
}
