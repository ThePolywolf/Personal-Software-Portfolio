using System;
using UnityEngine;

namespace Monsters
{
    [RequireComponent(typeof(NodeTrailMotionController), typeof(NodeTrailMeshBuilder))]
    public class NodeTrailManager : MonoBehaviour
    {
        // [Min(2)] [SerializeField] private int nodeCount; 
        [SerializeField] private Transform[] nodes;
        [SerializeField] private Transform head;

        [SerializeField] private NodeTrailSettings settings;

        private NodeTrailMotionController _motionController;
        private NodeTrailMeshBuilder _meshBuilder;

        private void Awake()
        {
            _motionController = GetComponent<NodeTrailMotionController>();
            _meshBuilder = GetComponent<NodeTrailMeshBuilder>();
            _meshBuilder = GetComponent<NodeTrailMeshBuilder>();
        }

        private void Start()
        {
            _motionController.InitializeFromManager(head, nodes, settings);
            _meshBuilder.InitializeFromManager(head, nodes, settings);
        }
    }
}
