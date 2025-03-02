using UnityEngine;
using UnityEngine.Serialization;

namespace Monsters
{
    [CreateAssetMenu(fileName = "New Node Trail Settings", menuName = "Settings / Node Trail", order = 1)]
    public class NodeTrailSettings : ScriptableObject
    {
        [FormerlySerializedAs("TargetDistance")]
        [Header("Joint Position")]
        [Tooltip("Ideal joint distance")]
        [Min(0)] public float targetDistance;
        
        [FormerlySerializedAs("PositionSmoothing")]
        [Tooltip("Distance smoothing")]
        [Range(0,1)] public float positionSmoothing;
        
        [FormerlySerializedAs("MaxDistance")]
        [Tooltip("Maximum joint distance")]
        [Min(0)] public float maxDistance;
        
        [FormerlySerializedAs("MinDistance")]
        [Tooltip("Minimum joint distance")]
        [Min(0)] public float minDistance;

        [Tooltip("Allows joints to hover above the ground")]
        public float jointHover;
        
        [FormerlySerializedAs("MinJointAngleDifference")]
        [Header("Joint Rotation")]
        [Tooltip("Minimum allowed dot-product similarity between joints. Snaps when exceeded")]
        [Range(-1,1)] public float minJointAngleDifference;
        
        [FormerlySerializedAs("ElasticRange")]
        [Tooltip("Proportion of range [1, MinAngle] where offset join angles are allowed")]
        [Range(0, 1)] public float elasticRange;
        
        [FormerlySerializedAs("RotationSmoothing")]
        [Tooltip("Stiffness of spring matching joint angles")]
        [Range(0, 1)] public float rotationSmoothing;
        
        public float SpringSimilarityAngle => minJointAngleDifference + (1 - minJointAngleDifference) * elasticRange;
        
        [Header("Mesh Settings")]
        [Tooltip("Sets the scale across the size curve")]
        [SerializeField] private float scaleSize;
 
        [Tooltip("Defines the scale of the trail mesh across its length (head -> tail)")]
        [SerializeField] private AnimationCurve scaleCurve;
        
        [Tooltip("Defines the offset position of the mesh for proper alignment")]
        public Vector3 offset;
        
        public float CurveEvaluation(float from, float max) => scaleCurve.Evaluate(from / max) * scaleSize;
    }
}