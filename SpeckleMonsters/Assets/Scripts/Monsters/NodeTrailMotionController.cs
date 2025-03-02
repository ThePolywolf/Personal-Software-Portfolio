using UnityEngine;
using UnityEngine.Serialization;

namespace Monsters
{
    public class NodeTrailMotionController : MonoBehaviour
    {
        [SerializeField] private NodeTrailSettings settings;
        [SerializeField] private Transform target;
        [SerializeField] private Transform[] nodes;

        private const int GroundCheckAboveStart = 20;
        private const float MaxFallSpeed = 0.2f;
        
        public void InitializeFromManager(Transform head, Transform[] nodesIn, NodeTrailSettings settingsIn)
        {
            target = head;
            nodes = nodesIn;
            settings = settingsIn;
        }
        
        private void FixedUpdate()
        {
            NodesFollowLead();

            SnapNodesToGround();

            RotateNodes();
        }

        private void NodesFollowLead()
        {
            var followTarget = target;
            var lastJointDirection = target.rotation * Vector3.forward;
            foreach (var node in nodes)
            {
                // get direction
                var direction = followTarget.position - node.transform.position;
                
                // get Dot angle
                var normalDirection = direction.normalized;
                normalDirection = SmoothedAngle(lastJointDirection, normalDirection);
                
                // smooth motion within clamp range
                var distance = direction.magnitude;
                var smoothedDistance = Mathf.Lerp(distance, settings.targetDistance, settings.positionSmoothing);
                var clampedDistance = Mathf.Clamp(smoothedDistance, settings.minDistance, settings.maxDistance);
                
                // apply motion
                node.transform.position = followTarget.position - normalDirection * clampedDistance;
                
                followTarget = node.transform;
                lastJointDirection = normalDirection;
            }
        }

        private void SnapNodesToGround()
        {
            // normally evaluate curve from nodes.length - 1, however the head will be treated as the first node
            SnapNodeToGround(target, settings.CurveEvaluation(0, nodes.Length));
            
            var nodeIndex = 0;
            foreach (var node in nodes)
            {
                var nodeRadius = settings.CurveEvaluation(nodeIndex + 1, nodes.Length);

                SnapNodeToGround(node, nodeRadius);
                
                nodeIndex++;
            }
        }

        private void SnapNodeToGround(Transform node, float nodeRadius)
        {
            var ray = new Ray(node.position + Vector3.up * GroundCheckAboveStart, Vector3.down);
            Physics.Raycast(ray, out var hit, 50);

            if (hit.collider is null)
            {
                // transform.position += Vector3.down * settings.MaxSpeed;
                return;
            }
            
            var distanceFromBottomToGround = hit.distance - GroundCheckAboveStart - settings.jointHover - nodeRadius;
            var movement = Mathf.Lerp(0, distanceFromBottomToGround, 0.2f);
            movement = Mathf.Clamp(movement, -MaxFallSpeed, MaxFallSpeed);
                
            // if (distanceFromBottomToGround < 0)
            // {
            //     movement = Mathf.Min(distanceFromBottomToGround, movement);
            // }
                
            node.position -= Vector3.up * movement;
        }

        private void RotateNodes()
        {
            var lastNode = target;
            foreach (var node in nodes)
            {
                node.transform.LookAt(lastNode);
                lastNode = node.transform;
            }
        }

        private Vector3 SmoothedAngle(Vector3 lastJointDirection, Vector3 currentJointDirection)
        {
            var dot = Vector3.Dot(lastJointDirection, currentJointDirection);

            // Keep angle if within allowed angle
            var springDot = settings.SpringSimilarityAngle;
            if (dot >= springDot) 
                return currentJointDirection;
            
            var followAngle = ClosestDotAngle(lastJointDirection, currentJointDirection, springDot);
            var smoothDirection =  Vector3.Lerp(currentJointDirection, followAngle, settings.rotationSmoothing).normalized;
            
            // Clamp within min dot
            var minDot = settings.minJointAngleDifference;
            var smoothDot = Vector3.Dot(lastJointDirection, smoothDirection);
            if (smoothDot >= minDot)
                return smoothDirection;
            
            return ClosestDotAngle(lastJointDirection, currentJointDirection, minDot);
        }

        private Vector3 ClosestDotAngle(Vector3 compare, Vector3 current, float minDot)
        {
            var axis = Vector3.Cross(compare, current);

            // co-linear
            if (axis == Vector3.zero)
                return compare;
                
            var minAngle = Mathf.Acos(minDot) * Mathf.Rad2Deg;
            var minimumRotation = Quaternion.AngleAxis(minAngle, axis.normalized);
                
            return minimumRotation * compare;
        }
    }
}